# Start Here

This repo is easiest to understand as an evidence artifact factory.

It does not try to infer true intent directly. It builds reproducible records
that show how predictions score against declared weak target proxies.

## One-Minute Orientation

The core architecture is:

```text
resource manifest
-> dataset-specific raw data contract
-> inventory or parser
-> weak target construction
-> prediction import or baseline prediction
-> protocol scoring
-> eval card and comparison report
-> validated artifact bundle
```

The novel part is the handoff object: every result should carry its data
provenance, proxy definition, scoring protocol, evidence level, and limitations
in a form that can be validated.

## Why This Is Architecture, Not A Demo

The repo is organized around durable contracts rather than one-off notebooks:

- ingestion modules only describe data and raw-file structure
- label modules own weak targets, proxy events, predictions, and JSONL IO
- metric modules score distributions without knowing dataset internals
- protocol modules assemble reusable `EvalResult` records
- report modules turn results into auditable Markdown and JSON artifacts
- audit and validation commands check that claims still match implementation

That separation is what makes the system extensible: a new dataset should enter
through a raw contract and typed events before it is allowed to become evidence.

## What Works Today

FALCON H2:

- Works now: downloaded NWB/HDF5 inventory, cue-character weak targets, feature
  baselines, eval cards, comparison reports, and validated bundles.
- Evidence boundary: one dataset family and simple feature baselines.

bigP3BCI:

- Works now: raw EDF+ file inventory, numeric record reading, and typed
  `P300SelectionEvent` JSONL export.
- Evidence boundary: fixture-backed extraction only; no downloaded-data event
  validation, prediction generation, scoring, or artifact bundle.

Speech, authorization, naturalistic:

- Works now: typed synthetic protocol scaffolds and report language.
- Evidence boundary: no real-data ingestion yet.

Current strongest result:

```text
FALCON H2 full feature-baseline run found a narrow ranking disagreement.
```

That is compelling infrastructure evidence. It is not comprehensive empirical
proof across datasets.

## First Commands

From a source checkout:

```text
PYTHONPATH=src python -m intentfidelity.cli.main overview
PYTHONPATH=src python -m intentfidelity.cli.main audit repo --json
pytest -q
```

With local FALCON H2 data:

```text
PYTHONPATH=src python -m intentfidelity.cli.main ingest falcon-h2-inventory \
  data/external --json

PYTHONPATH=src python -m intentfidelity.cli.main eval \
  falcon-h2-validate-feature-bundle outputs/falcon-h2-full-feature-bundle
```

With local bigP3BCI data:

```text
PYTHONPATH=src python -m intentfidelity.cli.main ingest bigp3bci-inventory \
  data/external --json

PYTHONPATH=src python -m intentfidelity.cli.main ingest bigp3bci-events \
  data/external outputs/bigp3bci-events.jsonl
```

## Read In This Order

1. `README.md` for the concise repo pitch.
2. `docs/ARGUMENT.md` for why intent fidelity is the measurement object.
3. `docs/EVIDENCE_STATUS.md` for what is and is not demonstrated.
4. `docs/SYSTEM_MAP.md` for module ownership.
5. `docs/FALCON_H2_FULL_COVERAGE_RUN.md` for the strongest current run.
6. `docs/BIGP3BCI_RAW_CONTRACT.md` for the first non-FALCON raw contract.
7. `docs/NEXT_STEPS.md` for the highest-value remaining work.

## What To Say

Accurate:

```text
The repo implements a validated intent-fidelity artifact flow and demonstrates
it on downloaded FALCON H2 data, including a narrow ranking disagreement among
simple feature baselines.
```

Too strong:

```text
The repo proves decoder accuracy fails across neural-interface datasets.
```

The right standard is: every claim should point to a reproducible artifact, a
declared proxy, and an evidence level.
