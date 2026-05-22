import pytest

from intentfidelity.metrics import DistributionMetric
from intentfidelity.metrics.method_scores import method_scores_from_metrics


def test_method_scores_from_metrics_averages_by_method() -> None:
    conventional = [
        DistributionMetric("a", "m1", "decoder_loss", 0.2),
        DistributionMetric("b", "m1", "decoder_loss", 0.4),
    ]
    fidelity = [
        DistributionMetric("a", "m1", "intent_fidelity_loss", 0.1),
        DistributionMetric("b", "m1", "intent_fidelity_loss", 0.3),
    ]

    scores = method_scores_from_metrics(conventional, fidelity)

    assert scores[0].method_id == "m1"
    assert scores[0].conventional_score == pytest.approx(0.3)
    assert scores[0].intent_fidelity_score == pytest.approx(0.2)
