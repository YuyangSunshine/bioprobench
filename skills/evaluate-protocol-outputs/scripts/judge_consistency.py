"""Consistency rate for precomputed boolean judge decisions."""

from __future__ import annotations

from typing import Any

from common import failure, require, result_envelope


def evaluate(records: list[dict[str, Any]], **_: Any) -> tuple[dict[str, Any], list[dict[str, str]]]:
    judgments: list[bool] = []
    errors: list[dict[str, str]] = []
    for index, item in enumerate(records):
        try:
            prediction = require(item, "prediction")
            if type(prediction) is not bool:
                raise ValueError("judge prediction must be a boolean")
            judgments.append(prediction)
        except Exception as exc:
            errors.append(failure(item, index, exc))
    scored = len(judgments)
    consistency = sum(judgments) / scored if scored else None
    return (
        result_envelope(
            "judge-consistency",
            len(records),
            scored,
            {"consistency": consistency},
            errors,
            {"requires_precomputed_judgment": True},
        ),
        errors,
    )
