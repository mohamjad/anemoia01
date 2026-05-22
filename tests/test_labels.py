import pytest

from intentfidelity.labels import (
    DistributionValidationError,
    Prediction,
    WeakTarget,
    align_probabilities,
    normalize_probabilities,
    require_same_support,
)


def test_probabilities_are_normalized() -> None:
    normalized = normalize_probabilities({"left": 2, "right": 1})

    assert normalized == {"left": pytest.approx(2 / 3), "right": pytest.approx(1 / 3)}


def test_weak_target_stores_declared_proxy_source() -> None:
    target = WeakTarget(
        sample_id="trial-001",
        probabilities={"accept": 0.75, "reject": 0.25},
        source_type="prompted_target",
        metadata={"session": "s1"},
    )

    assert target.support == ("accept", "reject")
    assert target.source_type == "prompted_target"


def test_prediction_support_must_match_target() -> None:
    target = WeakTarget("trial-001", {"left": 1.0, "right": 0.0}, "prompt")
    prediction = Prediction("trial-001", {"left": 1.0, "up": 0.0}, "decoder")

    with pytest.raises(DistributionValidationError, match="missing labels"):
        require_same_support(target, prediction)


def test_align_probabilities_sorts_labels_for_metrics() -> None:
    target = WeakTarget("trial-001", {"right": 0.25, "left": 0.75}, "prompt")
    prediction = Prediction("trial-001", {"left": 0.5, "right": 0.5}, "decoder")

    target_values, prediction_values, labels = align_probabilities(target, prediction)

    assert labels == ("left", "right")
    assert target_values == (0.75, 0.25)
    assert prediction_values == (0.5, 0.5)

