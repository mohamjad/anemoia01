# Next Chat Brief

Build `anemoia01` as a clean infrastructure repo for intent-fidelity evaluation.

Do not transform `neurodrift-lab` in place.

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

Do not backdate commits or fabricate history.

Keep claims narrow:

```text
decoder accuracy can be insufficient under weak supervision and nonstationarity
```

The next real-data target should be FALCON H2 evidence or a carefully scoped
dataset-specific ingestion path selected by the user.
