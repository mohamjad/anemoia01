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

CLI:

```text
intentfidelity ingest falcon-h2-inventory data --json
```

Experiment runner:

```text
python experiments/01_falcon_h2_ranking_disagreement/run.py data --json
```

This does not yet parse trial contents or produce real-data evidence. It is the
first guarded step toward FALCON H2 weak target construction and held-out-session
ranking disagreement evaluation.

