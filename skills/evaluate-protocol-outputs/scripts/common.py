"""Shared I/O helpers for the standalone BioProBench metrics skill."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


SKILL_NAME = "evaluate-protocol-outputs"
SKILL_VERSION = "2.0.0"


class InputError(ValueError):
    """Raised when an input file does not satisfy the evaluation contract."""


def load_records(path: str) -> list[dict[str, Any]]:
    input_path = Path(path).expanduser()
    try:
        with input_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError as exc:
        raise InputError(f"Input file does not exist: {input_path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"Input is not valid JSON: {exc}") from exc

    if not isinstance(payload, list):
        raise InputError("Top-level JSON value must be an array of objects")
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise InputError(f"Item {index} must be a JSON object")
    return payload


def sample_id(item: dict[str, Any], index: int) -> str:
    value = item.get("id")
    return str(value) if value is not None else f"index:{index}"


def failure(item: dict[str, Any], index: int, exc: Exception) -> dict[str, str]:
    return {
        "id": sample_id(item, index),
        "error": str(exc) or exc.__class__.__name__,
    }


def require(item: dict[str, Any], field: str) -> Any:
    if field not in item:
        raise ValueError(f"Missing required field: {field}")
    return item[field]


def finite_or_none(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: finite_or_none(item) for key, item in value.items()}
    if isinstance(value, list):
        return [finite_or_none(item) for item in value]
    return value


def result_envelope(
    task: str,
    total: int,
    scored: int,
    metrics: dict[str, Any],
    errors: list[dict[str, str]],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return finite_or_none(
        {
            "skill": SKILL_NAME,
            "version": SKILL_VERSION,
            "task": task,
            "samples": {
                "total": total,
                "scored": scored,
                "failed": len(errors),
                "failure_rate": len(errors) / total if total else 0.0,
            },
            "metrics": metrics,
            "config": config or {},
        }
    )


def merge_failures(
    result: dict[str, Any],
    errors: list[dict[str, str]],
    total: int,
) -> dict[str, Any]:
    result["samples"]["total"] = total
    result["samples"]["failed"] = len(errors)
    result["samples"]["failure_rate"] = len(errors) / total if total else 0.0
    return result


def write_json(path: str, payload: Any, *, jsonl: bool = False) -> None:
    output_path = Path(path).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        if jsonl:
            for item in payload:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        else:
            json.dump(payload, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
