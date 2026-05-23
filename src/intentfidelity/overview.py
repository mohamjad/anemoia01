from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intentfidelity.audit import audit_repository


@dataclass(frozen=True)
class EvidencePath:
    name: str
    evidence_level: str
    status: str
    works_now: tuple[str, ...]
    boundary: str
    next_step: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "evidence_level": self.evidence_level,
            "status": self.status,
            "works_now": list(self.works_now),
            "boundary": self.boundary,
            "next_step": self.next_step,
        }


@dataclass(frozen=True)
class NavigationEntry:
    path: str
    purpose: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "purpose": self.purpose}


@dataclass(frozen=True)
class RepoOverview:
    thesis: str
    current_status: str
    architecture_flow: tuple[str, ...]
    evidence_paths: tuple[EvidencePath, ...]
    quick_commands: tuple[str, ...]
    navigation: tuple[NavigationEntry, ...]
    audit_passed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "thesis": self.thesis,
            "current_status": self.current_status,
            "architecture_flow": list(self.architecture_flow),
            "evidence_paths": [path.to_dict() for path in self.evidence_paths],
            "quick_commands": list(self.quick_commands),
            "navigation": [entry.to_dict() for entry in self.navigation],
            "audit_passed": self.audit_passed,
        }


def build_repo_overview(repo_root: str | Path = ".") -> RepoOverview:
    audit = audit_repository(repo_root)
    return RepoOverview(
        thesis=(
            "Decoder accuracy can be insufficient under weak supervision and "
            "nonstationarity, so adaptive neural interfaces need explicit "
            "evaluation of fidelity to declared weak target proxies."
        ),
        current_status=(
            "Working infrastructure with downloaded-data FALCON H2 evidence; "
            "not comprehensive cross-dataset proof."
        ),
        architecture_flow=(
            "resource manifest",
            "dataset-specific ingestion",
            "weak target construction",
            "prediction import or baseline prediction",
            "protocol scoring",
            "method comparison",
            "report card and validated artifact bundle",
        ),
        evidence_paths=(
            EvidencePath(
                name="FALCON H2",
                evidence_level="downloaded_dataset_evidence",
                status="end-to-end artifact and feature-baseline bundle path",
                works_now=(
                    "NWB/HDF5 inventory",
                    "cue-character weak targets",
                    "baseline predictions",
                    "EvalResult JSON",
                    "eval card and comparison report",
                    "bundle validation with provenance",
                ),
                boundary=(
                    "One dataset family and simple feature-baseline methods; "
                    "not a submitted-decoder benchmark."
                ),
                next_step="Add richer method families under the same bundle contract.",
            ),
            EvidencePath(
                name="bigP3BCI",
                evidence_level="raw_inventory_contract",
                status="raw EDF+ file inventory contract",
                works_now=(
                    "local root resolution",
                    "EDF+ path inventory",
                    "study/session/phase parsing",
                    "structured validation issues",
                ),
                boundary="No EDF+ annotation parsing, target construction, or scoring.",
                next_step="Parse EDF+ annotations into typed P300 selection events.",
            ),
            EvidencePath(
                name="Speech, authorization, and naturalistic paths",
                evidence_level="synthetic_protocol_scaffold",
                status="protocol contracts and report language only",
                works_now=(
                    "typed events and predictions",
                    "JSONL IO",
                    "protocol scoring",
                    "Markdown reports",
                ),
                boundary="No real-data ingestion for these paths yet.",
                next_step="Write dataset-specific raw contracts before scoring.",
            ),
        ),
        quick_commands=(
            "intentfidelity overview",
            "intentfidelity audit repo --json",
            "intentfidelity resources list",
            "intentfidelity ingest falcon-h2-inventory data/external --json",
            "intentfidelity eval falcon-h2-validate-feature-bundle "
            "outputs/falcon-h2-full-feature-bundle",
        ),
        navigation=(
            NavigationEntry("docs/START_HERE.md", "guided first read"),
            NavigationEntry("docs/ARGUMENT.md", "thesis and evidence boundary"),
            NavigationEntry("docs/SYSTEM_MAP.md", "module ownership and data flow"),
            NavigationEntry("docs/EVIDENCE_STATUS.md", "what is demonstrated"),
            NavigationEntry(
                "docs/FALCON_H2_FULL_COVERAGE_RUN.md",
                "strongest current empirical run",
            ),
            NavigationEntry(
                "docs/BIGP3BCI_RAW_CONTRACT.md",
                "first non-FALCON raw contract",
            ),
        ),
        audit_passed=audit.passed,
    )


def render_repo_overview(overview: RepoOverview) -> str:
    lines = [
        "# Intent Fidelity Repo Overview",
        "",
        "## Thesis",
        overview.thesis,
        "",
        "## Current Status",
        overview.current_status,
        "",
        "## Architecture Flow",
    ]
    lines.extend(f"- {step}" for step in overview.architecture_flow)
    lines.extend(["", "## Evidence Paths"])
    for path in overview.evidence_paths:
        lines.extend(
            [
                f"### {path.name}",
                f"- Evidence level: {path.evidence_level}",
                f"- Status: {path.status}",
                f"- Boundary: {path.boundary}",
                f"- Next step: {path.next_step}",
                "- Works now:",
            ]
        )
        lines.extend(f"  - {item}" for item in path.works_now)
    lines.extend(["", "## Quick Commands"])
    lines.extend(f"- `{command}`" for command in overview.quick_commands)
    lines.extend(["", "## Start Here"])
    lines.extend(f"- `{entry.path}` - {entry.purpose}" for entry in overview.navigation)
    lines.extend(["", f"Audit passed: {overview.audit_passed}", ""])
    return "\n".join(lines)
