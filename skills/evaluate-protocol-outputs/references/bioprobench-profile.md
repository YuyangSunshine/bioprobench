# BioProBench profile

Use `--profile bioprobench` to adapt benchmark-shaped records to the generic internal protocol. The following aliases select this profile automatically.

| Alias | Generic task | Input mapping |
|---|---|---|
| `PQA` | `question-answering` | `generated_response` → prediction/confidence; `answer` → reference |
| `ERR` | `protocol-error-detection` | invert predicted correctness and `is_correct` into `has_error` booleans |
| `ORD` | `step-ordering` | parse indices from `generated_response`; apply them to `wrong_steps`; compare with `correct_steps` |
| `GEN` | `protocol-generation` | strip model wrappers from `generated_response`; use `output` as reference |
| `REA-ERR` | `judge-consistency` | parse the existing `LLM_judge` field |

Examples:

```bash
python scripts/evaluate.py --task PQA --input pqa-results.json
python scripts/evaluate.py --profile bioprobench --task step-ordering --input ord-results.json
python scripts/evaluate.py --task GEN --metrics all --input generation-results.json
```

The profile only normalizes schema and parsing conventions. All output task names and metric units follow the generic interface.
