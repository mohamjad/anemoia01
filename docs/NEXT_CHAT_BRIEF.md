# Next Chat Brief

Build `anemoia01` as a clean infrastructure repo for intent-fidelity evaluation.

Do not transform `neurodrift-lab` in place.

Use `neurodrift-lab` only as reference material for:

- weak target distributions
- scoring utilities
- ranking disagreement
- over-adaptation detection
- synthetic sanity checks
- CLI/test discipline

Current status:

```text
Pass 4 added communication, language-prior attribution, and authorization
protocol scaffolds for the speech-path resources.
```

Immediate task:

```text
Implement pass 1:
architecture, docs, schemas, metrics, resource manifests, CLI, tests.
```

Start with small commits:

1. Python package scaffold.
2. Resource manifest schema.
3. Initial dataset manifests.
4. Weak target schemas.
5. Proper scoring metrics.
6. Intent-fidelity metrics.
7. Ranking disagreement and over-adaptation.
8. Protocol result schemas.
9. Report cards.
10. CLI.
11. Tests.

Do not backdate commits or fabricate history.

Keep claims narrow:

```text
decoder accuracy can be insufficient under weak supervision and nonstationarity
```

The first real-data target after pass 1 is FALCON H2.
