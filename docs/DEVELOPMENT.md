# Development

## Code Organization

The package is organized by evaluation artifact:

- `resources`: resource manifests, validation, and external asset discovery.
- `ingest`: dataset-specific readers and raw-data summaries.
- `labels`: weak target, prediction, and proxy-event schemas plus JSONL IO.
- `metrics`: scoring rules, comparison metrics, text metrics, and proxy summaries.
- `protocols`: reusable evaluators that produce `EvalResult` objects.
- `baselines`: simple baseline methods and prediction builders.
- `reports`: Markdown and JSON renderers for cards and protocol summaries.
- `figures`: text/Markdown figure renderers for ranking and comparison outputs.
- `cli`: command-line orchestration around the same typed APIs.

Dataset-specific logic should enter through `ingest` and `labels`. Shared
evaluation logic belongs in `metrics`, `protocols`, and `reports`.

## Implementation Rules

- Keep modules typed, explicit, and small.
- Add IO helpers beside the schema they serialize.
- Keep protocol functions pure where practical: inputs in, `EvalResult` out.
- Put evidence-scope language in reports and docs, not buried in tests.
- Do not add a generic abstraction until two concrete dataset paths need it.
- Do not collapse distinct proxy types into one vague target schema.

## Test Discipline

Every implementation change should have a focused test:

- schema validation: `tests/test_*_labels.py`
- JSONL roundtrip: `tests/test_*_io.py`
- metrics: `tests/test_*_metrics.py`
- protocol scoring: `tests/test_*_protocol.py`
- report output: `tests/test_*_report.py`
- CLI behavior: `tests/test_cli.py`
- experiment runner: `tests/test_*_experiment.py`

Run the full suite before pushing:

```text
pytest -q
```

## Commit Discipline

Keep commits small and buildable. Good commit boundaries are:

- schema plus tests
- export plus tests
- IO plus roundtrip test
- metric plus tests
- protocol plus tests
- report plus tests
- CLI command plus CLI test
- experiment runner plus experiment test
- docs and manifest updates

Do not backdate commits or rewrite unrelated user changes.

## Style Expectations

Code should read as infrastructure, not as a demo:

- explicit dataclasses over loose dictionaries at module boundaries
- narrow function names that state the proxy or protocol
- deterministic ordering in reports and result construction
- plain errors that identify missing targets or invalid distributions
- report wording that keeps proxy limitations visible
