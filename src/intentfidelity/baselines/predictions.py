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


def project_prediction_to_target_support(
    prediction: Prediction,
    target: WeakTarget,
    *,
    floor_mass: float = 1e-6,
) -> Prediction:
    if prediction.sample_id != target.sample_id:
        raise ValueError("prediction and target sample_id values must match")
    if floor_mass < 0:
        raise ValueError("floor_mass cannot be negative")

    raw = {
        label: prediction.probabilities.get(label, 0.0) + floor_mass
        for label in target.support
    }
    projected = Prediction(
        sample_id=prediction.sample_id,
        probabilities=raw,
        method_id=prediction.method_id,
        metadata={
            **prediction.metadata,
            "support_projection": "declared_target_support",
            "support_floor_mass": floor_mass,
            "source_support_size": len(prediction.support),
            "target_support_size": len(target.support),
        },
    )
    return projected
