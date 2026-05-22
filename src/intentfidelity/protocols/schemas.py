from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from intentfidelity.metrics import MethodScore, RankingDisagreement


class ProtocolType(StrEnum):
    HELD_OUT_SESSION = "held_out_session"
    FEW_SHOT_RECALIBRATION = "few_shot_recalibration"
    COMMUNICATION = "communication"
    AUTHORIZATION = "authorization"
    NATURALISTIC_WEAK_LABEL = "naturalistic_weak_label"


@dataclass(frozen=True)
class EvalResult:
    dataset_id: str
    protocol: ProtocolType
    method_scores: tuple[MethodScore, ...]
    primary_metric: str
    ranking_disagreement: RankingDisagreement | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("dataset_id must be set")
        if not self.method_scores:
            raise ValueError("EvalResult requires at least one method score")
        if not self.primary_metric.strip():
            raise ValueError("primary_metric must be set")
        object.__setattr__(self, "method_scores", tuple(self.method_scores))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "protocol": self.protocol.value,
            "primary_metric": self.primary_metric,
            "created_at": self.created_at,
            "method_scores": [
                {
                    "method_id": score.method_id,
                    "conventional_score": score.conventional_score,
                    "intent_fidelity_score": score.intent_fidelity_score,
                }
                for score in self.method_scores
            ],
            "ranking_disagreement": _ranking_to_dict(self.ranking_disagreement),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> EvalResult:
        method_scores = tuple(
            MethodScore(
                method_id=item["method_id"],
                conventional_score=float(item["conventional_score"]),
                intent_fidelity_score=float(item["intent_fidelity_score"]),
            )
            for item in payload["method_scores"]
        )
        ranking = payload.get("ranking_disagreement")
        return cls(
            dataset_id=payload["dataset_id"],
            protocol=ProtocolType(payload["protocol"]),
            method_scores=method_scores,
            primary_metric=payload["primary_metric"],
            ranking_disagreement=_ranking_from_dict(ranking) if ranking else None,
            metadata=dict(payload.get("metadata", {})),
            created_at=payload.get(
                "created_at", datetime.now(UTC).isoformat(timespec="seconds")
            ),
        )


def held_out_session_result(
    dataset_id: str,
    method_scores: tuple[MethodScore, ...],
    **metadata: Any,
) -> EvalResult:
    return EvalResult(
        dataset_id=dataset_id,
        protocol=ProtocolType.HELD_OUT_SESSION,
        method_scores=method_scores,
        primary_metric="held_out_session_intent_fidelity_loss",
        metadata=metadata,
    )


def few_shot_recalibration_result(
    dataset_id: str,
    method_scores: tuple[MethodScore, ...],
    **metadata: Any,
) -> EvalResult:
    return EvalResult(
        dataset_id=dataset_id,
        protocol=ProtocolType.FEW_SHOT_RECALIBRATION,
        method_scores=method_scores,
        primary_metric="few_shot_recalibration_intent_fidelity_loss",
        metadata=metadata,
    )


def communication_result(
    dataset_id: str,
    method_scores: tuple[MethodScore, ...],
    **metadata: Any,
) -> EvalResult:
    return EvalResult(
        dataset_id=dataset_id,
        protocol=ProtocolType.COMMUNICATION,
        method_scores=method_scores,
        primary_metric="communication_intent_fidelity_loss",
        metadata=metadata,
    )


def authorization_result(
    dataset_id: str,
    method_scores: tuple[MethodScore, ...],
    **metadata: Any,
) -> EvalResult:
    return EvalResult(
        dataset_id=dataset_id,
        protocol=ProtocolType.AUTHORIZATION,
        method_scores=method_scores,
        primary_metric="authorization_intent_fidelity_loss",
        metadata=metadata,
    )


def naturalistic_weak_label_result(
    dataset_id: str,
    method_scores: tuple[MethodScore, ...],
    **metadata: Any,
) -> EvalResult:
    return EvalResult(
        dataset_id=dataset_id,
        protocol=ProtocolType.NATURALISTIC_WEAK_LABEL,
        method_scores=method_scores,
        primary_metric="naturalistic_weak_label_intent_fidelity_loss",
        metadata=metadata,
    )


def _ranking_to_dict(ranking: RankingDisagreement | None) -> dict[str, Any] | None:
    if ranking is None:
        return None
    return {
        "conventional_ranking": list(ranking.conventional_ranking),
        "intent_fidelity_ranking": list(ranking.intent_fidelity_ranking),
        "kendall_tau_distance": ranking.kendall_tau_distance,
        "has_disagreement": ranking.has_disagreement,
    }


def _ranking_from_dict(payload: dict[str, Any]) -> RankingDisagreement:
    return RankingDisagreement(
        conventional_ranking=tuple(payload["conventional_ranking"]),
        intent_fidelity_ranking=tuple(payload["intent_fidelity_ranking"]),
        kendall_tau_distance=int(payload["kendall_tau_distance"]),
        has_disagreement=bool(payload["has_disagreement"]),
    )

