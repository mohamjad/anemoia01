from intentfidelity.labels.text import TextPrediction, TextTarget
from intentfidelity.labels.text_io import (
    read_text_predictions_jsonl,
    read_text_targets_jsonl,
    write_text_predictions_jsonl,
    write_text_targets_jsonl,
)


def test_text_target_jsonl_round_trip(tmp_path) -> None:
    path = tmp_path / "targets.jsonl"
    targets = (TextTarget("utt-1", "HELLO", "prompt"),)

    write_text_targets_jsonl(targets, path)

    assert read_text_targets_jsonl(path) == targets


def test_text_prediction_jsonl_round_trip(tmp_path) -> None:
    path = tmp_path / "predictions.jsonl"
    predictions = (TextPrediction("utt-1", "hello", "decoder"),)

    write_text_predictions_jsonl(predictions, path)

    assert read_text_predictions_jsonl(path) == predictions

