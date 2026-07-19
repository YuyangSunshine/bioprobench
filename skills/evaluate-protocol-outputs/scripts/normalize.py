"""Normalize generic and BioProBench-shaped records before metric computation."""

from __future__ import annotations

import ast
import re
from typing import Any

from common import failure, sample_id


TASK_ALIASES = {
    "question-answering": "question-answering",
    "qa": "question-answering",
    "PQA": "question-answering",
    "protocol-error-detection": "protocol-error-detection",
    "error-detection": "protocol-error-detection",
    "ERR": "protocol-error-detection",
    "step-ordering": "step-ordering",
    "ordering": "step-ordering",
    "ORD": "step-ordering",
    "protocol-generation": "protocol-generation",
    "generation": "protocol-generation",
    "GEN": "protocol-generation",
    "judge-consistency": "judge-consistency",
    "REA-ERR": "judge-consistency",
}

ANSWER_PATTERN = re.compile(r"\[ANSWER_START\](.*?)\[ANSWER_END\]", re.DOTALL)
BOOL_PATTERN = re.compile(r"\b(true|false)\b", re.IGNORECASE)


def canonical_task(task: str) -> str:
    try:
        return TASK_ALIASES[task]
    except KeyError as exc:
        raise ValueError(f"Unsupported task: {task}") from exc


def get_field(item: dict[str, Any], path: str) -> Any:
    value: Any = item
    for component in path.split("."):
        if not isinstance(value, dict) or component not in value:
            raise ValueError(f"Missing field: {path}")
        value = value[component]
    return value


def strip_model_wrappers(value: str) -> str:
    if "</think>" in value:
        value = value.split("</think>")[-1]
    if "[/INST]" in value:
        value = value.split("[/INST]")[-1]
    return value.strip()


