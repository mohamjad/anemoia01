from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from intentfidelity.metrics.comparison import MethodScore
from intentfidelity.metrics.scoring import DistributionMetric


def method_scores_from_metrics(
    conventional_metrics: Iterable[DistributionMetric],
    intent_fidelity_metrics: Iterable[DistributionMetric],
) -> tuple[MethodScore, ...]:
    conventional = _mean_by_method(conventional_metrics)
    fidelity = _mean_by_method(intent_fidelity_metrics)
    method_ids = sorted(set(conventional) & set(fidelity))
    if not method_ids:
        raise ValueError("no overlapping method ids to score")
    return tuple(
        MethodScore(
            method_id=method_id,
            conventional_score=conventional[method_id],
            intent_fidelity_score=fidelity[method_id],
        )
        for method_id in method_ids
    )


def _mean_by_method(metrics: Iterable[DistributionMetric]) -> dict[str, float]:
    values: dict[str, list[float]] = defaultdict(list)
    for metric in metrics:
        values[metric.method_id].append(metric.value)
    return {
        method_id: sum(method_values) / len(method_values)
        for method_id, method_values in values.items()
    }

