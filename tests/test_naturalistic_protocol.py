from intentfidelity.labels import NaturalisticEvent, Prediction
from intentfidelity.protocols.naturalistic import naturalistic_eval_result


def test_naturalistic_eval_result_scores_predictions_and_summary() -> None:
    event = NaturalisticEvent("s0", "reach", ("reach", "rest"), 0.8, "session-1")
    prediction = Prediction("s0", {"reach": 0.7, "rest": 0.3}, "decoder")

    result = naturalistic_eval_result(
        (event,),
        {"decoder": (prediction,)},
        dataset_id="ajile12",
    )

    assert result.protocol.value == "naturalistic_weak_label"
    assert result.method_scores[0].method_id == "decoder"
    assert result.metadata["proxy_summary"]["event_count"] == 1
    assert result.metadata["proxy_summary"]["session_count"] == 1


def test_naturalistic_eval_result_reports_ranking_disagreement() -> None:
    event = NaturalisticEvent("s0", "reach", ("reach", "rest"), 0.8)

    result = naturalistic_eval_result(
        (event,),
        {
            "faithful": (Prediction("s0", {"reach": 0.8, "rest": 0.2}, "faithful"),),
            "blurred": (Prediction("s0", {"reach": 0.5, "rest": 0.5}, "blurred"),),
        },
        dataset_id="ajile12",
    )

    assert result.ranking_disagreement is not None
