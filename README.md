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

The current downloaded-data run is intentionally narrow:

- source: DANDI FALCON H2, dandiset `000950`, version `0.241029.1403`
- data: one downloaded NWB file per required split
- targets: 588 declared cue-character weak target proxies
- predictions: 1176 deterministic sanity-baseline predictions
- methods: `proxy_oracle` and `uniform_prior`
- validation: bundle contract passed with no issues

This is evidence that the local artifact flow works on downloaded FALCON H2
files. It is not a full FALCON H2 benchmark and it is not evidence of direct
intent measurement.

See `docs/FALCON_H2_LOCAL_RUN.md` for exact files, hashes, commands, counts,
and scope notes.

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
- ranking disagreement and over-adaptation checks
- eval cards, comparison reports, and reproducible artifact bundles

## Run The Current FALCON H2 Flow

Install for local development or run with `PYTHONPATH=src`.

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

## Repository Map

Start here:

- `docs/SOURCE_OF_TRUTH.md` - product and measurement contract
- `docs/FALCON_H2_LOCAL_RUN.md` - current downloaded-data artifact run
- `docs/FALCON_H2_BUNDLE.md` - bundle contract and validation behavior
- `docs/SYSTEM_MAP.md` - module responsibilities and data flow
- `docs/RELIABILITY.md` - evidence levels and verification gates
- `docs/HANDOFF.md` - current status and invariants
- `docs/NEXT_STEPS.md` - next implementation steps

Core implementation:

- `src/intentfidelity/ingest/` - dataset-specific readers and inventories
- `src/intentfidelity/labels/` - weak targets, predictions, and JSONL IO
- `src/intentfidelity/metrics/` - scoring and comparison metrics
- `src/intentfidelity/protocols/` - evaluation results and artifact bundles
- `src/intentfidelity/reports/` - Markdown and JSON reports
- `src/intentfidelity/cli/` - command-line orchestration

## Claim Discipline

Use this language:

- intent fidelity
- weak target distribution
- intent proxy
- fidelity to declared weak target
- ranking disagreement
- over-adaptation
- held-out-session reliability

Avoid this language:

- the system observes true intent
- the metric measures what the brain means
- fixture results are real dataset evidence
- sanity baselines are decoder submissions
- the current minimal run is a full benchmark

The core claim should stay narrow:

```text
Decoder accuracy can be insufficient under weak supervision and
nonstationarity, so adaptive neural interfaces need explicit evaluation of
fidelity to declared weak target proxies.
```
