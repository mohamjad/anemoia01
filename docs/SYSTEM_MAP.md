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
| `cli` | command wiring around typed APIs | hidden business logic |

## Current Resource Paths

| Resource | Current Path | Evidence Level |
| --- | --- | --- |
| FALCON H2 | NWB/HDF5 ingestion, character weak targets, held-out eval, baselines | fixture and local-data ready |
| Card 2024 | communication transcript scaffold | synthetic protocol scaffold |
| Willett 2023 | communication and language-prior scaffold | synthetic protocol scaffold |
| Kunz 2025 | authorization scaffold | synthetic protocol scaffold |
| AJILE12 | naturalistic behavior proxy scaffold | synthetic protocol scaffold |
| bigP3BCI | P300 selection proxy scaffold | synthetic protocol scaffold |

## Extension Pattern

For a new dataset path:

1. Add or update the resource manifest.
2. Add typed event or target schemas in `labels`.
3. Add JSONL IO beside the schema.
4. Add any proxy summary metric in `metrics`.
5. Add a protocol evaluator in `protocols`.
6. Add a report renderer in `reports`.
7. Add a CLI command only after the Python API is tested.
8. Add or update an experiment scaffold.
9. Update docs and evidence scope.
