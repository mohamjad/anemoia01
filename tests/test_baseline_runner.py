from intentfidelity.baselines.examples import LabeledExample
from intentfidelity.baselines.runner import run_centroid_baseline


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

