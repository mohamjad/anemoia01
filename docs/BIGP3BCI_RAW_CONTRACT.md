# bigP3BCI Raw Contract

This is the first non-FALCON raw-data contract in the repo. It is intentionally
limited to local file inventory, fixture-backed event extraction, and a
fixture-backed artifact bundle path.

Source: https://physionet.org/content/bigp3bci/1.0.0/

## Scope

Implemented:

- resolve a local `bigP3BCI-data` root from either the data parent or dataset
  root
- inventory EDF+ files under the expected PhysioNet hierarchy
- parse study, subject, session, phase, condition path, file index, path, and
  byte size
- report structured validation issues for missing roots, empty roots, and
  invalid EDF paths
- read numeric EDF+ record signals from valid local files
- infer symbol-grid candidates from labels shaped like `<symbol>_<row>_<column>`
- export typed `P300SelectionEvent` JSONL from `StimulusBegin`,
  `StimulusType`, `CurrentTarget`, and optional `SelectedTarget` signals
- generate a fixture-backed selection artifact bundle with inventory, events,
  weak targets, sanity predictions, `EvalResult`, diagnostics, reports, and a
  manifest
- validate bundle counts, event/target/prediction coverage, source hashes,
  evidence scope, and proxy-limitation language
- expose the raw contract through Python and CLI JSON

Not implemented:

- broad downloaded-data validation of event extraction
- P300 timing-window alignment
- neural decoder baselines for bigP3BCI

## Local Layout

Expected local root:

```text
data/external/bigP3BCI-data
```

Expected file shape:

```text
bigP3BCI-data/
  Study*/
    <subject_id>/
      <session_id>/
        <Train|Test>/
          <condition...>/
            *<Train|Test><index>.edf
```

The inventory parser currently validates:

- study directory starts with `Study`
- subject directory follows examples such as `A_01` or `S1_01`
- session directory follows examples such as `SE001`
- phase directory is `Train` or `Test`
- file name phase matches the phase directory

## Record Labels

The raw contract records these EDF+ labels as required by the future parser:

```text
StimulusBegin
StimulusType
CurrentTarget
```

Feedback-style labels are tracked separately as optional prefixes:

```text
SelectedTarget
SelectedRow
SelectedColumn
DisplayResult
FakeFeedback
```

These labels are parsed as numeric EDF+ record signals by the fixture-backed
event extractor. This is not yet downloaded-data evidence.

## Command

```text
PYTHONPATH=src python -m intentfidelity.cli.main ingest bigp3bci-inventory \
  data/external --json
```

Extract typed selection events:

```text
PYTHONPATH=src python -m intentfidelity.cli.main ingest bigp3bci-events \
  data/external outputs/bigp3bci-events.jsonl
```

Create and validate a fixture-scoped artifact bundle:

```text
PYTHONPATH=src python -m intentfidelity.cli.main eval bigp3bci-bundle \
  data/external outputs/bigp3bci-bundle

PYTHONPATH=src python -m intentfidelity.cli.main eval bigp3bci-validate-bundle \
  outputs/bigp3bci-bundle
```

The inventory command emits an inventory JSON object and embeds the raw-data
contract. The event command writes `P300SelectionEvent` JSONL. The bundle
command writes `inventory.json`, `events.jsonl`, `targets.jsonl`,
`predictions.jsonl`, `result.json`, `diagnostics.json`, `diagnostics.md`,
`eval_card.md`, `selection_report.md`, `comparison.md`, and
`bundle_manifest.json`.

Successful fixture-backed extraction or bundle validation is not evidence for
the thesis and should not be described as a downloaded dataset run.

The first single-file downloaded EDF+ validation run is recorded in
`docs/BIGP3BCI_LOCAL_RUN.md`. It validates bundle mechanics on one public file
and remains limited to sanity baselines.
