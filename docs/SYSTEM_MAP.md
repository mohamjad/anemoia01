# System Map

The system is built around a single flow:

```text
resource manifest
-> dataset-specific ingestion
-> proxy event or weak target construction
-> prediction import or baseline prediction
-> protocol scoring
-> method comparison
-> report card
```

## Module Responsibilities

| Module | Owns | Should Not Own |
| --- | --- | --- |
| `resources` | dataset registry, manifest validation, asset discovery | scoring logic |
| `ingest` | dataset-specific raw file readers | protocol decisions |
| `labels` | proxy events, weak targets, predictions, JSONL IO | scoring rules |
| `metrics` | scoring rules and summary metrics | dataset parsing |
| `protocols` | evaluation assembly into `EvalResult` | raw file parsing |
| `baselines` | simple method implementations and predictions | report language |
| `reports` | Markdown and JSON rendering | metric computation |
| `figures` | lightweight comparison visualizations | evaluation state |
| `audit` | repository posture checks and evidence-boundary gates | empirical scoring |
| `overview` | navigable repo status and command guidance | hidden validation logic |
| `cli` | command wiring around typed APIs | hidden business logic |

## Current Resource Paths

| Resource | Current Path | Evidence Level |
| --- | --- | --- |
| FALCON H2 | NWB/HDF5 ingestion, character weak targets, held-out eval, baselines | fixture and local-data ready |
| Card 2024 | communication transcript scaffold | synthetic protocol scaffold |
| Willett 2023 | communication and language-prior scaffold | synthetic protocol scaffold |
| Kunz 2025 | authorization scaffold | synthetic protocol scaffold |
| AJILE12 | naturalistic behavior proxy scaffold | synthetic protocol scaffold |
| bigP3BCI | EDF+ raw-file inventory contract plus P300 selection proxy scaffold | raw inventory contract; no target evidence |

## Extension Pattern

For a new dataset path:

1. Add or update the resource manifest.
2. Add a dataset-specific raw contract in `ingest`.
3. Add typed event or target schemas in `labels`.
4. Add JSONL IO beside the schema.
5. Add any proxy summary metric in `metrics`.
6. Add a protocol evaluator in `protocols`.
7. Add a report renderer in `reports`.
8. Add a CLI command only after the Python API is tested.
9. Add or update an experiment scaffold.
10. Update docs and evidence scope.

## Artifact Bundle Flow

FALCON H2 now has a local bundle writer:

```text
NWB/HDF5 file or FALCON H2 data root
-> inventory.json
-> targets.jsonl
-> predictions.jsonl
-> result.json
-> eval_card.md
-> comparison.md
-> bundle_manifest.json
```

The implementation keeps ingestion, target construction, baseline prediction,
protocol scoring, and report rendering in separate modules. Bundle metadata
records evidence level and target type so fixture results are not confused with
downloaded dataset evidence.

FALCON H2 bundle validation checks the generated file contract, result and JSONL
loadability, count consistency, source-file hashes, evidence-level consistency,
and report language that keeps proxy limitations visible.

## Navigation Layer

The repo has two first-stop UX surfaces:

```text
intentfidelity overview
intentfidelity audit repo --json
```

`overview` explains the thesis, current evidence paths, boundaries, quick
commands, and docs to read next. `audit repo` is stricter: it checks that the
authoritative docs and manifests still describe the implemented evidence
posture.
