# Evidence Status

This repo should not be described as having proven the broad thesis yet.

The current honest status is:

```text
infrastructure demonstrated on downloaded FALCON H2 data;
method-disagreement thesis not yet established across real datasets.
```

## What Is Demonstrated

FALCON H2 now has three downloaded-data artifact records. bigP3BCI has one
downloaded-data EDF+ bundle validation record with sanity baselines only.

### Sanity Bundle

Recorded in `docs/FALCON_H2_LOCAL_RUN.md`.

This run demonstrates:

- local DANDI NWB ingestion
- inventory generation
- declared cue-character weak target construction
- deterministic sanity-baseline predictions
- `EvalResult` JSON
- eval card and comparison report generation
- bundle manifest and validation
- source-file hashing and provenance
- evaluation diagnostics with per-method proxy metrics and bootstrap ranking
  stability

It does not test meaningful decoder methods.

### Feature-Baseline Bundle

Recorded in `docs/FALCON_H2_METHOD_RUN.md`.

This run demonstrates:

- train/test FALCON H2 feature extraction from downloaded NWB files
- three centroid-style feature baselines
- conventional proxy top-1 error
- intent-fidelity log loss
- method ranking comparison
- validated feature-baseline artifact bundle
- evaluation diagnostics with per-method proxy metrics and bootstrap ranking
  stability

The first subset result was a null ranking-disagreement result:

```text
session_centered_centroid -> whitened_centroid -> identity_centroid
```

Both proxy top-1 error and intent-fidelity log loss produced that ranking.

### Full-Coverage FALCON H2 Bundle

Recorded in `docs/FALCON_H2_FULL_COVERAGE_RUN.md`.

This run uses all 47 NWB assets in the configured DANDI version for the full
sanity bundle, and all held-in calibration plus all held-out calibration files
for the feature-baseline method comparison.

The full feature-baseline run found a ranking disagreement:

```text
proxy top-1 error:        whitened_centroid -> session_centered_centroid -> identity_centroid
intent-fidelity log loss: session_centered_centroid -> whitened_centroid -> identity_centroid
```

This is the current strongest empirical result in the repo.

## What Is Not Demonstrated

Do not claim:

- conventional decoder accuracy fails on FALCON H2
- intent-fidelity metrics reverse method rankings on FALCON H2
- the current baselines represent state-of-the-art decoders
- the current FALCON runs compare submitted decoder systems
- true intent is directly observed
- the broad thesis is proven across datasets

## Dataset Bias Risk

The current empirical path is FALCON-heavy.

That is acceptable for infrastructure sequencing, but it creates a real evidence
risk:

```text
The metric may be useful only for specific proxy structures, datasets, or
protocols.
```

The repo should treat that as an open empirical question, not a settled claim.

Dataset-family status is summarized in `docs/DATASET_LANDSCAPE.md`.

## Non-FALCON Boundary

Card 2024, Willett 2023, Kunz 2025, and AJILE12 currently have protocol
scaffolds, not real-data ingestion paths. bigP3BCI now has raw EDF+ inventory,
fixture-backed event extraction, fixture-backed artifact bundles, and one
single-file downloaded EDF+ bundle validation with deterministic sanity
baselines and evaluation diagnostics. It still has no neural decoder baselines
or real-data method comparison evidence.

Their manifests do not yet encode enough local data contracts to run the same
downloaded-data artifact flow. For bigP3BCI, the next step is broader
downloaded EDF+ coverage plus real EEG/P300 prediction generation before
treating any selection score as method evidence.

## Next Evidence Upgrade

The next stronger empirical result should be one of:

1. A richer FALCON H2 method set where conventional proxy error and
   intent-fidelity log loss can plausibly diverge.
2. A real non-FALCON method path with downloaded data, real predictions, and
   validated artifact bundles.
3. An over-adaptation experiment comparing before/after adaptive updates.

Null results should be recorded. If rankings agree, the repo should say so.
