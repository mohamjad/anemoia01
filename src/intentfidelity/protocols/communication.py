from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from intentfidelity.labels import TextPrediction, TextTarget
from intentfidelity.metrics import MethodScore, character_error_rate, word_error_rate
from intentfidelity.metrics import ranking_disagreement
from intentfidelity.protocols.schemas import EvalResult, ProtocolType


def communication_eval_result(
    targets: Iterable[TextTarget],
    predictions: Iterable[TextPrediction],
    *,
    dataset_id: str,
    metric: str = "character_error_rate",
) -> EvalResult:
    targets_by_id = {target.sample_id: target for target in targets}
    grouped: dict[str, list[float]] = defaultdict(list)
    for prediction in predictions:
        target = targets_by_id.get(prediction.sample_id)
        if target is None:
            raise ValueError(f"missing text target for sample_id: {prediction.sample_id}")
        score = (
            character_error_rate(target, prediction)
            if metric == "character_error_rate"
            else word_error_rate(target, prediction)
        )
        grouped[prediction.method_id].append(score.value)

    if not grouped:
        raise ValueError("communication eval requires at least one prediction")

    method_scores = tuple(
        MethodScore(method_id, sum(values) / len(values), sum(values) / len(values))
        for method_id, values in sorted(grouped.items())
    )
    return EvalResult(
        dataset_id=dataset_id,
        protocol=ProtocolType.COMMUNICATION,
        method_scores=method_scores,
        primary_metric=metric,
        ranking_disagreement=ranking_disagreement(method_scores)
        if len(method_scores) > 1
        else None,
        metadata={"target_type": "text_transcript_proxy"},
    )
