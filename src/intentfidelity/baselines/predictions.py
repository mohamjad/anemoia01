from __future__ import annotations

from intentfidelity.labels import Prediction, WeakTarget


def uniform_prediction(target: WeakTarget, method_id: str = "uniform_prior") -> Prediction:
    support = target.support
    mass = 1.0 / len(support)
    return Prediction(
        sample_id=target.sample_id,
        probabilities={label: mass for label in support},
        method_id=method_id,
        metadata={"baseline_type": "uniform_over_declared_support"},
    )


def proxy_oracle_prediction(
    target: WeakTarget, method_id: str = "proxy_oracle"
) -> Prediction:
    return Prediction(
        sample_id=target.sample_id,
        probabilities=dict(target.probabilities),
        method_id=method_id,
        metadata={"baseline_type": "copies_declared_weak_target"},
    )

