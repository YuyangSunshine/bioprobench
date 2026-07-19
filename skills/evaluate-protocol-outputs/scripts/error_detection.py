"""Binary error-detection metrics."""

from __future__ import annotations

from typing import Any

from common import failure, require, result_envelope


def evaluate(records: list[dict[str, Any]], **_: Any) -> tuple[dict[str, Any], list[dict[str, str]]]:
    predictions: list[bool] = []
    references: list[bool] = []
    errors: list[dict[str, str]] = []

    for index, item in enumerate(records):
        try:
            prediction = require(item, "prediction")
            reference = require(item, "reference")
            if type(prediction) is not bool or type(reference) is not bool:
                raise ValueError("prediction and reference must be booleans")
            predictions.append(prediction)
            references.append(reference)
        except Exception as exc:
            errors.append(failure(item, index, exc))

    scored = len(predictions)
    true_positive = sum(pred is True and ref is True for pred, ref in zip(predictions, references))
    false_positive = sum(pred is True and ref is False for pred, ref in zip(predictions, references))
    false_negative = sum(pred is False and ref is True for pred, ref in zip(predictions, references))
    accuracy = sum(pred == ref for pred, ref in zip(predictions, references)) / scored if scored else None
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return (
        result_envelope(
            "protocol-error-detection",
            len(records),
            scored,
            {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1},
            errors,
            {"positive_class": "has_error=true"},
        ),
        errors,
    )
