import math

import pytest

from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.metrics import (
    brier_score,
    energy_score,
    intent_fidelity_loss,
    jensen_shannon_divergence,
    kl_divergence,
    log_loss,
)


def test_log_loss_rewards_probability_on_declared_target() -> None:
    target = WeakTarget("trial-001", {"yes": 1.0, "no": 0.0}, "prompt")
    good = Prediction("trial-001", {"yes": 0.9, "no": 0.1}, "good")
    bad = Prediction("trial-001", {"yes": 0.1, "no": 0.9}, "bad")

    assert log_loss(target, good) < log_loss(target, bad)


def test_brier_score_matches_squared_distribution_error() -> None:
    target = WeakTarget("trial-001", {"a": 0.75, "b": 0.25}, "prompt")
    prediction = Prediction("trial-001", {"a": 0.5, "b": 0.5}, "decoder")

    assert brier_score(target, prediction) == pytest.approx(0.125)


def test_kl_and_js_are_zero_for_equal_distributions() -> None:
    target = WeakTarget("trial-001", {"a": 0.6, "b": 0.4}, "prompt")
    prediction = Prediction("trial-001", {"a": 0.6, "b": 0.4}, "decoder")

    assert kl_divergence(target, prediction) == pytest.approx(0.0)
    assert jensen_shannon_divergence(target, prediction) == pytest.approx(0.0)


def test_intent_fidelity_loss_is_named_log_loss_metric() -> None:
    target = WeakTarget("trial-001", {"a": 1.0, "b": 0.0}, "prompt")
    prediction = Prediction("trial-001", {"a": 0.5, "b": 0.5}, "decoder")

    metric = intent_fidelity_loss(target, prediction)

    assert metric.metric == "intent_fidelity_log_loss"
    assert metric.value == pytest.approx(math.log(2))


def test_energy_score_supports_continuous_sanity_checks() -> None:
    assert energy_score([1.0], [0.0, 2.0]) == pytest.approx(0.5)

