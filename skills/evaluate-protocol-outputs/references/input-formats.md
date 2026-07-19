# Input formats

Provide a UTF-8 JSON file whose top-level value is an array of objects. An `id` field is optional but recommended.

## Canonical fields

Use these fields when possible:

- `prediction`: model output after parsing.
- `reference`: expected output; not required for `judge-consistency`.
- `confidence`: optional QA confidence in `0..1` or `0..100`.
- `items`: optional source items when an ordering prediction contains indices.
- `id`: optional sample identifier.

## Task examples

### Question answering

```json
[
  {"id":"q1","prediction":"0.3","reference":"0.3","confidence":0.9},
  {"id":"q2","prediction":"PBS","reference":"PBS"}
]
```

Accuracy uses every valid sample. Brier Score uses only samples with confidence.

### Error detection

Represent whether an error exists. `true` is the positive class.

```json
[{"id":"e1","prediction":true,"reference":true}]
```

### Step ordering

Provide ordered values directly:

```json
[{"prediction":["wash","spin","resuspend"],"reference":["wash","spin","resuspend"]}]
```

Or provide zero-based permutations plus `items`:

```json
[{
  "items":["spin","wash","resuspend"],
  "prediction":[1,0,2],
  "reference":[1,0,2]
}]
```

### Protocol generation

Use strings or arrays of step strings:

```json
[{
  "prediction":["Add buffer","Centrifuge"],
  "reference":["Add buffer","Centrifuge"]
}]
```

### Judge consistency

Supply a precomputed boolean decision as `prediction`:

```json
[{"id":"j1","prediction":true}]
```

The evaluator never calls an external judge model.

## Custom field mapping

Map flat or dotted object paths:

```bash
python scripts/evaluate.py \
  --task protocol-generation \
  --input results.json \
  --prediction-field result.text \
  --reference-field expected.protocol
```

Available options are `--prediction-field`, `--reference-field`, `--confidence-field`, `--items-field`, and `--id-field`.

## Raw-text parsers

- `structured`: require native strings, booleans, or arrays.
- `answer-tags`: read the final `[ANSWER_START]...[ANSWER_END]` block.
- `last-line`: use the last line where the task permits it.
- `auto`: preserve structured data and recognize answer tags or simple boolean text.

Prefer explicit parsers in reproducible evaluations.

## Output

All tasks produce a stable envelope:

```json
{
  "skill":"evaluate-protocol-outputs",
  "version":"2.0.0",
  "task":"step-ordering",
  "samples":{"total":10,"scored":9,"failed":1,"failure_rate":0.1},
  "metrics":{"exact_match":0.7,"kendall_tau":0.88},
  "config":{"profile":"generic","parser":"auto"}
}
```

Undefined aggregate metrics are JSON `null`, never `NaN`.
