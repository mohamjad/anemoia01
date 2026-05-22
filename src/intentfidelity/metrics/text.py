from __future__ import annotations

from intentfidelity.labels.text import TextPrediction, TextTarget
from intentfidelity.metrics.edit_distance import normalized_edit_distance
from intentfidelity.metrics.scoring import DistributionMetric


def character_error_rate(target: TextTarget, prediction: TextPrediction) -> DistributionMetric:
    _require_same_sample(target, prediction)
    return DistributionMetric(
        sample_id=target.sample_id,
        method_id=prediction.method_id,
        metric="character_error_rate",
        value=normalized_edit_distance(tuple(target.text), tuple(prediction.text)),
    )


def word_error_rate(target: TextTarget, prediction: TextPrediction) -> DistributionMetric:
    _require_same_sample(target, prediction)
    return DistributionMetric(
        sample_id=target.sample_id,
        method_id=prediction.method_id,
        metric="word_error_rate",
        value=normalized_edit_distance(tuple(target.text.split()), tuple(prediction.text.split())),
    )


def _require_same_sample(target: TextTarget, prediction: TextPrediction) -> None:
    if target.sample_id != prediction.sample_id:
        raise ValueError("target and prediction sample_id values differ")

