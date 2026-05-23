# Handoff

This repository is the implementation engine for intent-fidelity evaluation
infrastructure for adaptive neural interfaces.

For the concise repo argument, read `README.md` and `docs/ARGUMENT.md` first.
The short version is: decoder accuracy remains necessary, but adaptive neural
interfaces also need reproducible evaluation artifacts that score fidelity to
declared weak target proxies under explicit protocols.

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

Current implementation includes `intentfidelity eval falcon-h2-bundle`, which
writes `inventory.json`, `targets.jsonl`, `predictions.jsonl`, `result.json`,
`eval_card.md`, `comparison.md`, and `bundle_manifest.json`. The command
defaults to `fixture_evidence`; pass `--evidence-level
downloaded_dataset_evidence` only for local runs against downloaded FALCON H2
files.

Validate completed bundles with:

```text
intentfidelity eval falcon-h2-validate-bundle outputs/falcon-h2-bundle
```

The validator checks expected artifacts, loadability, count consistency,
source-file hashes, evidence-level consistency, and report proxy-scope wording.

One minimal downloaded-data FALCON H2 bundle run is recorded in
`docs/FALCON_H2_LOCAL_RUN.md`. It uses one downloaded NWB file per required
split and remains scoped to declared cue-character proxy targets and sanity
baselines.

A stronger FALCON H2 feature-baseline method run is recorded in
`docs/FALCON_H2_METHOD_RUN.md`. It compares three centroid-style baselines on
five held-in train sessions and five held-out calibration sessions. The result
is a null ranking-disagreement result: proxy top-1 error and intent-fidelity
log loss rank the tested methods the same way.

Read `docs/EVIDENCE_STATUS.md` before making thesis-level claims. It records
what is demonstrated, what is not demonstrated, and the current FALCON-heavy
dataset bias risk.

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
