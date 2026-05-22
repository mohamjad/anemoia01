# FALCON H2 Local Downloaded-Data Run

Run date: 2026-05-22

Evidence level:

```text
downloaded_dataset_evidence
```

This note records a minimal local FALCON H2 artifact-bundle run against three
downloaded DANDI NWB files, one per required split. It is a downloaded-data
plumbing and reporting check over declared cue-character weak target proxies.
It is not a full FALCON H2 benchmark and does not claim direct access to true
intent.

## Interpretation

This run matters because it moves the FALCON H2 path from fixture-only plumbing
to a validated local artifact bundle over downloaded NWB files.

The result should be read as an infrastructure result:

```text
downloaded NWB files
-> typed inventory
-> declared cue-character weak targets
-> deterministic sanity-baseline predictions
-> protocol result
-> eval card
-> comparison report
-> validated bundle manifest
```

The `proxy_oracle` baseline copies the declared weak target and should achieve
zero loss. The `uniform_prior` baseline spreads probability over the declared
support and should perform worse. That ordering is a sanity check for the
bundle flow, not evidence that a neural decoder is better or worse.

The useful claim is narrow:

```text
The repository can generate and validate a reproducible FALCON H2 local
downloaded-data artifact bundle whose targets, predictions, scores, reports,
and provenance are inspectable.
```

## Source

DANDI dandiset:

```text
000950 version 0.241029.1403
```

Downloaded local root:

```text
data/external/h2
```

Files:

| Split | File | Size Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `held_in_calib` | `sub-T5-held-in-calib/sub-T5-held-in-calib_ses-20221215.nwb` | 17448705 | `24d0507c1fcd9451d502a6a883f80ed9be66834029e5e485b3921f2d40f39323` |
| `held_out_calib` | `sub-T5-held-out-calib/sub-T5-held-out-calib_ses-20230417.nwb` | 3312425 | `0de25c2b32e2ea02b571c0c649d6d692546bb766d2425893662b2b8201cc9b19` |
| `minival` | `sub-T5-held-in-minival/sub-T5-held-in-minival_ses-20220523.nwb` | 1226680 | `ee4c05afdf27aac047c09930dc8e4ffb4169eafaf4aa221090cfab76f14389d7` |

## Commands

The checkout did not have the console script installed, so commands were
executed through the module entry point with `PYTHONPATH=src`.

Inventory:

```text
PYTHONPATH=src python -m intentfidelity.cli.main ingest falcon-h2-inventory data/external --json
```

Bundle:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval falcon-h2-bundle data/external outputs/falcon-h2-bundle --evidence-level downloaded_dataset_evidence
```

Validation:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval falcon-h2-validate-bundle outputs/falcon-h2-bundle
```

Full tests:

```text
pytest -q
```

## Artifact Summary

Output directory:

```text
outputs/falcon-h2-bundle
```

Generated artifacts:

- `inventory.json`
- `targets.jsonl`
- `predictions.jsonl`
- `result.json`
- `eval_card.md`
- `comparison.md`
- `bundle_manifest.json`

Counts:

- data files: 3
- weak targets: 588
- baseline predictions: 1176
- methods: 2

Method scores:

| Method | Intent-Fidelity Log Loss |
| --- | ---: |
| `proxy_oracle` | 0.000000 |
| `uniform_prior` | 3.358308 |

Ranking disagreement:

```text
false
```

Validation result:

```text
is_valid: true
issues: []
```

## Scope Notes

- Targets are declared cue-character weak target proxies from FALCON H2 trial
  cue text.
- The deterministic baselines are `proxy_oracle` and `uniform_prior`; these are
  artifact sanity baselines, not neural decoder submissions.
- The run validates local downloaded-data ingestion, target construction,
  scoring, provenance, and report generation for a minimal split-covering
  subset.
- The result should not be described as full-dataset evidence or as measuring
  true intent directly.
