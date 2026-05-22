from intentfidelity.baselines.examples import LabeledExample
from intentfidelity.baselines.runner import (
    run_centroid_baseline,
    run_default_centroid_baselines,
)


def test_run_centroid_baseline_returns_predictions_for_test_set() -> None:
    train = (
        LabeledExample("train-a", "a", [0.0], "s1"),
        LabeledExample("train-b", "b", [10.0], "s1"),
    )
    test = (LabeledExample("test-a", "a", [1.0], "s2"),)

    run = run_centroid_baseline(train, test)

    assert run.train_count == 2
    assert run.test_count == 1
    assert run.predictions[0].method_id == "identity_centroid"


def test_run_default_centroid_baselines_returns_method_suite() -> None:
    train = (
        LabeledExample("train-a", "a", [0.0], "s1"),
        LabeledExample("train-b", "b", [10.0], "s1"),
    )
    test = (LabeledExample("test-a", "a", [1.0], "s2"),)

    runs = run_default_centroid_baselines(train, test)

    assert [run.method_id for run in runs] == [
        "identity_centroid",
        "session_centered_centroid",
        "whitened_centroid",
    ]
