---
name: evaluate-protocol-outputs
description: Evaluate model outputs for biological and scientific procedural tasks, including question answering against reference answers, detecting whether protocols contain errors, restoring shuffled step order, comparing generated protocols with references, and aggregating precomputed judge consistency decisions. Use when an agent needs to score, compare, validate, or diagnose prediction files with accuracy, calibration, classification, ordering, lexical, or semantic metrics. Accept generic JSON field mappings and BioProBench-compatible files.
---

# Evaluate Protocol Outputs

Normalize prediction data, run deterministic metrics, and report scored and failed samples. Do not assume access to a particular repository.

## Workflow

1. Select one task from the table below.

| Task | Select when |
|---|---|
| `question-answering` | Each sample contains a predicted answer and a reference answer; confidence is optional. |
| `protocol-error-detection` | Each sample predicts whether a protocol contains an error; `true` means an error exists. |
| `step-ordering` | Each sample restores the order of a fixed set of shuffled steps. |
| `protocol-generation` | Each sample contains a generated protocol and a reference protocol. |
| `judge-consistency` | Each sample contains a precomputed boolean judge decision; the metric reports the fraction judged `true`. |
2. Read `references/input-formats.md` when the input does not already use `prediction`, `reference`, `confidence`, and `items`.
3. Run the evaluator from this skill directory:

```bash
python scripts/evaluate.py --task step-ordering --input /absolute/path/predictions.json
```

4. Map custom fields instead of rewriting the source data:

```bash
python scripts/evaluate.py \
  --task question-answering \
  --input /absolute/path/predictions.json \
  --prediction-field model_output \
  --reference-field gold_answer \
  --confidence-field probability
```

5. Add `--output metrics.json`, `--errors errors.jsonl`, or `--strict` when needed.
6. Report the task, profile, metrics, total/scored/failed counts, and parsing assumptions.

Prefer structured predictions. Use `--parser answer-tags` or `--parser last-line` only for raw model text. Use `--task auto` only when the task is structurally unambiguous.

## Generation metrics

Use `--metrics core` by default for dependency-free exact match and token-overlap metrics. Use `--metrics semantic` or `--metrics all` for BLEU, METEOR, ROUGE, keyword, embedding, and step metrics after installing:

```bash
python -m pip install -r requirements-semantic.txt
```

Use `--offline` only when NLTK resources and sentence-transformer models are already cached or supplied as local model paths.

## BioProBench compatibility

Use `--profile bioprobench` with descriptive task names, or pass `PQA`, `ERR`, `ORD`, `GEN`, or `REA-ERR` directly. The shorter names `qa`, `error-detection`, `ordering`, and `generation` remain CLI aliases only. Read `references/bioprobench-profile.md` for field and parsing mappings.

Read `references/metric-definitions.md` before interpreting positive classes, units, semantic settings, or failure handling.
