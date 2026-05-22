from __future__ import annotations

from typing import Iterable

from intentfidelity.labels import AuthorizationEvent, Prediction
from intentfidelity.labels.authorization import weak_target_from_authorization_event
from intentfidelity.metrics import MethodScore, intent_fidelity_loss, ranking_disagreement
from intentfidelity.protocols.schemas import EvalResult, ProtocolType


def authorization_eval_result(
    events: Iterable[AuthorizationEvent],
    predictions_by_method: dict[str, tuple[Prediction, ...]],
    *,
    dataset_id: str,
) -> EvalResult:
    targets = tuple(weak_target_from_authorization_event(event) for event in events)
    if not targets:
        raise ValueError("authorization eval requires at least one event")
    target_by_id = {target.sample_id: target for target in targets}
    scores = tuple(
        _score_method(method_id, predictions, target_by_id)
        for method_id, predictions in sorted(predictions_by_method.items())
    )
    return EvalResult(
        dataset_id=dataset_id,
        protocol=ProtocolType.AUTHORIZATION,
        method_scores=scores,
        primary_metric="authorization_intent_fidelity_log_loss",
        ranking_disagreement=ranking_disagreement(scores) if len(scores) > 1 else None,
        metadata={"target_type": "authorization_state_proxy"},
    )


def _score_method(method_id: str, predictions, target_by_id) -> MethodScore:
    losses = []
    for prediction in predictions:
        target = target_by_id.get(prediction.sample_id)
        if target is None:
            raise ValueError(f"missing authorization target: {prediction.sample_id}")
        losses.append(intent_fidelity_loss(target, prediction).value)
    mean_loss = sum(losses) / len(losses)
    return MethodScore(method_id, mean_loss, mean_loss)

