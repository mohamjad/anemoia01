import pytest

from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.protocols.diagnostics import (
    evaluation_diagnostics,
    render_evaluation_diagnostics_markdown,
)


def test_evaluation_diagnostics_summarize_method_quality() -> None:
    targets = (
        WeakTarget("s0", {"A": 1.0, "B": 0.0}, "prompt"),
        WeakTarget("s1", {"A": 0.0, "B": 1.0}, "prompt"),
    )
    predictions = (
        Prediction("s0", {"A": 0.9, "B": 0.1}, "faithful"),
        Prediction("s1", {"A": 0.1, "B": 0.9}, "faithful"),
        Prediction("s0", {"A": 0.5, "B": 0.5}, "flat"),
        Prediction("s1", {"A": 0.5, "B": 0.5}, "flat"),
    )

    diagnostics = evaluation_diagnostics(
        targets,
        predictions,
        n_resamples=20,
        seed=7,
    )

    assert diagnostics.sample_count == 2
    assert diagnostics.method_count == 2
    assert diagnostics.bootstrap_ranking.top_method_frequencies["faithful"] == 1.0
    assert diagnostics.method_diagnostics[0].method_id == "faithful"
    assert diagnostics.method_diagnostics[0].proxy_top1_accuracy == 1.0
    assert diagnostics.proxy_state_dynamics.transition_count == 1
    assert diagnostics.proxy_state_dynamics.target_top_label_switch_rate == 1.0
    method_dynamics = {
        item.method_id: item for item in diagnostics.proxy_state_dynamics.method_dynamics
    }
    assert method_dynamics["faithful"].mean_prediction_shift > 0.0
    assert (
        method_dynamics["faithful"].mean_shift_tracking_error
        < method_dynamics["flat"].mean_shift_tracking_error
    )


def test_evaluation_diagnostics_requires_complete_prediction_coverage() -> None:
    target = WeakTarget("s0", {"A": 1.0, "B": 0.0}, "prompt")

    with pytest.raises(ValueError, match="missing predictions"):
        evaluation_diagnostics(
            (target,),
            (Prediction("other", {"A": 1.0, "B": 0.0}, "decoder"),),
        )


def test_render_evaluation_diagnostics_markdown_states_scope() -> None:
    target = WeakTarget("s0", {"A": 1.0, "B": 0.0}, "prompt")
    diagnostics = evaluation_diagnostics(
        (target,),
        (Prediction("s0", {"A": 1.0, "B": 0.0}, "decoder"),),
        n_resamples=5,
        seed=0,
    )

    markdown = render_evaluation_diagnostics_markdown(diagnostics)

    assert "Evaluation Diagnostics" in markdown
    assert "Proxy State Dynamics" in markdown
    assert "not directly observed true intent" in markdown


def test_evaluation_diagnostics_describe_static_prediction_streams() -> None:
    targets = (
        WeakTarget("s0", {"A": 1.0, "B": 0.0}, "prompt"),
        WeakTarget("s1", {"A": 0.0, "B": 1.0}, "prompt"),
        WeakTarget("s2", {"A": 1.0, "B": 0.0}, "prompt"),
    )
    predictions = (
        Prediction("s0", {"A": 0.5, "B": 0.5}, "flat"),
        Prediction("s1", {"A": 0.5, "B": 0.5}, "flat"),
        Prediction("s2", {"A": 0.5, "B": 0.5}, "flat"),
    )

    dynamics = evaluation_diagnostics(targets, predictions).proxy_state_dynamics

    assert dynamics.transition_count == 2
    assert dynamics.mean_target_shift > 0.0
    assert dynamics.method_dynamics[0].mean_prediction_shift == 0.0
    assert dynamics.method_dynamics[0].mean_shift_tracking_error > 0.0
    assert "do not reveal latent intent directly" in dynamics.scope
