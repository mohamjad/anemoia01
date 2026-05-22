# Handoff

This repository is the implementation engine for intent-fidelity evaluation
infrastructure for adaptive neural interfaces.

## Current State

The repo now has six scaffold passes:

1. Core package architecture, resource registry, weak target schemas, scoring
   metrics, protocol result schemas, cards, CLI, and tests.
2. FALCON H2 NWB/HDF5 ingestion, handwriting cue targets, held-out-session
   evaluation, and FALCON-specific CLI paths.
3. Method comparison, centroid baselines, ranking disagreement reports, and
   over-adaptation checks.
4. Communication, language-prior attribution, and authorization protocol
   scaffolds.
5. Naturalistic weak-label scaffolding for AJILE12-style behavior proxies.
6. Selection weak-target scaffolding for bigP3BCI-style P300 symbol proxies.

All non-FALCON resource paths remain synthetic protocol scaffolds. They validate
contracts and report language, not real-data evidence.

## Current Frontier

Move from scaffolded protocol contracts into real-data evidence.

Recommended next step:

1. Choose the next real-data path explicitly.
2. Prefer FALCON H2 unless the user selects a speech, naturalistic, or P300 path.
3. Keep ingestion separate from target construction and protocol scoring.
4. Add tests with each ingestion or evaluation change.
5. Update source-of-truth, architecture, CLI, and pass docs in the same pass.

## Most Concrete Next Pass

Build a real FALCON H2 evidence pass:

1. Define a local data contract for where NWB files live and which split names
   are required.
2. Add a small command that writes a complete eval artifact bundle:
   `targets.jsonl`, `predictions.jsonl`, `result.json`, `eval_card.md`, and
   `comparison.md` when applicable.
3. Add fixture-level tests using synthetic NWB/HDF5 files first.
4. Add docs that distinguish fixture evidence from downloaded dataset evidence.
5. Run the full suite and push small commits.

## Invariants

- Do not claim direct access to true intent.
- Metrics evaluate fidelity to declared proxies.
- Synthetic scaffolds are sanity checks only.
- Real-data ingestion must be dataset-specific and typed.
- Protocol scoring must remain reusable across datasets.
- Reports must state evidence scope and proxy limitations.

## Verification Commands

```text
pytest -q
intentfidelity resources validate
intentfidelity resources list
```

When changing CLI behavior, add a `tests/test_cli.py` case for the exact command.

When changing a resource manifest, run:

```text
pytest tests/test_resource_registry.py tests/test_resource_schema.py -q
```
