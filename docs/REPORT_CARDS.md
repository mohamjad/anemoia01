# Report Cards

Pass 1 supports three report-card types:

- `DatasetCard` from resource manifests
- `ClaimCard` for scoped evaluation claims
- `EvalCard` from protocol results

Cards render to JSON or Markdown. Eval cards summarize fidelity to declared weak
target distributions and do not claim access to true intent.

Eval cards preserve `evidence_scope` when the underlying `EvalResult` records
whether a run used sanity baselines or supplied predictions.

Pass 4 adds focused Markdown renderers for:

- communication evaluation results
- language-prior attribution summaries
- authorization evaluation results

These renderers keep the same constraint as eval cards: they describe fidelity
to declared proxies, not direct measurement of true intent.
