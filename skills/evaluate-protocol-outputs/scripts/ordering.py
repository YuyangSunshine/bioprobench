"""Sequence ordering metrics."""

from __future__ import annotations

from itertools import combinations
from typing import Any

from common import failure, require, result_envelope


def validate_pair(prediction: Any, reference: Any) -> tuple[list[Any], list[Any]]:
    if not isinstance(prediction, list) or not isinstance(reference, list):
        raise ValueError("prediction and reference must be lists")
    if len(prediction) != len(reference):
        raise ValueError("prediction and reference must have equal length")
    try:
        prediction_set = set(prediction)
        reference_set = set(reference)
    except TypeError as exc:
        raise ValueError("ordering items must be hashable scalar values") from exc
    if len(prediction_set) != len(prediction) or len(reference_set) != len(reference):
        raise ValueError("ordering items must be unique")
    if prediction_set != reference_set:
        raise ValueError("prediction and reference must contain the same items")
    return prediction, reference


def kendall_tau(references: list[list[Any]], predictions: list[list[Any]]) -> float:
    total_pairs = 0
    concordant_pairs = 0
    for reference, prediction in zip(references, predictions):
        ref_rank = {item: index for index, item in enumerate(reference)}
        pred_rank = {item: index for index, item in enumerate(prediction)}
        for first, second in combinations(ref_rank, 2):
            if (ref_rank[first] - ref_rank[second]) * (pred_rank[first] - pred_rank[second]) > 0:
                concordant_pairs += 1
            total_pairs += 1
    return (2 * concordant_pairs - total_pairs) / total_pairs if total_pairs else 0.0


def evaluate(records: list[dict[str, Any]], **_: Any) -> tuple[dict[str, Any], list[dict[str, str]]]:
    predictions: list[list[Any]] = []
    references: list[list[Any]] = []
    errors: list[dict[str, str]] = []
    for index, item in enumerate(records):
        try:
            prediction, reference = validate_pair(
                require(item, "prediction"), require(item, "reference")
            )
            predictions.append(prediction)
            references.append(reference)
        except Exception as exc:
            errors.append(failure(item, index, exc))

    scored = len(predictions)
    exact_match = sum(pred == ref for pred, ref in zip(predictions, references)) / scored if scored else None
    tau = kendall_tau(references, predictions) if scored else None
    return (
        result_envelope(
            "step-ordering",
            len(records),
            scored,
            {"exact_match": exact_match, "kendall_tau": tau},
            errors,
        ),
        errors,
    )
