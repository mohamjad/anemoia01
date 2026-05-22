import pytest

from intentfidelity.metrics import (
    MethodScore,
    detect_over_adaptation,
    expected_calibration_error,
    ranking_disagreement,
)


def test_ranking_disagreement_detects_reversal() -> None:
    scores = [
        MethodScore("accuracy_first", conventional_score=0.1, intent_fidelity_score=0.5),
        MethodScore("proxy_faithful", conventional_score=0.2, intent_fidelity_score=0.1),
    ]

    disagreement = ranking_disagreement(scores)

    assert disagreement.has_disagreement is True
    assert disagreement.conventional_ranking == ("accuracy_first", "proxy_faithful")
    assert disagreement.intent_fidelity_ranking == ("proxy_faithful", "accuracy_first")
    assert disagreement.kendall_tau_distance == 1
    assert disagreement.reversal_rate == pytest.approx(1.0)


def test_detect_over_adaptation_flags_divergent_metric_changes() -> None:
    before = {
        "adaptive": MethodScore("adaptive", 0.4, 0.2),
        "stable": MethodScore("stable", 0.4, 0.2),
    }
    after = {
        "adaptive": MethodScore("adaptive", 0.2, 0.5),
        "stable": MethodScore("stable", 0.5, 0.1),
    }

    events = detect_over_adaptation(before, after)

    assert [event.method_id for event in events] == ["adaptive"]
    assert events[0].conventional_delta == pytest.approx(0.2)
    assert events[0].intent_fidelity_delta == pytest.approx(0.3)


def test_expected_calibration_error_bins_confidence_accuracy_gap() -> None:
    ece = expected_calibration_error(
        confidences=[0.9, 0.8, 0.2, 0.1],
        correctness=[1.0, 1.0, 0.0, 0.0],
        bins=2,
    )

    assert ece == pytest.approx(0.15)
