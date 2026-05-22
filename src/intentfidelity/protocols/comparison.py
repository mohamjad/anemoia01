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

    def to_dict(self) -> dict:
        return {
            "dataset_id": self.dataset_id,
            "protocol": self.protocol,
            "ranking": {
                "conventional_ranking": list(self.ranking.conventional_ranking),
                "intent_fidelity_ranking": list(self.ranking.intent_fidelity_ranking),
                "kendall_tau_distance": self.ranking.kendall_tau_distance,
                "has_disagreement": self.ranking.has_disagreement,
            },
            "over_adaptation_events": [
                {
                    "method_id": event.method_id,
                    "conventional_delta": event.conventional_delta,
                    "intent_fidelity_delta": event.intent_fidelity_delta,
                    "reason": event.reason,
                }
                for event in self.over_adaptation_events
            ],
        }


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
