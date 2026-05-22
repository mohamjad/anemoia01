# Report Cards

Pass 1 supports three report-card types:

- `DatasetCard` from resource manifests
- `ClaimCard` for scoped evaluation claims
- `EvalCard` from protocol results

Cards render to JSON or Markdown. Eval cards summarize fidelity to declared weak
target distributions and do not claim access to true intent.

Eval cards preserve `evidence_scope` when the underlying `EvalResult` records
whether a run used sanity baselines or supplied predictions.
