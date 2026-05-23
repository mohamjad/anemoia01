# Architecture

`intentfidelity` is organized around explicit evaluation artifacts:

- resource manifests define available datasets and proxy sources
- dataset-specific raw contracts make local data expectations inspectable
- weak targets encode declared target distributions
- predictions encode method output distributions on the same support
- metrics score fidelity to the declared weak target
- protocols package method scores into eval results
- reports render dataset, claim, and eval cards
- audit and overview commands keep repo state navigable and bounded
- the CLI exposes registry, summary, report, and figure entry points

For module ownership and extension boundaries, see `docs/SYSTEM_MAP.md`.

The architecture now has three maturity layers:

1. Synthetic protocol scaffolds validate schema, scoring, and report contracts.
2. Raw data contracts define local dataset expectations before target parsing.
3. Downloaded-data artifact bundles record provenance, targets, predictions,
   scores, reports, and validation state.

Pass 2 adds the first FALCON H2 data path: DANDI asset discovery, NWB/HDF5
inventory, trial cue extraction, character-level weak targets, and held-out
evaluation against either built-in sanity baselines or supplied predictions.

Pass 3 adds the method-comparison layer: typed feature examples, baseline
feature transforms, centroid prediction baselines, comparison reports, and
ranking reversal tables.

Pass 4 adds the first speech-path and authorization protocol scaffolds:
transcript targets, text predictions, language-prior attribution, authorization
events, and dedicated report renderers. These modules keep proxy construction,
metrics, protocols, and reports separate so real-data ingestion can attach to
the same contracts later.

Pass 5 adds the naturalistic weak-label path: behavior proxy events, event IO,
proxy ambiguity summaries, an AJILE12 scaffold runner, and a naturalistic report
renderer.

Pass 6 adds the selection weak-target path for bigP3BCI-style P300 symbol
selection: event schemas, event IO, selection proxy summaries, a selection
protocol, a report renderer, and an executable scaffold runner.

The current production-quality path is FALCON H2. It has downloaded-data bundle
generation and validation. bigP3BCI has the first non-FALCON raw EDF+ inventory
contract, but no annotation parser or scoring path yet.

For first-run navigation, use:

```text
intentfidelity overview
intentfidelity audit repo --json
```
