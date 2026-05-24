# Report Cards

The reporting layer supports three general card types:

- `DatasetCard` from resource manifests
- `ClaimCard` for scoped evaluation claims
- `EvalCard` from protocol results

Cards render to JSON or Markdown. Eval cards summarize fidelity to declared weak
target distributions and do not claim access to true intent.

Eval cards preserve `evidence_scope` when the underlying `EvalResult` records
whether a run used sanity baselines or supplied predictions.

FALCON H2 and bigP3BCI artifact bundles write `eval_card.md`, `comparison.md`,
`diagnostics.json`, and `diagnostics.md`. Reports state that targets are
declared weak target proxies and do not imply direct access to true intent.
Fixture bundle cards also state that fixture results are not downloaded dataset
evidence.

Pass 4 adds focused Markdown renderers for:

- communication evaluation results
- language-prior attribution summaries
- authorization evaluation results
- naturalistic weak-label evaluation results
- selection evaluation results

These renderers keep the same constraint as eval cards: they describe fidelity
to declared proxies, not direct measurement of true intent.
