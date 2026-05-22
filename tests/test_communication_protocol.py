from intentfidelity.labels import TextPrediction, TextTarget
from intentfidelity.protocols.communication import communication_eval_result


def test_communication_eval_result_scores_text_predictions() -> None:
    result = communication_eval_result(
        targets=(TextTarget("utt-1", "hello", "prompt"),),
        predictions=(TextPrediction("utt-1", "hallo", "decoder"),),
        dataset_id="card2024",
    )

    assert result.dataset_id == "card2024"
    assert result.protocol.value == "communication"
    assert result.method_scores[0].method_id == "decoder"
    assert result.primary_metric == "character_error_rate"

