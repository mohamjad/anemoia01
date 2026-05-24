# anemoia01

`anemoia01` is intent-fidelity evaluation infrastructure for adaptive neural
interfaces.

Core idea:

```text
Decoder accuracy is necessary, but it is not always enough.
```

In long-running neural interfaces, labels can be weak, delayed, self-paced,
behaviorally confounded, or mediated by adaptive decoders and language models.
Under those conditions, a method can improve a conventional decoder metric
while becoming less faithful to the declared task proxy the system is supposed
to preserve.

This repo builds the evaluation layer for that failure mode.

It does not claim direct access to true intent. It evaluates fidelity to
declared weak target distributions constructed from explicit proxies such as
task prompts, timing windows, behavioral outputs, endorsement signals, language
priors, authorization states, and session metadata.

## What Exists Now

Fast orientation:

```text
PYTHONPATH=src python -m intentfidelity.cli.main overview
```

The repo has a working end-to-end FALCON H2 artifact path:

```text
NWB/HDF5 file or FALCON H2 data root
-> inventory
-> declared cue-character weak targets
-> deterministic baseline predictions
-> EvalResult JSON
-> eval card
-> comparison report
-> bundle manifest
-> bundle validation
```

The strongest current downloaded-data evidence is FALCON H2:

- source: DANDI FALCON H2, dandiset `000950`, version `0.241029.1403`
- full local cache: 47 NWB assets, 1.22 GB
- sanity bundle: all 47 assets, 29,636 declared cue-character weak targets
- feature bundle: all 21 held-in calibration sessions for training and all 5
  held-out calibration sessions for testing
- feature methods: `identity_centroid`, `session_centered_centroid`,
  `whitened_centroid`
- feature result: proxy top-1 error and intent-fidelity log loss disagree on
  the top two centroid baselines

This is evidence that the local artifact flow works on downloaded FALCON H2
files and can surface a real ranking disagreement for simple feature-derived
methods. It is not evidence that rankings always disagree, not a submitted
decoder benchmark, and not evidence of direct intent measurement.

FALCON H2 feature bundles also emit a latent feature-state report. The default
backend is deterministic PCA/SVD. An optional CEBRA backend is available behind
`intentfidelity[latent-cebra]` and `--latent-backend cebra`, but it remains a
neural feature-state probe rather than a direct intent readout.

See:

- `docs/FALCON_H2_LOCAL_RUN.md` for the sanity artifact bundle
- `docs/FALCON_H2_METHOD_RUN.md` for the feature-baseline method run
- `docs/FALCON_H2_FULL_COVERAGE_RUN.md` for the full-coverage FALCON H2 run
- `docs/LATENT_BACKENDS.md` for PCA/SVD and optional CEBRA latent probes
- `docs/EVIDENCE_STATUS.md` for the current empirical boundary
- `docs/DATASET_LANDSCAPE.md` for dataset-family coverage and remaining gaps

## Why This Matters

Conventional neural-interface evaluation often asks:

```text
Did the decoded output match the observed target?
```

That remains important. This repo adds a second question:

```text
Did the method remain faithful to the declared weak target distribution under
the protocol being evaluated?
```

The point is not to replace decoder metrics. The point is to detect cases where
conventional metrics and proxy-fidelity metrics select different methods, or
where adaptation improves a conventional score while worsening fidelity to the
declared proxy.

The infrastructure is organized around:

- resource manifests for open neural-interface datasets
- dataset-specific ingestion
- weak target construction
- prediction import and baseline prediction
- protocol scoring
- proxy-state and neural feature-state diagnostics
- ranking disagreement and over-adaptation checks
- eval cards, comparison reports, and reproducible artifact bundles

## Reproduce The Current Result

Install for local development or run with `PYTHONPATH=src`.

The documented downloaded-data result requires local FALCON H2 NWB files from
DANDI dandiset `000950`, version `0.241029.1403`. The repo does not vendor
those files.

Inventory a local FALCON H2 root:

```text
PYTHONPATH=src python -m intentfidelity.cli.main ingest falcon-h2-inventory data/external --json
```

Generate a bundle:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval falcon-h2-bundle data/external outputs/falcon-h2-bundle --evidence-level downloaded_dataset_evidence
```

Validate the bundle:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval falcon-h2-validate-bundle outputs/falcon-h2-bundle
```

Run tests:

```text
pytest -q
```

Audit the repo posture:

```text
PYTHONPATH=src python -m intentfidelity.cli.main audit repo --json
```

The current full-coverage result is recorded in
`docs/FALCON_H2_FULL_COVERAGE_RUN.md`. Re-running it requires the same local
data layout and may write ignored artifacts under `outputs/`.

## Repository Map

Start here:

- `docs/START_HERE.md` - guided first read and command path
- `docs/SOURCE_OF_TRUTH.md` - product and measurement contract
- `docs/EVIDENCE_STATUS.md` - what is and is not empirically demonstrated
- `docs/DATASET_LANDSCAPE.md` - resource families and evidence maturity
- `docs/FALCON_H2_LOCAL_RUN.md` - current downloaded-data artifact run
- `docs/FALCON_H2_METHOD_RUN.md` - current FALCON H2 feature-baseline run
- `docs/FALCON_H2_FULL_COVERAGE_RUN.md` - full FALCON H2 local run
- `docs/FALCON_H2_BUNDLE.md` - bundle contract and validation behavior
- `docs/BIGP3BCI_LOCAL_RUN.md` - first downloaded bigP3BCI EDF bundle run
- `docs/BIGP3BCI_RAW_CONTRACT.md` - non-FALCON raw inventory, event, and bundle boundary
- `docs/SYSTEM_MAP.md` - module responsibilities and data flow
- `docs/RELIABILITY.md` - evidence levels and verification gates
- `CONTRIBUTING.md` - contribution rules and evidence boundaries
- `docs/NEXT_STEPS.md` - next implementation steps

Core implementation:

- `src/intentfidelity/ingest/` - dataset-specific readers and inventories
- `src/intentfidelity/latent/` - PCA/SVD and optional CEBRA neural feature-state probes
- `src/intentfidelity/labels/` - weak targets, predictions, and JSONL IO
- `src/intentfidelity/metrics/` - scoring and comparison metrics
- `src/intentfidelity/protocols/` - evaluation results and artifact bundles
- `src/intentfidelity/reports/` - Markdown and JSON reports
- `src/intentfidelity/cli/` - command-line orchestration

## Current Status

```text
Decoder accuracy can be insufficient under weak supervision and
nonstationarity, so adaptive neural interfaces need explicit evaluation of
fidelity to declared weak target proxies.
```

That is the repo's architectural claim. The empirical state is narrower:
downloaded-data FALCON H2 evidence exists; comprehensive cross-dataset evidence
does not. bigP3BCI now has one downloaded EDF+ bundle validation run, but only
with sanity baselines, not neural decoder evidence.

## Contributing

Contributions should preserve the contract boundaries:

- ingestion describes raw data and dataset layout
- labels define weak targets, events, predictions, and JSONL IO
- metrics score distributions without dataset-specific parsing
- protocols assemble `EvalResult` records
- reports state evidence level and proxy limitations

See `CONTRIBUTING.md` before adding datasets, metrics, or evidence claims.

## License

MIT. See `LICENSE`.
