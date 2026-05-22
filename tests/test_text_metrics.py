import pytest

from intentfidelity.labels.text import TextPrediction, TextTarget
from intentfidelity.metrics.text import character_error_rate, word_error_rate


def test_character_error_rate_scores_transcript_prediction() -> None:
    target = TextTarget("utt-1", "abcd", "prompt")
    prediction = TextPrediction("utt-1", "abxd", "decoder")

    assert character_error_rate(target, prediction).value == pytest.approx(0.25)


def test_word_error_rate_scores_word_sequence() -> None:
    target = TextTarget("utt-1", "hello world", "prompt")
    prediction = TextPrediction("utt-1", "hello there", "decoder")

    assert word_error_rate(target, prediction).value == pytest.approx(0.5)

