# Next Chat Brief

Build `anemoia01` as a clean infrastructure repo for intent-fidelity evaluation.

Do not transform `neurodrift-lab` in place.

Repo-facing explanation now lives in:

- `README.md`
- `docs/ARGUMENT.md`
- `docs/FALCON_H2_LOCAL_RUN.md`

Use `neurodrift-lab` only as reference material for:

- weak target distributions
- scoring utilities
- ranking disagreement
- over-adaptation detection
- synthetic sanity checks
- CLI/test discipline

Current status:

```text
Pass 4 added communication, language-prior attribution, and authorization
protocol scaffolds for the speech-path resources.
Pass 5 added naturalistic weak-label scaffolding for AJILE12-style behavior
proxies.
Pass 6 added selection weak-target scaffolding for bigP3BCI-style P300 symbol
selection.
```

Current task frontier:

```text
Use the FALCON H2 artifact bundle path for local evidence runs, then run it
against downloaded FALCON H2 files when available.
```

Read these before starting the next implementation pass:

- `docs/HANDOFF.md`
- `docs/NEXT_STEPS.md`
- `docs/SYSTEM_MAP.md`
- `docs/RELIABILITY.md`

Completed scaffold passes:

1. Core package, schemas, metrics, reports, CLI, and tests.
2. FALCON H2 ingestion and held-out-session evaluation.
3. Method comparison, baselines, ranking disagreement, and over-adaptation.
4. Communication, language-prior, and authorization scaffolds.
5. Naturalistic weak-label scaffolding.
6. Selection weak-target scaffolding.
7. Fixture-backed FALCON H2 artifact bundle flow.

FALCON H2 bundle command:

```text
intentfidelity eval falcon-h2-bundle <nwb-or-data-root> <output-dir>
intentfidelity eval falcon-h2-validate-bundle <output-dir>
```

The command defaults to `fixture_evidence`. Use `--evidence-level
downloaded_dataset_evidence` only for local runs against downloaded FALCON H2
files.

A minimal downloaded-data run is recorded in `docs/FALCON_H2_LOCAL_RUN.md`.
It uses one NWB file per required split and reports only proxy-oracle and
uniform sanity baselines against declared cue-character weak target proxies.

A feature-baseline method run is recorded in `docs/FALCON_H2_METHOD_RUN.md`.
It compares three centroid-style baselines on downloaded FALCON H2 data and
finds no ranking disagreement between proxy top-1 error and intent-fidelity log
loss for those tested methods.

The full-coverage FALCON H2 run is recorded in
`docs/FALCON_H2_FULL_COVERAGE_RUN.md`. It uses all 47 local NWB assets for the
sanity bundle and all held-in/held-out calibration files for the method bundle.
This full method run finds a narrow ranking disagreement between proxy top-1
error and intent-fidelity log loss for the top two centroid baselines.

Current evidence boundaries are summarized in `docs/EVIDENCE_STATUS.md`.
Dataset-family maturity is summarized in `docs/DATASET_LANDSCAPE.md`.
The first non-FALCON raw-file contract is documented in
`docs/BIGP3BCI_RAW_CONTRACT.md`; it inventories bigP3BCI EDF+ files and now has
fixture-backed typed event extraction plus a fixture-backed selection artifact
bundle from numeric EDF+ records. `docs/BIGP3BCI_LOCAL_RUN.md` records the first
single-file downloaded EDF+ validation run.

Do not backdate commits or fabricate history.

Keep claims narrow:

```text
decoder accuracy can be insufficient under weak supervision and nonstationarity
```

The next real-data target should be stronger FALCON H2 method evidence or the
next bigP3BCI step: broader downloaded EDF+ coverage plus real neural
prediction generation.
