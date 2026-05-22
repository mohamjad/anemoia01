from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

from intentfidelity.labels import Prediction, WeakTarget, align_probabilities


EPSILON = 1e-12


@dataclass(frozen=True)
class DistributionMetric:
    sample_id: str
    method_id: str
    metric: str
    value: float


def log_loss(target: WeakTarget, prediction: Prediction, epsilon: float = EPSILON) -> float:
    target_values, prediction_values, _ = align_probabilities(target, prediction)
    return -sum(
        target_probability * math.log(max(predicted_probability, epsilon))
        for target_probability, predicted_probability in zip(target_values, prediction_values)
    )


def brier_score(target: WeakTarget, prediction: Prediction) -> float:
    target_values, prediction_values, _ = align_probabilities(target, prediction)
    return sum(
        (predicted_probability - target_probability) ** 2
        for target_probability, predicted_probability in zip(target_values, prediction_values)
    )


def kl_divergence(
    target: WeakTarget, prediction: Prediction, epsilon: float = EPSILON
) -> float:
    target_values, prediction_values, _ = align_probabilities(target, prediction)
    total = 0.0
    for target_probability, predicted_probability in zip(target_values, prediction_values):
        if target_probability <= 0:
            continue
        total += target_probability * math.log(
            target_probability / max(predicted_probability, epsilon)
        )
    return total


def jensen_shannon_divergence(
    target: WeakTarget, prediction: Prediction, epsilon: float = EPSILON
) -> float:
    target_values, prediction_values, _ = align_probabilities(target, prediction)
    midpoint = tuple(
        (target_probability + predicted_probability) / 2.0
        for target_probability, predicted_probability in zip(target_values, prediction_values)
    )
    return 0.5 * _kl_values(target_values, midpoint, epsilon) + 0.5 * _kl_values(
        prediction_values, midpoint, epsilon
    )


def intent_fidelity_loss(target: WeakTarget, prediction: Prediction) -> DistributionMetric:
    return DistributionMetric(
        sample_id=target.sample_id,
        method_id=prediction.method_id,
        metric="intent_fidelity_log_loss",
        value=log_loss(target, prediction),
    )


def energy_score(
    target_samples: Sequence[float],
    prediction_samples: Sequence[float],
) -> float:
    if not target_samples:
        raise ValueError("target_samples cannot be empty")
    if not prediction_samples:
        raise ValueError("prediction_samples cannot be empty")

    expected_distance = _mean_abs_difference(prediction_samples, target_samples)
    prediction_spread = _mean_abs_difference(prediction_samples, prediction_samples)
    return expected_distance - 0.5 * prediction_spread


def mean_metric(metrics: Iterable[DistributionMetric]) -> float:
    values = [metric.value for metric in metrics]
    if not values:
        raise ValueError("cannot average an empty metric collection")
    return sum(values) / len(values)


def _kl_values(
    left: Sequence[float], right: Sequence[float], epsilon: float = EPSILON
) -> float:
    total = 0.0
    for left_value, right_value in zip(left, right):
        if left_value <= 0:
            continue
        total += left_value * math.log(left_value / max(right_value, epsilon))
    return total


def _mean_abs_difference(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(abs(a - b) for a in left for b in right) / (len(left) * len(right))

