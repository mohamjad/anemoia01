# bigP3BCI Raw Contract

This is the first non-FALCON raw-data contract in the repo. It is intentionally
limited to local file inventory.

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
- expose the raw contract through Python and CLI JSON

Not implemented:

- EDF+ signal loading
- EDF+ annotation extraction
- target-symbol construction
- P300 timing-window alignment
- downloaded-data evidence bundles for bigP3BCI

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

These labels are not parsed yet. They are contract metadata for the next pass.

## Command

```text
PYTHONPATH=src python -m intentfidelity.cli.main ingest bigp3bci-inventory \
  data/external --json
```

The command emits an inventory JSON object and embeds the raw-data contract. A
successful fixture-backed inventory is not evidence for the thesis and should
not be described as a downloaded dataset run.
