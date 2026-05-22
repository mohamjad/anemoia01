from __future__ import annotations

from collections.abc import Iterable

from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.metrics.scoring import DistributionMetric, intent_fidelity_loss


def score_predictions(
    targets: Iterable[WeakTarget],
    predictions: Iterable[Prediction],
) -> tuple[DistributionMetric, ...]:
    targets_by_sample = {target.sample_id: target for target in targets}
    metrics: list[DistributionMetric] = []
    for prediction in predictions:
        target = targets_by_sample.get(prediction.sample_id)
        if target is None:
            raise KeyError(f"missing weak target for sample_id: {prediction.sample_id}")
        metrics.append(intent_fidelity_loss(target, prediction))
    return tuple(metrics)

