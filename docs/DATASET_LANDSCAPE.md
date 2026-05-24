# Dataset Landscape

This document keeps dataset diversity separate from empirical proof.

The repo currently understands six dataset paths at different maturity levels.
Only FALCON H2 has downloaded-data method evidence. bigP3BCI now has a raw-file
inventory contract, typed event extraction, fixture-backed bundles, and one
single-file downloaded EDF+ bundle validation, but not neural decoder
prediction generation or real-data method comparison evidence.
The other paths are useful for protocol design and proxy taxonomy, but they are
not real-data evidence yet.

## Summary

| Dataset | Proxy Type | Current Evidence | Main Risk |
| --- | --- | --- | --- |
| FALCON H2 | cue-character handwriting proxy | downloaded-data artifact and feature-baseline bundles | motor cue targets may be cleaner than naturalistic or speech settings |
| Card 2024 | prompted speech/text proxy | synthetic communication scaffold | raw data contract not implemented |
| Willett 2023 | prompted speech/text and language-prior proxy | synthetic communication and language-prior scaffold | language model contribution not yet tied to raw data |
| Kunz 2025 | authorization-state proxy | synthetic authorization scaffold | event extraction is dataset-specific future work |
| AJILE12 | naturalistic behavior proxy | synthetic naturalistic scaffold | behavior may be confounded and weakly timed |
| bigP3BCI | P300 symbol-selection proxy | one downloaded EDF+ bundle validation plus fixture-backed artifact bundle | neural decoder scoring is not implemented |

## What FALCON H2 Teaches

FALCON H2 is the strongest current path because the repo can:

- discover public DANDI assets
- inventory local NWB/HDF5 files
- parse trial cue text and timing
- construct declared cue-character weak targets
- extract simple character-window neural features
- run centroid-style baselines
- compare proxy top-1 error with intent-fidelity log loss
- generate validated artifact bundles with source-file hashes

The full FALCON H2 feature-baseline run now shows a narrow ranking disagreement:

```text
proxy top-1 error:       whitened_centroid -> session_centered_centroid -> identity_centroid
intent-fidelity log loss: session_centered_centroid -> whitened_centroid -> identity_centroid
```

This is real downloaded-data method evidence, but it is still one resource
family and one method family.

## Why Dataset Diversity Still Matters

The thesis is not only about handwriting cue targets. The hard cases include:

- communication outputs where text may be language-model mediated
- authorization states where the proxy is categorical and operational
- naturalistic behavior where labels are delayed and confounded
- P300 selection where event timing and symbol support define the target

Those cases may produce different failure modes. They may also produce null
results. Both outcomes matter.

## Current Boundary

Do not describe the repo as having validated the thesis across diverse datasets.

Accurate statement:

```text
The repo has real downloaded-data FALCON H2 method evidence and executable
synthetic scaffolds for speech, authorization, and naturalistic proxy families.
bigP3BCI also has a downloaded EDF+ bundle validation path, but its current
scores are sanity baselines rather than neural decoder evidence.
```

Inaccurate statement:

```text
The repo has shown across datasets that decoder accuracy fails.
```

## Next Dataset For Diversity

The next real-data path should be chosen by raw-data contract availability.

Recommended order:

1. A speech/text path if trial prompts and decoded text outputs are available in
   a reproducible local format.
2. A P300 selection path if event markers and target symbols can be aligned
   directly.
3. A naturalistic behavior path if behavior labels include timing confidence or
   session-level context.
4. An authorization path if authorized/not-authorized events can be extracted
   without manual annotation.

For any non-FALCON path, the first implementation step is not scoring. It is:

```text
raw local file contract
-> fixture-backed parser
-> typed events or weak targets
-> JSONL IO
-> protocol result
-> validated artifact bundle
```

Until that exists, non-FALCON paths should remain labeled as scaffolds.
bigP3BCI has completed that sequence at fixture scope and on one downloaded EDF+
file for bundle validation: raw local file contract, typed event extraction,
weak targets, sanity predictions, scoring, diagnostics, reports, and a validated
bundle.
