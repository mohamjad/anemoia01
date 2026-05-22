import pytest

from intentfidelity.baselines.predictions import (
    project_prediction_to_target_support,
    proxy_oracle_prediction,
    uniform_prediction,
)
from intentfidelity.labels import Prediction, WeakTarget


def test_uniform_prediction_uses_declared_support() -> None:
    target = WeakTarget("sample", {"a": 1.0, "b": 0.0}, "prompt")

    prediction = uniform_prediction(target)

    assert prediction.probabilities == {"a": 0.5, "b": 0.5}


def test_proxy_oracle_prediction_copies_weak_target_distribution() -> None:
    target = WeakTarget("sample", {"a": 0.8, "b": 0.2}, "prompt")

    prediction = proxy_oracle_prediction(target)

    assert prediction.probabilities == target.probabilities
    assert prediction.metadata["baseline_type"] == "copies_declared_weak_target"


def test_project_prediction_to_target_support_drops_extra_labels() -> None:
    target = WeakTarget("sample", {"a": 1.0, "b": 0.0}, "prompt")
    prediction = Prediction("sample", {"a": 0.8, "b": 0.1, "c": 0.1}, "decoder")

    projected = project_prediction_to_target_support(
        prediction,
        target,
        floor_mass=0.0,
    )

    assert set(projected.support) == {"a", "b"}
    assert projected.probabilities["a"] > projected.probabilities["b"]
    assert projected.metadata["support_projection"] == "declared_target_support"


def test_project_prediction_to_target_support_assigns_floor_to_unseen_labels() -> None:
    target = WeakTarget("sample", {"a": 1.0, "q": 0.0}, "prompt")
    prediction = Prediction("sample", {"a": 1.0}, "decoder")

    projected = project_prediction_to_target_support(
        prediction,
        target,
        floor_mass=0.01,
    )

    assert projected.probabilities["q"] > 0.0
    assert projected.probabilities["a"] > projected.probabilities["q"]


def test_project_prediction_to_target_support_requires_matching_sample_id() -> None:
    target = WeakTarget("target", {"a": 1.0}, "prompt")
    prediction = Prediction("prediction", {"a": 1.0}, "decoder")

    with pytest.raises(ValueError, match="sample_id"):
        project_prediction_to_target_support(prediction, target)
