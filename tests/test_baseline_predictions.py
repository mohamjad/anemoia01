from intentfidelity.baselines.predictions import proxy_oracle_prediction, uniform_prediction
from intentfidelity.labels import WeakTarget


def test_uniform_prediction_uses_declared_support() -> None:
    target = WeakTarget("sample", {"a": 1.0, "b": 0.0}, "prompt")

    prediction = uniform_prediction(target)

    assert prediction.probabilities == {"a": 0.5, "b": 0.5}


def test_proxy_oracle_prediction_copies_weak_target_distribution() -> None:
    target = WeakTarget("sample", {"a": 0.8, "b": 0.2}, "prompt")

    prediction = proxy_oracle_prediction(target)

    assert prediction.probabilities == target.probabilities
    assert prediction.metadata["baseline_type"] == "copies_declared_weak_target"

