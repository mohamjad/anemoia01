from intentfidelity.baselines.examples import LabeledExample
from intentfidelity.baselines.nearest_centroid import fit_nearest_centroid


def test_nearest_centroid_predicts_highest_probability_for_nearest_label() -> None:
    train = (
        LabeledExample("train-a", "a", [0.0], "s1"),
        LabeledExample("train-b", "b", [10.0], "s1"),
    )
    test = (LabeledExample("test-a", "a", [1.0], "s2"),)

    predictions = fit_nearest_centroid(train).predict(test)

    assert predictions[0].probabilities["a"] > predictions[0].probabilities["b"]

