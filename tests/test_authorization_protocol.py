from intentfidelity.labels import AuthorizationEvent, AuthorizationState, Prediction
from intentfidelity.protocols.authorization import authorization_eval_result


def test_authorization_eval_result_scores_authorization_predictions() -> None:
    event = AuthorizationEvent("sample-1", AuthorizationState.AUTHORIZED)
    prediction = Prediction(
        "sample-1",
        {"authorized": 0.9, "not_authorized": 0.1},
        "auth_detector",
    )

    result = authorization_eval_result(
        (event,),
        {"auth_detector": (prediction,)},
        dataset_id="kunz2025",
    )

    assert result.protocol.value == "authorization"
    assert result.method_scores[0].method_id == "auth_detector"