def answer_content(value: Any, *, allow_last_line: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError("Prediction must be a string for answer parsing")
    value = strip_model_wrappers(value)
    matches = ANSWER_PATTERN.findall(value)
    if matches:
        return matches[-1].strip()
    if allow_last_line and value:
        return value.splitlines()[-1].strip()
    raise ValueError("Missing [ANSWER_START] or [ANSWER_END]")


def parse_boolean(value: Any, parser: str) -> bool:
    if type(value) is bool:
        return value
    if parser == "structured":
        raise ValueError("Structured boolean prediction must be true or false")
    text = answer_content(value, allow_last_line=parser in {"auto", "last-line"})
    matches = {match.lower() for match in BOOL_PATTERN.findall(text)}
    if matches == {"true"}:
        return True
    if matches == {"false"}:
        return False
    raise ValueError("Expected an unambiguous True or False prediction")


def parse_qa(value: Any, confidence: Any, parser: str) -> tuple[str, float | None]:
    should_parse_text = parser in {"answer-tags", "last-line"} or (
        parser == "auto" and isinstance(value, str) and bool(ANSWER_PATTERN.search(value))
    )
    if not should_parse_text:
        prediction = str(value)
    else:
        content = answer_content(value, allow_last_line=parser == "last-line")
        if confidence is not None:
            prediction = content
        elif "&" in content:
            parts = content.split("&")
            if len(parts) != 2:
                raise ValueError("Expected one '&' between answer and confidence")
            prediction, confidence = parts
        else:
            parts = content.rsplit(maxsplit=1)
            if len(parts) != 2:
                raise ValueError("Answer and confidence could not be separated")
            prediction, confidence = parts
    if confidence is None:
        return prediction.strip(), None
    try:
        confidence_value = float(str(confidence).strip().rstrip("%"))
    except (TypeError, ValueError) as exc:
        raise ValueError("Confidence must be numeric") from exc
    if confidence_value > 1:
        confidence_value /= 100
    if not 0 <= confidence_value <= 1:
        raise ValueError("Confidence must be in 0..1 or 0..100")
    return prediction.strip(), confidence_value


def parse_order(value: Any, items: Any, parser: str) -> list[Any]:
    if isinstance(value, list):
        order = value
    elif parser != "structured":
        content = answer_content(value, allow_last_line=parser == "last-line")
        try:
            order = ast.literal_eval(content)
        except (SyntaxError, ValueError) as exc:
            raise ValueError("Could not parse ordering prediction as a list") from exc
        if not isinstance(order, list):
            raise ValueError("Ordering prediction must be a list")
    else:
        raise ValueError("Structured ordering prediction must be a list")

    if items is not None and all(type(index) is int for index in order):
        if not isinstance(items, list):
            raise ValueError("items must be a list when prediction contains indices")
        if len(order) != len(items) or set(order) != set(range(len(items))):
            raise ValueError("Ordering indices must be a complete zero-based permutation")
        return [items[index] for index in order]
    return order


def parse_generation(value: Any, parser: str) -> str | list[str]:
    if isinstance(value, list):
        if not all(isinstance(entry, str) for entry in value):
            raise ValueError("Generation prediction list must contain strings")
        return value
    if not isinstance(value, str):
        raise ValueError("Generation prediction must be a string or list of strings")
    if parser == "structured":
        return value
    value = strip_model_wrappers(value).split("</Structure>")[-1].strip()
    matches = ANSWER_PATTERN.findall(value)
    if matches:
        return matches[-1].strip()
    return value.splitlines()[-1].strip() if parser == "last-line" and value else value


def infer_task(records: list[dict[str, Any]], profile: str, fields: dict[str, str]) -> str:
    if not records:
        raise ValueError("Cannot infer a task from empty input")
    item = records[0]
    if profile == "bioprobench":
        keys = set(item)
        candidates = []
        if {"answer", "generated_response"} <= keys:
            candidates.append("question-answering")
        if {"is_correct", "generated_response"} <= keys:
            candidates.append("protocol-error-detection")
        if {"wrong_steps", "correct_steps", "generated_response"} <= keys:
            candidates.append("step-ordering")
        if {"output", "generated_response"} <= keys:
            candidates.append("protocol-generation")
        if "LLM_judge" in keys:
            candidates.append("judge-consistency")
    else:
        prediction = get_field(item, fields["prediction"])
        try:
            reference = get_field(item, fields["reference"])
        except ValueError:
            reference = None
        candidates = []
        try:
            get_field(item, fields["confidence"])
            candidates.append("question-answering")
        except ValueError:
            pass
        if type(reference) is bool:
            candidates.append("protocol-error-detection")
        if isinstance(prediction, list) and isinstance(reference, list):
            candidates.append("step-ordering")
    if len(candidates) != 1:
        names = ", ".join(candidates) if candidates else "none"
        raise ValueError(f"Task inference is ambiguous; candidates: {names}. Pass --task explicitly.")
    return candidates[0]


def normalize_record(
    item: dict[str, Any],
    task: str,
    profile: str,
    parser: str,
    fields: dict[str, str],
) -> dict[str, Any]:
    try:
        identifier = get_field(item, fields["id"])
    except ValueError:
        identifier = item.get("id")
    normalized: dict[str, Any] = {"id": identifier}

    if profile == "bioprobench":
        if task == "question-answering":
            prediction, confidence = parse_qa(item.get("generated_response"), None, "answer-tags")
            normalized.update(prediction=prediction, reference=str(get_field(item, "answer")), confidence=confidence)
        elif task == "protocol-error-detection":
            is_correct = get_field(item, "is_correct")
            if type(is_correct) is not bool:
                raise ValueError("is_correct must be true or false")
            normalized.update(
                prediction=not parse_boolean(item.get("generated_response"), "auto"),
                reference=not is_correct,
            )
        elif task == "step-ordering":
            wrong_steps = get_field(item, "wrong_steps")
            normalized.update(
                prediction=parse_order(item.get("generated_response"), wrong_steps, "answer-tags"),
                reference=get_field(item, "correct_steps"),
            )
        elif task == "protocol-generation":
            normalized.update(
                prediction=parse_generation(item.get("generated_response"), "auto"),
                reference=get_field(item, "output"),
            )
        else:
            normalized["prediction"] = parse_boolean(item.get("LLM_judge"), "auto")
        return normalized

    prediction = get_field(item, fields["prediction"])
    if task == "question-answering":
        try:
            confidence = get_field(item, fields["confidence"])
        except ValueError:
            confidence = None
        prediction, confidence = parse_qa(prediction, confidence, parser)
        normalized.update(
            prediction=prediction,
            reference=str(get_field(item, fields["reference"])),
            confidence=confidence,
        )
    elif task == "protocol-error-detection":
        reference = get_field(item, fields["reference"])
        if type(reference) is not bool:
            raise ValueError("Error-detection reference must be true or false")
        normalized.update(prediction=parse_boolean(prediction, parser), reference=reference)
    elif task == "step-ordering":
        try:
            items = get_field(item, fields["items"])
        except ValueError:
            items = None
        reference = get_field(item, fields["reference"])
        if not isinstance(reference, list):
            raise ValueError("Ordering reference must be a list")
        normalized.update(
            prediction=parse_order(prediction, items, parser),
            reference=parse_order(reference, items, "structured"),
        )
    elif task == "protocol-generation":
        reference = get_field(item, fields["reference"])
        if not isinstance(reference, (str, list)):
            raise ValueError("Generation reference must be a string or list of strings")
        normalized.update(prediction=parse_generation(prediction, parser), reference=reference)
    else:
        normalized["prediction"] = parse_boolean(prediction, parser)
    return normalized


def normalize_records(
    records: list[dict[str, Any]],
    task: str,
    profile: str,
    parser: str,
    fields: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    normalized = []
    errors = []
    for index, item in enumerate(records):
        try:
            record = normalize_record(item, task, profile, parser, fields)
            if record.get("id") is None:
                record["id"] = sample_id(item, index)
            normalized.append(record)
        except Exception as exc:
            errors.append(failure(item, index, exc))
    return normalized, errors
