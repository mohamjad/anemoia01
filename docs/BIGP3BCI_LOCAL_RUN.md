# bigP3BCI Local Downloaded-Data Run

This document records the first local downloaded-data bigP3BCI artifact run.
It validates that the EDF+ ingestion, event extraction, weak-target
construction, sanity predictions, diagnostics, reports, and bundle validation
work on a real public PhysioNet EDF file.

It is not neural decoder evidence.

## Evidence Level

```text
downloaded_dataset_evidence
```

This label means the bundle was generated from a locally downloaded public
dataset file. It does not mean the resulting sanity-baseline scores prove the
intent-fidelity thesis.

## Source

Dataset:

```text
bigP3BCI 1.0.0
https://physionet.org/content/bigp3bci/1.0.0/
```

Downloaded file:

```text
data/external/bigP3BCI-data/StudyA/A_01/SE001/Train/CB/A_01_SE001_CB_Train01.edf
```

File provenance recorded in the bundle:

```text
size_bytes: 8057142
sha256: fe530cccb751a2b40f27e03d20224d4f9941a00980f792a3a575a62e0709a6fa
```

## Commands

Inventory:

```text
PYTHONPATH=src python -m intentfidelity.cli.main ingest bigp3bci-inventory \
  data/external --json
```

Event extraction:

```text
PYTHONPATH=src python -m intentfidelity.cli.main ingest bigp3bci-events \
  data/external outputs/bigp3bci-real-events.jsonl
```

Bundle generation:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval bigp3bci-bundle \
  data/external outputs/bigp3bci-real-bundle \
  --evidence-level downloaded_dataset_evidence
```

Bundle validation:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval bigp3bci-validate-bundle \
  outputs/bigp3bci-real-bundle
```

Validation result:

```text
is_valid: true
issues: []
```

## Artifact Summary

The run produced:

- `inventory.json`
- `events.jsonl`
- `targets.jsonl`
- `predictions.jsonl`
- `result.json`
- `diagnostics.json`
- `diagnostics.md`
- `eval_card.md`
- `selection_report.md`
- `comparison.md`
- `bundle_manifest.json`

Counts:

```text
data_file_count: 1
event_count: 7
target_count: 7
prediction_count: 21
method_count: 3
```

The extracted candidate support contains 72 selection symbols. The downloaded
Train file did not expose selected-symbol feedback for these events, so
`observed_selection_feedback` falls back to a uniform sanity prediction.

## Diagnostics

The diagnostics are proxy diagnostics. They evaluate declared target-symbol
distributions and prediction streams, not true intent.

Method diagnostics:

```text
selection_proxy_oracle:        log_loss 0.000, proxy_top1_accuracy 1.000
selection_uniform_prior:       log_loss 4.277, proxy_top1_accuracy 0.000
observed_selection_feedback:   log_loss 4.277, proxy_top1_accuracy 0.000
```

Bootstrap ranking stability:

```text
selection_proxy_oracle top frequency: 1.000
```

Proxy-state dynamics:

```text
transitions: 6
mean_target_shift: 0.693
target_top_label_switch_rate: 1.000
```

The proxy-state signal says that the declared prompted symbol changes on every
extracted transition. The proxy oracle tracks those shifts by construction; the
uniform sanity baselines do not. This is useful as a bundle sanity check, not as
a decoder result.

## Boundary

Do not claim:

- bigP3BCI neural decoding has been solved
- the current bigP3BCI scores compare real decoder methods
- selected-symbol feedback was available in this Train subset
- true intent is directly observed
- the broad thesis is proven across datasets

Accurate statement:

```text
The repo has validated the bigP3BCI downloaded EDF+ ingestion and artifact
bundle path on one public file, using prompted-symbol weak targets and sanity
baselines.
```
