# FALCON H2 Artifact Bundle

The FALCON H2 bundle command creates a local, reproducible evidence artifact
set from either one NWB/HDF5 file or a FALCON H2 data root:

```text
intentfidelity eval falcon-h2-bundle <nwb-or-data-root> <output-dir>
```

Generated files:

- `inventory.json`
- `targets.jsonl`
- `predictions.jsonl`
- `result.json`
- `diagnostics.json`
- `diagnostics.md`
- `eval_card.md`
- `comparison.md`
- `bundle_manifest.json`

The flow is intentionally staged:

```text
source path
-> inventory
-> declared cue-character weak targets
-> deterministic baseline predictions
-> EvalResult JSON
-> diagnostics
-> eval card and comparison report
```

Targets are constructed from declared FALCON H2 cue text. They are intent
proxies, not direct observations of true intent.

## Evidence Scope

The command defaults to:

```text
--evidence-level fixture_evidence
```

Use that default for synthetic NWB/HDF5 fixtures and tests. Fixture bundles
validate ingestion, target construction, scoring, and reporting plumbing; they
are not downloaded FALCON H2 dataset evidence.

For a local run against downloaded FALCON H2 files, pass:

```text
intentfidelity eval falcon-h2-bundle data outputs/falcon-h2-bundle --evidence-level downloaded_dataset_evidence
```

The downloaded-data label only describes local provenance. The resulting scores
still evaluate fidelity to declared weak target distributions.

## Validation

Validate a completed bundle with:

```text
intentfidelity eval falcon-h2-validate-bundle outputs/falcon-h2-bundle
```

The validator checks that expected files exist, the result can be loaded,
target and prediction counts match metadata, evidence level is consistent, the
reports include proxy-scope language, and source files have SHA-256 hashes in
the bundle manifest.

Validation is a contract check. It does not turn fixture evidence into
downloaded dataset evidence.

Feature-baseline method bundles use separate commands:

```text
intentfidelity eval falcon-h2-feature-bundle <train-source> <test-source> <output-dir> --evidence-level downloaded_dataset_evidence
intentfidelity eval falcon-h2-validate-feature-bundle <output-dir>
```

These bundles compare centroid-style methods using proxy top-1 error as the
conventional score and intent-fidelity log loss as the primary metric.

Feature-baseline bundles additionally write:

- `latent_drift.json`
- `latent_drift.md`

Those files contain a neural feature-state probe. The default backend is
deterministic PCA/SVD. An optional CEBRA backend can be selected with
`--latent-backend cebra` after installing `intentfidelity[latent-cebra]`.
Both backends summarize movement in low-dimensional neural features and its
relation to proxy-fidelity loss. Neither claims to recover true intent.

## Provenance

`bundle_manifest.json` and `result.json` metadata record:

- evidence level
- target type
- generated timestamp
- package version
- command used when generated through the CLI
- source file path, split, size, and SHA-256 hash
- target and prediction counts

## Data Root Contract

When the input is a directory, the existing FALCON H2 inventory contract is
used. The root may be the parent directory containing `h2` or the `h2` directory
itself. Required split directories are:

- `held_in_calib` or `sub-T5-held-in-calib`
- `held_out_calib` or `sub-T5-held-out-calib`
- `minival` or `sub-T5-held-in-minival`

When the input is a single file, the split is inferred from the path name and
only that file is included in the bundle.
