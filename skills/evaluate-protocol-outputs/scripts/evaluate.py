#!/usr/bin/env python3
"""Evaluate generic procedural-model outputs or BioProBench-compatible files."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

import error_detection
import generation
import judge_consistency
import ordering
import qa
from common import InputError, load_records, merge_failures, write_json
from normalize import TASK_ALIASES, canonical_task, infer_task, normalize_records


Evaluator = Callable[..., tuple[dict[str, Any], list[dict[str, str]]]]
EVALUATORS: dict[str, Evaluator] = {
    "question-answering": qa.evaluate,
    "protocol-error-detection": error_detection.evaluate,
    "step-ordering": ordering.evaluate,
    "protocol-generation": generation.evaluate,
    "judge-consistency": judge_consistency.evaluate,
}
BIOPROBENCH_ALIASES = {"PQA", "ERR", "ORD", "GEN", "REA-ERR"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate model outputs for procedural tasks")
    parser.add_argument(
        "--task",
        required=True,
        choices=[*TASK_ALIASES, "auto"],
        help="Generic task name, BioProBench alias, or auto",
    )
    parser.add_argument("--input", required=True, help="UTF-8 JSON array")
    parser.add_argument("--profile", choices=["generic", "bioprobench"], default="generic")
    parser.add_argument(
        "--parser",
        choices=["auto", "structured", "answer-tags", "last-line"],
        default="auto",
        help="How to parse generic predictions",
    )
    parser.add_argument("--prediction-field", default="prediction")
    parser.add_argument("--reference-field", default="reference")
    parser.add_argument("--confidence-field", default="confidence")
    parser.add_argument("--items-field", default="items")
    parser.add_argument("--id-field", default="id")
    parser.add_argument("--output", help="Optional metrics JSON output path")
    parser.add_argument("--errors", help="Optional JSONL path for sample-level failures")
    parser.add_argument("--strict", action="store_true", help="Exit with status 2 on partial evaluation")
    semantic = parser.add_argument_group("generation metrics")
    semantic.add_argument("--metrics", choices=["core", "semantic", "all"], default="core")
    semantic.add_argument("--offline", action="store_true")
    semantic.add_argument("--embedding-model", default=generation.DEFAULT_EMBEDDING_MODEL)
    semantic.add_argument("--keyword-model", default=generation.DEFAULT_KEYWORD_MODEL)
    semantic.add_argument("--similarity-threshold", type=float, default=0.7)
    semantic.add_argument("--top-k", type=int, default=64)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    fields = {
        "prediction": args.prediction_field,
        "reference": args.reference_field,
        "confidence": args.confidence_field,
        "items": args.items_field,
        "id": args.id_field,
    }
    try:
        records = load_records(args.input)
        profile = "bioprobench" if args.task in BIOPROBENCH_ALIASES else args.profile
        task = infer_task(records, profile, fields) if args.task == "auto" else canonical_task(args.task)
        normalized, normalization_errors = normalize_records(
            records, task, profile, args.parser, fields
        )
        result, evaluation_errors = EVALUATORS[task](
            normalized,
            metrics_mode=args.metrics,
            offline=args.offline,
            embedding_model=args.embedding_model,
            keyword_model=args.keyword_model,
            similarity_threshold=args.similarity_threshold,
            top_k=args.top_k,
        )
        errors = normalization_errors + evaluation_errors
        merge_failures(result, errors, len(records))
        result["config"].update(
            {
                "profile": profile,
                "parser": "profile-defined" if profile == "bioprobench" else args.parser,
                "fields": fields if profile == "generic" else None,
            }
        )
        if args.output:
            write_json(args.output, result)
        if args.errors:
            write_json(args.errors, errors, jsonl=True)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 2 if args.strict and errors else 0
    except (InputError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
