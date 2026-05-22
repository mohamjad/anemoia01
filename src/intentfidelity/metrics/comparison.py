from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class MethodScore:
    method_id: str
    conventional_score: float
    intent_fidelity_score: float


@dataclass(frozen=True)
class RankingDisagreement:
    conventional_ranking: tuple[str, ...]
    intent_fidelity_ranking: tuple[str, ...]
    kendall_tau_distance: int
    has_disagreement: bool

    @property
    def reversal_rate(self) -> float:
        method_count = len(self.conventional_ranking)
        if method_count < 2:
            return 0.0
        return self.kendall_tau_distance / (method_count * (method_count - 1) / 2)


@dataclass(frozen=True)
class OverAdaptationEvent:
    method_id: str
    conventional_delta: float
    intent_fidelity_delta: float
    reason: str


def ranking_disagreement(scores: Sequence[MethodScore]) -> RankingDisagreement:
    if len(scores) < 2:
        raise ValueError("ranking disagreement requires at least two methods")

    conventional = tuple(
        score.method_id
        for score in sorted(scores, key=lambda item: item.conventional_score)
    )
    intent = tuple(
        score.method_id
        for score in sorted(scores, key=lambda item: item.intent_fidelity_score)
    )
    distance = _kendall_tau_distance(conventional, intent)
    return RankingDisagreement(
        conventional_ranking=conventional,
        intent_fidelity_ranking=intent,
        kendall_tau_distance=distance,
        has_disagreement=distance > 0,
    )


def detect_over_adaptation(
    before: Mapping[str, MethodScore],
    after: Mapping[str, MethodScore],
    *,
    conventional_improvement: float = 0.0,
    intent_fidelity_regression: float = 0.0,
) -> list[OverAdaptationEvent]:
    events: list[OverAdaptationEvent] = []
    for method_id, before_score in before.items():
        after_score = after.get(method_id)
        if after_score is None:
            continue

        conventional_delta = before_score.conventional_score - after_score.conventional_score
        intent_delta = after_score.intent_fidelity_score - before_score.intent_fidelity_score
        if (
            conventional_delta > conventional_improvement
            and intent_delta > intent_fidelity_regression
        ):
            events.append(
                OverAdaptationEvent(
                    method_id=method_id,
                    conventional_delta=conventional_delta,
                    intent_fidelity_delta=intent_delta,
                    reason=(
                        "conventional metric improved while intent-fidelity "
                        "loss worsened"
                    ),
                )
            )
    return events


def expected_calibration_error(
    confidences: Sequence[float],
    correctness: Sequence[float],
    *,
    bins: int = 10,
) -> float:
    if len(confidences) != len(correctness):
        raise ValueError("confidences and correctness must have the same length")
    if not confidences:
        raise ValueError("calibration requires at least one observation")
    if bins <= 0:
        raise ValueError("bins must be positive")

    total_error = 0.0
    n = len(confidences)
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        if index == bins - 1:
            members = [
                i
                for i, confidence in enumerate(confidences)
                if lower <= confidence <= upper
            ]
        else:
            members = [
                i for i, confidence in enumerate(confidences) if lower <= confidence < upper
            ]
        if not members:
            continue
        mean_confidence = sum(confidences[i] for i in members) / len(members)
        mean_correctness = sum(correctness[i] for i in members) / len(members)
        total_error += (len(members) / n) * abs(mean_confidence - mean_correctness)
    return total_error


def _kendall_tau_distance(left: Sequence[str], right: Sequence[str]) -> int:
    if set(left) != set(right):
        raise ValueError("rankings must contain the same method ids")

    right_positions = {method_id: index for index, method_id in enumerate(right)}
    inversions = 0
    for i, left_method in enumerate(left):
        for right_method in left[i + 1 :]:
            if right_positions[left_method] > right_positions[right_method]:
                inversions += 1
    return inversions
