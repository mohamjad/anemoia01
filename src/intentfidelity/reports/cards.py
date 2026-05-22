from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Protocol

from intentfidelity.protocols import EvalResult
from intentfidelity.resources import ResourceManifest


class RenderableCard(Protocol):
    def to_dict(self) -> dict[str, Any]: ...


@dataclass(frozen=True)
class DatasetCard:
    dataset_id: str
    title: str
    domain: str
    status: str
    access: str
    weak_proxy_sources: tuple[str, ...]
    known_limitations: tuple[str, ...]
    first_pass_role: str

    @classmethod
    def from_manifest(cls, manifest: ResourceManifest) -> DatasetCard:
        return cls(
            dataset_id=manifest.dataset_id,
            title=manifest.title,
            domain=manifest.domain,
            status=manifest.status,
            access=manifest.access,
            weak_proxy_sources=manifest.weak_proxy_sources,
            known_limitations=manifest.known_limitations,
            first_pass_role=manifest.first_pass_role,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "dataset_card",
            "dataset_id": self.dataset_id,
            "title": self.title,
            "domain": self.domain,
            "status": self.status,
            "access": self.access,
            "weak_proxy_sources": list(self.weak_proxy_sources),
            "known_limitations": list(self.known_limitations),
            "first_pass_role": self.first_pass_role,
        }


@dataclass(frozen=True)
class ClaimCard:
    claim_id: str
    claim: str
    scope: str
    evidence_status: str
    caveats: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "claim_card",
            "claim_id": self.claim_id,
            "claim": self.claim,
            "scope": self.scope,
            "evidence_status": self.evidence_status,
            "caveats": list(self.caveats),
        }


@dataclass(frozen=True)
class EvalCard:
    dataset_id: str
    protocol: str
    primary_metric: str
    method_count: int
    ranking_disagreement: bool | None
    summary: str
    evidence_scope: str | None = None

    @classmethod
    def from_result(cls, result: EvalResult) -> EvalCard:
        disagreement = (
            result.ranking_disagreement.has_disagreement
            if result.ranking_disagreement is not None
            else None
        )
        return cls(
            dataset_id=result.dataset_id,
            protocol=result.protocol.value,
            primary_metric=result.primary_metric,
            method_count=len(result.method_scores),
            ranking_disagreement=disagreement,
            summary=(
                "Evaluation card summarizes fidelity to declared weak target "
                "distributions, not direct access to intent."
            ),
            evidence_scope=result.metadata.get("baseline_scope"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "eval_card",
            "dataset_id": self.dataset_id,
            "protocol": self.protocol,
            "primary_metric": self.primary_metric,
            "method_count": self.method_count,
            "ranking_disagreement": self.ranking_disagreement,
            "summary": self.summary,
            "evidence_scope": self.evidence_scope,
        }


def render_json(card: RenderableCard) -> str:
    return json.dumps(card.to_dict(), indent=2, sort_keys=True)


def render_markdown(card: RenderableCard) -> str:
    payload = card.to_dict()
    title = payload.get("title") or payload.get("claim_id") or payload.get("type")
    lines = [f"# {title}", ""]
    for key, value in payload.items():
        if key == "title":
            continue
        label = key.replace("_", " ").title()
        if isinstance(value, list):
            lines.append(f"## {label}")
            lines.extend(f"- {item}" for item in value)
            lines.append("")
        else:
            lines.append(f"**{label}:** {value}")
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def default_claim_card() -> ClaimCard:
    return ClaimCard(
        claim_id="decoder_accuracy_insufficient_under_weak_supervision",
        claim=(
            "Decoder accuracy can be insufficient under weak supervision and "
            "neural nonstationarity."
        ),
        scope=(
            "This is an evaluation-infrastructure claim about disagreement "
            "between conventional metrics and intent-fidelity metrics."
        ),
        evidence_status=(
            "architecture, fixture-backed FALCON H2 plumbing, and synthetic "
            "protocol scaffolds"
        ),
        caveats=(
            "No direct access to true intent is claimed.",
            "Real-data evidence is planned after resource ingestion.",
        ),
    )
