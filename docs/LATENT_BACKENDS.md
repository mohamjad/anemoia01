# Latent Backends

Latent probes summarize neural feature-state movement inside an artifact bundle.
They are diagnostics, not direct intent readouts and not replacements for
decoder evaluation.

## Default Backend

`pca_svd` is the default backend.

It is deterministic, lightweight, and part of the core test suite:

```text
intentfidelity eval falcon-h2-feature-bundle <train-source> <test-source> <output-dir>
```

The bundle writes:

- `latent_drift.json`
- `latent_drift.md`

These files include latent dimensionality, per-sample latent vectors, centroid
shift, covariance magnitude, step-size dynamics, and correlation between latent
norm and proxy loss when every evaluated sample has targets and predictions.

## Optional CEBRA Backend

`cebra` is optional because it brings a heavier representation-learning runtime.
It is kept outside the core dependency set and outside default CI execution.

Install it explicitly:

```text
pip install 'intentfidelity[latent-cebra]'
```

Run a CEBRA latent probe:

```text
intentfidelity eval falcon-h2-feature-bundle <train-source> <test-source> <output-dir> --latent-backend cebra
```

Useful bounded knobs:

```text
--latent-components 3
--cebra-max-iterations 100
```

The current CEBRA integration is a self-supervised neural feature embedding
probe. It fits on training examples and transforms evaluated examples, then
emits the same `latent_drift` contract as PCA/SVD. It does not add a CEBRA
decoder, does not claim recovery of hidden intent, and does not turn proxy
labels into ground truth.

## Contribution Boundary

Additional latent methods should preserve this contract:

```text
fit examples + evaluated examples + weak targets + predictions
-> LatentDriftReport
-> latent_drift.json
-> latent_drift.md
```

Default tests should not require heavy optional ML stacks. Add contract tests
with fake backends and keep true integration tests skipped or optional unless
the dependency becomes part of the core project.
