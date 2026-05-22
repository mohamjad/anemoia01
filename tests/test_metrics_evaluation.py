from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.metrics import score_predictions


def test_score_predictions_matches_predictions_to_targets() -> None:
    targets = [
        WeakTarget("a", {"yes": 1.0, "no": 0.0}, "prompt"),
        WeakTarget("b", {"yes": 0.0, "no": 1.0}, "prompt"),
    ]
    predictions = [
        Prediction("b", {"yes": 0.25, "no": 0.75}, "decoder"),
        Prediction("a", {"yes": 0.75, "no": 0.25}, "decoder"),
    ]

    metrics = score_predictions(targets, predictions)

    assert [metric.sample_id for metric in metrics] == ["b", "a"]
    assert all(metric.method_id == "decoder" for metric in metrics)

