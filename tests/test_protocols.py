from intentfidelity.metrics import MethodScore, ranking_disagreement
from intentfidelity.protocols import (
    EvalResult,
    ProtocolType,
    authorization_result,
    communication_result,
    few_shot_recalibration_result,
    held_out_session_result,
    naturalistic_weak_label_result,
)


def test_eval_result_round_trips_to_dict() -> None:
    scores = (
        MethodScore("a", conventional_score=0.1, intent_fidelity_score=0.3),
        MethodScore("b", conventional_score=0.2, intent_fidelity_score=0.1),
    )
    result = held_out_session_result(
        "falcon_h2",
        scores,
        split="session_held_out",
    )
    result = EvalResult(
        dataset_id=result.dataset_id,
        protocol=result.protocol,
        method_scores=result.method_scores,
        primary_metric=result.primary_metric,
        ranking_disagreement=ranking_disagreement(scores),
        metadata=result.metadata,
        created_at=result.created_at,
    )

    restored = EvalResult.from_dict(result.to_dict())

    assert restored.dataset_id == "falcon_h2"
    assert restored.protocol == ProtocolType.HELD_OUT_SESSION
    assert restored.ranking_disagreement is not None
    assert restored.metadata == {"split": "session_held_out"}


def test_protocol_factories_encode_required_result_types() -> None:
    scores = (MethodScore("baseline", 0.2, 0.3),)

    assert few_shot_recalibration_result("falcon_h2", scores).protocol == (
        ProtocolType.FEW_SHOT_RECALIBRATION
    )
    assert communication_result("card2024", scores).protocol == ProtocolType.COMMUNICATION
    assert authorization_result("kunz2025", scores).protocol == ProtocolType.AUTHORIZATION
    assert naturalistic_weak_label_result("ajile12", scores).protocol == (
        ProtocolType.NATURALISTIC_WEAK_LABEL
    )

