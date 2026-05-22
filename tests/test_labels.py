import pytest

from intentfidelity.labels import (
    DistributionValidationError,
    Prediction,
    WeakTarget,
    align_probabilities,
    normalize_probabilities,
    prediction_from_dict,
    require_same_support,
    weak_target_from_dict,
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


def test_targets_and_predictions_round_trip_through_dicts() -> None:
    target = WeakTarget("trial-001", {"go": 2, "stop": 1}, "prompt")
    prediction = Prediction("trial-001", {"go": 0.6, "stop": 0.4}, "decoder")

    assert weak_target_from_dict(target.to_dict()) == target
    assert prediction_from_dict(prediction.to_dict()) == prediction
