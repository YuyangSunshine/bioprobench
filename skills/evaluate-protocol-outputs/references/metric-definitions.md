# Metric definitions

## Failure policy

Calculate metrics over successfully normalized and evaluated samples. Report excluded samples under `samples.failed`. Use `--errors` to retain reasons and `--strict` to reject partial evaluation.

## `question-answering`

- `accuracy`: exact string-match rate.
- `brier_score`: mean squared difference between normalized confidence and binary correctness. Lower is better. Samples without confidence contribute to accuracy but not Brier Score.

## `protocol-error-detection`

- `accuracy`: boolean exact-match rate.
- `precision`, `recall`, `f1`: binary metrics with `has_error=true` as the positive class.

## `step-ordering`

- `exact_match`: fraction of predicted sequences exactly equal to references.
- `kendall_tau`: pairwise rank correlation aggregated across scored pairs, ranging from -1 through 1.

Prediction and reference sequences must contain the same unique scalar values.

## `protocol-generation`: core

- `exact_match`: equality after joining step arrays with newlines and trimming surrounding whitespace.
- `token_precision`, `token_recall`, `token_f1`: multiset overlap of lowercased Unicode word tokens.

Core metrics use only the Python standard library.

## `protocol-generation`: semantic

- `bleu`: sentence BLEU with unigram/bigram weights `(0.5, 0.5)` and NLTK smoothing method 1.
- `meteor`: NLTK METEOR over lowercased word tokens.
- `rouge1`, `rouge2`, `rougeL`: ROUGE F-measures with stemming.
- `keyword_precision`, `keyword_recall`, `keyword_f1`: overlap of KeyBERT keyword sets.
- `step_recall`: fraction of reference steps matching a predicted step above the embedding threshold.
- `redundancy_penalty`: fraction of predicted steps matching a reference step; despite the historical name, higher is better.

Step metrics are defined only when the reference is an array. Defaults are `sentence-transformers/all-mpnet-base-v2`, `sentence-transformers/all-MiniLM-L6-v2`, keyword count 64, and cosine threshold 0.7.

## `judge-consistency`

- `consistency`: fraction of successfully parsed precomputed judgments that are `true`, ranging from 0 through 1.
