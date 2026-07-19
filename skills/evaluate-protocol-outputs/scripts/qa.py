"""Question-answering accuracy and confidence calibration metrics."""

from __future__ import annotations

from typing import Any

from common import failure, require, result_envelope


def evaluate(records: list[dict[str, Any]], **_: Any) -> tuple[dict[str, Any], list[dict[str, str]]]:
    correctness: list[int] = []
    confidences: list[float] = []
    calibration_correctness: list[int] = []
    errors: list[dict[str, str]] = []

    for index, item in enumerate(records):
        try:
            prediction = str(require(item, "prediction"))
            reference = str(require(item, "reference"))
            correct = int(prediction == reference)
            confidence = item.get("confidence")
            if confidence is not None:
                if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
                    raise ValueError("confidence must be numeric")
                if not 0 <= confidence <= 1:
                    raise ValueError("normalized confidence must be between 0 and 1")
                confidences.append(float(confidence))
                calibration_correctness.append(correct)
            correctness.append(correct)
        except Exception as exc:
            errors.append(failure(item, index, exc))

    scored = len(correctness)
    accuracy = sum(correctness) / scored if scored else None
    brier = (
        sum(
            (confidence - correct) ** 2
            for confidence, correct in zip(confidences, calibration_correctness)
        )
        / len(confidences)
        if confidences
        else None
    )
    return (
        result_envelope(
            "question-answering",
            len(records),
            scored,
            {"accuracy": accuracy, "brier_score": brier},
            errors,
            {"brier_samples": len(confidences)},
        ),
        errors,
    )
