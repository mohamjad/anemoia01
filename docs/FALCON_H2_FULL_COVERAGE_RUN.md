# FALCON H2 Full-Coverage Local Run

Run date: 2026-05-23

Evidence level:

```text
downloaded_dataset_evidence
```

This note records the full local FALCON H2 run for the configured DANDI version
used by the repo.

It remains scoped to declared cue-character weak target proxies. It does not
claim direct access to true intent, and it does not compare submitted decoder
systems.

## Source

DANDI dandiset:

```text
000950 version 0.241029.1403
```

Local root:

```text
data/external/h2
```

Downloaded NWB assets:

| Split | Files | Bytes |
| --- | ---: | ---: |
| `held_in_calib` | 21 | 1135747851 |
| `held_out_calib` | 5 | 18812720 |
| `minival` | 21 | 70396165 |
| Total | 47 | 1224956736 |

The generated bundle manifests record per-file paths, sizes, splits, and
SHA-256 hashes.

## Commands

Inventory:

```text
PYTHONPATH=src python -m intentfidelity.cli.main ingest falcon-h2-inventory data/external --json
```

Full sanity bundle:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval falcon-h2-bundle data/external outputs/falcon-h2-full-bundle --evidence-level downloaded_dataset_evidence
```

Full sanity bundle validation:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval falcon-h2-validate-bundle outputs/falcon-h2-full-bundle
```

Full feature-baseline method bundle:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval falcon-h2-feature-bundle data/external data/external outputs/falcon-h2-full-feature-bundle --evidence-level downloaded_dataset_evidence
```

Full feature-baseline validation:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval falcon-h2-validate-feature-bundle outputs/falcon-h2-full-feature-bundle
```

## Sanity Bundle Result

The full sanity bundle used all 47 NWB assets.

Counts:

- data files: 47
- weak targets: 29636
- sanity predictions: 59272

Method scores:

| Method | Intent-Fidelity Log Loss |
| --- | ---: |
| `proxy_oracle` | 0.000000 |
| `uniform_prior` | 3.366593 |

Validation:

```text
is_valid: true
issues: []
```

This result is a full-asset artifact-flow check. It is not a decoder comparison.

## Feature-Baseline Method Result

The feature-baseline bundle used:

- train split: all 21 `held_in_calib` files
- test split: all 5 `held_out_calib` files
- train examples: 27263
- test examples: 561
- scored weak targets: 561
- predictions: 1683
- latent drift artifacts: `latent_drift.json`, `latent_drift.md`

Methods:

- `identity_centroid`
- `session_centered_centroid`
- `whitened_centroid`

Scoring:

- conventional score: proxy top-1 error against the declared cue-character target
- intent-fidelity score: log loss against the declared weak target distribution

Predictions were projected onto each target's declared support with
`support_floor_mass = 1e-6`.

| Method | Proxy Top-1 Error | Intent-Fidelity Log Loss |
| --- | ---: | ---: |
| `whitened_centroid` | 0.889483 | 3.158741 |
| `session_centered_centroid` | 0.893048 | 3.149373 |
| `identity_centroid` | 0.978610 | 3.169953 |

Ranking by conventional proxy top-1 error:

```text
whitened_centroid -> session_centered_centroid -> identity_centroid
```

Ranking by intent-fidelity log loss:

```text
session_centered_centroid -> whitened_centroid -> identity_centroid
```

Ranking disagreement:

```text
true
```

Kendall tau distance:

```text
1
```

Reversal rate:

```text
0.333
```

Validation:

```text
is_valid: true
issues: []
```

The regenerated feature bundle also includes a PCA/SVD latent drift report. It
is a neural feature-state probe, not a direct intent readout. The optional CEBRA
backend was not used for this recorded run.

## Interpretation

This is the first FALCON H2 downloaded-data method run in this repo that shows
ranking disagreement between a conventional proxy metric and an
intent-fidelity metric.

The result is narrow:

```text
For three centroid-style baselines on the downloaded FALCON H2 held-out
calibration split, proxy top-1 error and intent-fidelity log loss select
different top methods.
```

The result does not show that decoder accuracy generally fails, that these
baselines are competitive decoders, or that true intent is observed. It shows
that the infrastructure can surface a real metric-ranking disagreement under a
declared proxy contract.

## Implementation Note

This run exposed and fixed a structural issue before the full artifacts were
accepted: FALCON sample IDs previously used dataset, session date, and trial id
but not split. Full asset coverage includes held-in and minival files sharing
session dates and trial ids, so sample IDs now include the split:

```text
falcon_h2:<split>:<session_date>:trial-<id>:char-<index>
```

This prevents target and prediction collisions across splits.
