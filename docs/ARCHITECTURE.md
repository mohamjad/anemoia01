# Architecture

`intentfidelity` is organized around explicit evaluation artifacts:

- resource manifests define available datasets and proxy sources
- weak targets encode declared target distributions
- predictions encode method output distributions on the same support
- metrics score fidelity to the declared weak target
- protocols package method scores into eval results
- reports render dataset, claim, and eval cards
- the CLI exposes registry, summary, report, and figure entry points

Pass 1 intentionally stops before real dataset ingestion. Synthetic checks are
only used to validate metric and reporting plumbing.

