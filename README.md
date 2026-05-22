# anemoia01

Private implementation engine for intent-fidelity evaluation infrastructure.

Neural interfaces are usually evaluated by how well decoded outputs match
observed targets. That remains necessary, but it is not always sufficient. In
long-running adaptive systems, neural activity, recording conditions, user
strategy, labels, and decoders can all change. When supervision is weak,
delayed, self-paced, or behaviorally confounded, the method that improves
conventional decoder metrics may not be the method that remains most faithful
to the user's task-relevant intended state.

This repo is for building that evaluation layer.

It should become:

- a resource registry for neural-interface datasets
- a weak-target construction system
- an intent-fidelity metric library
- a protocol engine for held-out-session and recalibration evaluations
- a comparison layer for ranking disagreement and over-adaptation
- a reporting layer for dataset cards, claim cards, eval cards, and figures

This is not a BCI decoder. It does not claim to observe true intent. It does not
claim all drift is plasticity.

Start with:

```text
docs/SOURCE_OF_TRUTH.md
docs/IMPLEMENTATION_PLAN.md
docs/NEXT_CHAT_BRIEF.md
docs/ARCHITECTURE.md
```

Useful pass-1 references:

- `docs/RESOURCE_MANIFESTS.md`
- `docs/METRICS.md`
- `docs/PROTOCOLS.md`
- `docs/REPORT_CARDS.md`
- `docs/CLI.md`
- `docs/FALCON_H2_PASS2.md`
- `docs/FALCON_H2_FORMAT.md`
- `docs/PASS3_METHOD_COMPARISON.md`
- `docs/PASS4_COMMUNICATION_AUTHORIZATION.md`
- `docs/PASS5_NATURALISTIC_WEAK_LABELS.md`
