from __future__ import annotations

from dataclasses import dataclass

from intentfidelity.metrics import (
    OverAdaptationEvent,
    RankingDisagreement,
    detect_over_adaptation,
    ranking_disagreement,
)
from intentfidelity.protocols import EvalResult


@dataclass(frozen=True)
class MethodComparisonReport:
    dataset_id: str
    protocol: str
    ranking: RankingDisagreement
    over_adaptation_events: tuple[OverAdaptationEvent, ...]


def compare_eval_results(
    before: EvalResult,
    after: EvalResult | None = None,
) -> MethodComparisonReport:
    ranking = ranking_disagreement(before.method_scores)
    events: tuple[OverAdaptationEvent, ...] = ()
    if after is not None:
        before_scores = {score.method_id: score for score in before.method_scores}
        after_scores = {score.method_id: score for score in after.method_scores}
        events = tuple(detect_over_adaptation(before_scores, after_scores))
    return MethodComparisonReport(
        dataset_id=before.dataset_id,
        protocol=before.protocol.value,
        ranking=ranking,
        over_adaptation_events=events,
    )

