from intentfidelity.labels import P300SelectionEvent, Prediction
from intentfidelity.protocols.selection import selection_eval_result


def test_selection_eval_result_scores_predictions_and_summary() -> None:
    event = P300SelectionEvent("s0", "A", ("A", "B"), 0.9, "A", "session-1")
    prediction = Prediction("s0", {"A": 0.8, "B": 0.2}, "decoder")

    result = selection_eval_result(
        (event,),
        {"decoder": (prediction,)},
        dataset_id="bigp3bci",
    )

    assert result.protocol.value == "selection"
    assert result.method_scores[0].method_id == "decoder"
    assert result.metadata["proxy_summary"]["event_count"] == 1
    assert result.metadata["proxy_summary"]["observed_selection_accuracy"] == 1.0


def test_selection_eval_result_reports_ranking_disagreement() -> None:
    event = P300SelectionEvent("s0", "A", ("A", "B"), 0.9)

    result = selection_eval_result(
        (event,),
        {
            "faithful": (Prediction("s0", {"A": 0.9, "B": 0.1}, "faithful"),),
            "flat": (Prediction("s0", {"A": 0.5, "B": 0.5}, "flat"),),
        },
        dataset_id="bigp3bci",
    )

    assert result.ranking_disagreement is not None
