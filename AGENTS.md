# AGENTS.md

This repo is being built as intent-fidelity evaluation infrastructure for
adaptive neural interfaces.

Follow `docs/SOURCE_OF_TRUTH.md` as the product and research contract.

## Rules

- Keep claims narrower than the implementation.
- Do not center "meaning gap", "plasticity signal", or "NeuroDrift" framing.
- Do not claim direct access to true intent.
- Use "weak target distribution", "intent proxy", "intent fidelity",
  "ranking disagreement", and "over-adaptation".
- Add tests with implementation.
- Keep commits small and buildable.
- Prefer typed, explicit modules over clever abstractions.
- Preserve compatibility with useful `neurodrift-lab` ideas only when they serve
  the new infrastructure direction.

## Immediate Build Direction

First pass:

1. Create `src/intentfidelity/`.
2. Add resource manifests and validation.
3. Add weak target and prediction schemas.
4. Add proper scoring rules and intent-fidelity loss.
5. Add ranking disagreement and over-adaptation detection.
6. Add protocol result schemas.
7. Add report cards.
8. Add CLI for resources, metrics, and reports.
9. Add tests.

Synthetic experiments are sanity checks only. Real-data evidence comes later.
