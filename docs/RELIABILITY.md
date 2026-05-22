# Reliability

Reliability in this repo means the evaluation artifact is reproducible,
scope-limited, and explicit about its proxy assumptions.

## Gates Before Push

Always run:

```text
pytest -q
git status --short --branch
```

For resource manifest changes:

```text
pytest tests/test_resource_registry.py tests/test_resource_schema.py -q
```

For CLI changes, test the command in `tests/test_cli.py` and verify the output
contract, not only exit status.

For FALCON H2 bundle changes, run:

```text
pytest tests/test_falcon_h2_artifacts.py tests/test_cli.py -q
```

## Evidence Levels

Use these terms consistently:

- `manifest only`: resource exists in the registry but has no protocol scaffold.
- `synthetic_protocol_scaffold`: executable scaffold using synthetic data only.
- `fixture_evidence`: repository fixture or synthetic file validates ingestion.
- `downloaded_dataset_evidence`: local run against downloaded dataset files.
- `reported_result`: result artifact has an eval card and documented scope.

Do not describe scaffold or fixture results as real dataset evidence.

## Failure Modes To Guard

- target and prediction supports do not match
- predictions reference missing targets
- event confidence is outside `[0, 1]`
- report text implies true intent was observed
- a dataset-specific parser leaks into shared protocol code
- a synthetic experiment is mistaken for evidence
- result metadata omits target type or evidence scope

## Result Artifact Expectations

A complete evaluation handoff should include:

- resource manifest
- target construction notes
- target JSONL or equivalent typed artifact
- prediction JSONL or baseline configuration
- `EvalResult` JSON
- report card or protocol Markdown
- test command used to validate the run
- data provenance and limitations

The FALCON H2 bundle command writes these artifacts directly and records
`evidence_level`, `target_type`, file counts, target counts, and prediction
counts in `bundle_manifest.json` and `result.json` metadata.

## Review Checklist

Before handing off a pass, check:

- authoritative docs reflect the current state
- no stale pass status remains in manifests or experiment docs
- new public APIs are exported from package `__init__.py` files
- CLI docs list new commands
- reports state proxy limitations
- full tests pass
- git branch is clean after push
