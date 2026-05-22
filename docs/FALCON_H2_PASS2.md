# FALCON H2 Pass 2

Pass 2 starts with layout validation before trial-level NWB parsing.

Expected local structure:

```text
data/
  h2/
    held_in_calib/
    held_out_calib/
    minival/
```

The inventory step scans each split for `.nwb`, `.h5`, or `.hdf5` files and
reports missing roots, missing split directories, empty splits, and discovered
file counts.

The parser also accepts canonical DANDI split directory names:

- `sub-T5-held-in-calib`
- `sub-T5-held-in-minival`
- `sub-T5-held-out-calib`

CLI:

```text
intentfidelity ingest falcon-h2-inventory data --json
```

Experiment runner:

```text
python experiments/01_falcon_h2_ranking_disagreement/run.py data --json
```

Weak target export:

```text
intentfidelity eval falcon-h2-targets data/h2/sub-T5-held-out-calib/example.nwb outputs/targets.jsonl
```

Baseline sanity eval:

```text
intentfidelity eval falcon-h2-baselines data/h2/sub-T5-held-out-calib/example.nwb
```

External prediction eval:

```text
intentfidelity eval falcon-h2-predictions data/h2/sub-T5-held-out-calib/example.nwb outputs/predictions.jsonl
```

Optional public-sample test:

```text
$env:FALCON_H2_SAMPLE_NWB="C:\path\to\sub-T5-held-out-calib_ses-20230417.nwb"
pytest tests/test_falcon_h2_public_sample.py -q
```

The built-in baselines are target-construction sanity checks. Decoder evidence
requires external predictions or later decoder integration.
