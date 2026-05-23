# Contributing

This project is research infrastructure. Contributions should make the evidence
flow more reproducible, typed, and explicit.

## Core Boundaries

Keep these layers separate:

- `resources`: dataset registry and source metadata
- `ingest`: raw file contracts, inventories, and dataset-specific parsing
- `labels`: weak targets, proxy events, predictions, and JSONL IO
- `metrics`: scoring rules and comparison metrics
- `protocols`: `EvalResult` assembly and artifact bundles
- `reports`: Markdown and JSON presentation
- `cli`: command wiring around tested APIs

Do not put dataset parsing in shared protocol code. Do not put report language
inside metric functions.

## Evidence Rules

- Do not claim direct access to true intent.
- Do not describe fixtures or synthetic scaffolds as downloaded-data evidence.
- Do not describe a raw data contract as target construction or scoring.
- Record null results as directly as ranking disagreements.
- Every reported result should state the proxy, protocol, evidence level, and
  limitations.

## Adding A Dataset

Start with the smallest local contract:

```text
resource manifest
-> raw file contract
-> fixture-backed inventory or parser
-> typed events or weak targets
-> JSONL IO
-> protocol scoring
-> report and artifact validation
```

Do not skip from a manifest to a thesis claim.

## Before Opening A Pull Request

Run:

```text
PYTHONPATH=src python -m intentfidelity.cli.main overview
PYTHONPATH=src python -m intentfidelity.cli.main audit repo --json
pytest -q
```

For CLI changes, add a `tests/test_cli.py` case. For manifest changes, run the
resource registry tests. For artifact bundle changes, add or update validation
tests.
