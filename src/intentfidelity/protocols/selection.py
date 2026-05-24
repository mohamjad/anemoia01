from __future__ import annotations

from typing import Any, Iterable, Mapping

from intentfidelity.labels import P300SelectionEvent, Prediction
from intentfidelity.labels.p300 import weak_target_from_p300_event
from intentfidelity.metrics import (
    MethodScore,
    intent_fidelity_loss,
    ranking_disagreement,
    summarize_selection_proxy,
)
from intentfidelity.protocols.schemas import EvalResult, ProtocolType


def selection_eval_result(
    events: Iterable[P300SelectionEvent],
    predictions_by_method: dict[str, tuple[Prediction, ...]],
    *,
    dataset_id: str,
    metadata: Mapping[str, Any] | None = None,
) -> EvalResult:
    event_tuple = tuple(events)
    targets = tuple(weak_target_from_p300_event(event) for event in event_tuple)
    if not targets:
        raise ValueError("selection eval requires at least one event")
    target_by_id = {target.sample_id: target for target in targets}
    target_ids = frozenset(target_by_id)
    scores = tuple(
        _score_method(method_id, predictions, target_by_id, target_ids)
        for method_id, predictions in sorted(predictions_by_method.items())
    )
    summary = summarize_selection_proxy(event_tuple)
    result_metadata = {
        "target_type": "p300_selection_proxy",
        "proxy_summary": summary.to_dict(),
    }
    if metadata is not None:
        result_metadata.update(dict(metadata))
    return EvalResult(
        dataset_id=dataset_id,
        protocol=ProtocolType.SELECTION,
        method_scores=scores,
        primary_metric="selection_intent_fidelity_log_loss",
        ranking_disagreement=ranking_disagreement(scores) if len(scores) > 1 else None,
        metadata=result_metadata,
    )


def _score_method(
    method_id: str,
    predictions: tuple[Prediction, ...],
    target_by_id,
    target_ids: frozenset[str],
) -> MethodScore:
    if not predictions:
        raise ValueError(f"method has no predictions: {method_id}")
    prediction_ids = frozenset(prediction.sample_id for prediction in predictions)
    if prediction_ids != target_ids:
        missing = sorted(target_ids - prediction_ids)
        extra = sorted(prediction_ids - target_ids)
        parts = []
        if missing:
            parts.append(f"missing predictions: {', '.join(missing)}")
        if extra:
            parts.append(f"unknown predictions: {', '.join(extra)}")
        raise ValueError(
            f"incomplete selection predictions for {method_id}: {'; '.join(parts)}"
        )
    losses = []
    for prediction in predictions:
        target = target_by_id.get(prediction.sample_id)
        if target is None:
            raise ValueError(f"missing selection target: {prediction.sample_id}")
        losses.append(intent_fidelity_loss(target, prediction).value)
    mean_loss = sum(losses) / len(losses)
    return MethodScore(method_id, mean_loss, mean_loss)
