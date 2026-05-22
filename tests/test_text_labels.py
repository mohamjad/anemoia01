from intentfidelity.labels.text import TextPrediction, TextTarget, normalize_text


def test_normalize_text_lowercases_and_collapses_whitespace() -> None:
    assert normalize_text(" Hello   WORLD ") == "hello world"


def test_text_target_normalizes_text_and_keeps_proxy_source() -> None:
    target = TextTarget("utt-1", "HELLO", "prompted_transcript")

    assert target.text == "hello"
    assert target.source_type == "prompted_transcript"


def test_text_prediction_normalizes_text_and_method() -> None:
    prediction = TextPrediction("utt-1", "Hello", "lm_light")

    assert prediction.text == "hello"
    assert prediction.method_id == "lm_light"

