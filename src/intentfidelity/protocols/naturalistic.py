from __future__ import annotations

from typing import Iterable

from intentfidelity.labels import NaturalisticEvent, Prediction
from intentfidelity.labels.naturalistic import weak_target_from_naturalistic_event
from intentfidelity.metrics import (
    MethodScore,
    intent_fidelity_loss,
    ranking_disagreement,
    summarize_naturalistic_proxy,
)
from intentfidelity.protocols.schemas import EvalResult, ProtocolType


def naturalistic_eval_result(
    events: Iterable[NaturalisticEvent],
    predictions_by_method: dict[str, tuple[Prediction, ...]],
    *,
    dataset_id: str,
) -> EvalResult:
    event_tuple = tuple(events)
    targets = tuple(weak_target_from_naturalistic_event(event) for event in event_tuple)
    if not targets:
        raise ValueError("naturalistic eval requires at least one event")
    target_by_id = {target.sample_id: target for target in targets}
    scores = tuple(
        _score_method(method_id, predictions, target_by_id)
        for method_id, predictions in sorted(predictions_by_method.items())
    )
    proxy_summary = summarize_naturalistic_proxy(event_tuple)
    return EvalResult(
        dataset_id=dataset_id,
        protocol=ProtocolType.NATURALISTIC_WEAK_LABEL,
        method_scores=scores,
        primary_metric="naturalistic_intent_fidelity_log_loss",
        ranking_disagreement=ranking_disagreement(scores) if len(scores) > 1 else None,
        metadata={
            "target_type": "naturalistic_behavior_proxy",
            "proxy_summary": proxy_summary.to_dict(),
        },
    )


def _score_method(method_id: str, predictions, target_by_id) -> MethodScore:
    if not predictions:
        raise ValueError(f"method has no predictions: {method_id}")
    losses = []
    for prediction in predictions:
        target = target_by_id.get(prediction.sample_id)
        if target is None:
            raise ValueError(f"missing naturalistic target: {prediction.sample_id}")
        losses.append(intent_fidelity_loss(target, prediction).value)
    mean_loss = sum(losses) / len(losses)
    return MethodScore(method_id, mean_loss, mean_loss)
