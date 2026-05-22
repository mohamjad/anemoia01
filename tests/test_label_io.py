from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.labels.io import (
    read_predictions_jsonl,
    read_weak_targets_jsonl,
    write_predictions_jsonl,
    write_weak_targets_jsonl,
)


def test_weak_targets_jsonl_round_trip(tmp_path) -> None:
    path = tmp_path / "targets.jsonl"
    targets = (WeakTarget("s1", {"a": 1.0, "b": 0.0}, "prompt"),)

    write_weak_targets_jsonl(targets, path)

    assert read_weak_targets_jsonl(path) == targets


def test_predictions_jsonl_round_trip(tmp_path) -> None:
    path = tmp_path / "predictions.jsonl"
    predictions = (Prediction("s1", {"a": 0.6, "b": 0.4}, "decoder"),)

    write_predictions_jsonl(predictions, path)

    assert read_predictions_jsonl(path) == predictions

