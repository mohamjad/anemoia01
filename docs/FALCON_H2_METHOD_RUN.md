# FALCON H2 Feature-Baseline Method Run

Run date: 2026-05-22

Evidence level:

```text
downloaded_dataset_evidence
```

This note records a local FALCON H2 feature-baseline comparison against
downloaded DANDI NWB files. It is stronger than the sanity bundle because it
compares three real feature-derived baseline methods on held-out calibration
sessions.

It remains scoped to declared cue-character weak target proxies. It does not
claim direct access to true intent, and it is not a full FALCON H2 benchmark.

## Source

DANDI dandiset:

```text
000950 version 0.241029.1403
```

Local root:

```text
data/external/h2
```

Train split:

```text
sub-T5-held-in-calib
```

Test split:

```text
sub-T5-held-out-calib
```

The run used five held-in calibration sessions and all five held-out
calibration sessions available in the FALCON H2 asset listing.

## Commands

Inventory:

```text
PYTHONPATH=src python -m intentfidelity.cli.main ingest falcon-h2-inventory data/external --json
```

Feature-baseline bundle:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval falcon-h2-feature-bundle data/external data/external outputs/falcon-h2-feature-bundle --evidence-level downloaded_dataset_evidence
```

Validation:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval falcon-h2-validate-feature-bundle outputs/falcon-h2-feature-bundle
```

Full tests:

```text
pytest -q
```

## Artifact Summary

Output directory:

```text
outputs/falcon-h2-feature-bundle
```

Generated artifacts:

- `train_inventory.json`
- `test_inventory.json`
- `targets.jsonl`
- `predictions.jsonl`
- `baseline_runs.json`
- `result.json`
- `eval_card.md`
- `comparison.md`
- `bundle_manifest.json`

Counts:

- train files: 5
- test files: 5
- train examples: 4583
- test examples: 561
- scored weak targets: 561
- predictions: 1683
- methods: 3

Methods:

- `identity_centroid`
- `session_centered_centroid`
- `whitened_centroid`

Scoring:

- conventional score: proxy top-1 error against the declared cue-character target
- intent-fidelity score: log loss against the declared weak target distribution

Predictions were projected onto each target's declared support with
`support_floor_mass = 1e-6`, so labels absent from a trained centroid model
remain represented and penalized during scoring.

## Result

| Method | Proxy Top-1 Error | Intent-Fidelity Log Loss |
| --- | ---: | ---: |
| `session_centered_centroid` | 0.898396 | 3.138514 |
| `whitened_centroid` | 0.903743 | 3.152052 |
| `identity_centroid` | 0.962567 | 3.167253 |

Ranking disagreement:

```text
false
```

Both metrics ranked the methods:

```text
session_centered_centroid -> whitened_centroid -> identity_centroid
```

Validation result:

```text
is_valid: true
issues: []
```

## Interpretation

This is a null ranking-disagreement result for the tested FALCON H2 centroid
baselines. It does not support the claim that conventional proxy accuracy and
intent-fidelity log loss disagree in this setting.

It does support a narrower and more useful infrastructure claim:

```text
The repo can compare feature-derived methods on downloaded FALCON H2 held-out
sessions, score them with both proxy top-1 error and intent-fidelity log loss,
and emit a validated artifact bundle with provenance and report cards.
```

The null result is important. It means the thesis should not be presented as
"accuracy fails on FALCON H2." The stronger next claim requires either a method
set, protocol, or dataset path where ranking disagreement or over-adaptation is
actually observed.

## Remaining Limits

- Only five held-in calibration sessions were used for training, not the full
  held-in split.
- The baselines are simple centroid methods, not submitted decoder systems.
- Targets are declared cue-character proxies, not direct intent observations.
- No non-FALCON real-data ingestion path has been completed yet.
