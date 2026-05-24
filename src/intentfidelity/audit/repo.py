from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intentfidelity.resources import load_manifests


REQUIRED_DOCS: tuple[str, ...] = (
    "AGENTS.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "docs/START_HERE.md",
    "docs/SOURCE_OF_TRUTH.md",
    "docs/ARGUMENT.md",
    "docs/EVIDENCE_STATUS.md",
    "docs/DATASET_LANDSCAPE.md",
    "docs/BIGP3BCI_RAW_CONTRACT.md",
    "docs/SYSTEM_MAP.md",
    "docs/RELIABILITY.md",
    "docs/HANDOFF.md",
    "docs/NEXT_STEPS.md",
    "docs/NEXT_CHAT_BRIEF.md",
)

DB_STATE_SUFFIXES: tuple[str, ...] = (
    ".db",
    ".sqlite",
    ".sqlite3",
    ".duckdb",
    ".parquet",
)

SCAN_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "data",
        "outputs",
        "venv",
    }
)


@dataclass(frozen=True)
class AuditCheck:
    name: str
    passed: bool
    message: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
        }


@dataclass(frozen=True)
class RepoAuditReport:
    repo_root: Path
    checks: tuple[AuditCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_root": str(self.repo_root),
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.checks],
        }


def audit_repository(repo_root: str | Path) -> RepoAuditReport:
    root = Path(repo_root)
    checks = (
        _required_docs_check(root),
        _ci_workflow_check(root),
        _resource_manifest_check(root),
        _evidence_boundary_check(root),
        _db_state_check(root),
    )
    return RepoAuditReport(root, checks)


def _required_docs_check(root: Path) -> AuditCheck:
    missing = [
        relative for relative in REQUIRED_DOCS if not (root / relative).is_file()
    ]
    return AuditCheck(
        name="required_docs",
        passed=not missing,
        message=(
            "All authoritative docs are present."
            if not missing
            else "Required authoritative docs are missing."
        ),
        details={"missing": missing, "required": list(REQUIRED_DOCS)},
    )


def _resource_manifest_check(root: Path) -> AuditCheck:
    manifest_dir = root / "src" / "intentfidelity" / "resources" / "manifests"
    try:
        manifests = load_manifests(manifest_dir)
    except Exception as exc:
        return AuditCheck(
            name="resource_manifests",
            passed=False,
            message="Resource manifests failed to load.",
            details={"error": f"{type(exc).__name__}: {exc}"},
        )

    by_id = {manifest.dataset_id: manifest for manifest in manifests}

    expected_stages = {
        "falcon_h2": "full downloaded-data artifact and feature-baseline bundle path",
        "bigp3bci": "fixture-backed artifact bundle path",
    }
    stage_mismatches = {
        dataset_id: by_id[dataset_id].metadata.get("evidence_stage")
        for dataset_id, expected in expected_stages.items()
        if dataset_id not in by_id
        or by_id[dataset_id].metadata.get("evidence_stage") != expected
    }

    return AuditCheck(
        name="resource_manifests",
        passed=not stage_mismatches,
        message=(
            "Resource manifests load and key evidence stages match the docs."
            if not stage_mismatches
            else "Resource manifest evidence stages do not match expected state."
        ),
        details={
            "count": len(manifests),
            "dataset_ids": [manifest.dataset_id for manifest in manifests],
            "stage_mismatches": stage_mismatches,
        },
    )


def _ci_workflow_check(root: Path) -> AuditCheck:
    workflow = root / ".github" / "workflows" / "tests.yml"
    if not workflow.is_file():
        return AuditCheck(
            name="ci_workflow",
            passed=False,
            message="CI workflow is missing.",
            details={"path": str(workflow.relative_to(root))},
        )

    text = workflow.read_text(encoding="utf-8")
    required_fragments = (
        "python -m pip install -e \".[dev]\"",
        "intentfidelity audit repo --json",
        "pytest -q",
    )
    missing = [fragment for fragment in required_fragments if fragment not in text]
    return AuditCheck(
        name="ci_workflow",
        passed=not missing,
        message=(
            "CI workflow installs the package and runs audit plus tests."
            if not missing
            else "CI workflow is missing required public-readiness gates."
        ),
        details={
            "path": str(workflow.relative_to(root)),
            "missing_fragments": missing,
        },
    )


def _evidence_boundary_check(root: Path) -> AuditCheck:
    evidence_status = _read_text(root / "docs" / "EVIDENCE_STATUS.md")
    dataset_landscape = _read_text(root / "docs" / "DATASET_LANDSCAPE.md")
    argument = _read_text(root / "docs" / "ARGUMENT.md")

    required_phrases = {
        "evidence_status": (
            "should not be described as having proven the broad thesis",
            "bigP3BCI now has raw EDF+ inventory, fixture-backed event extraction, and fixture-backed artifact bundles",
            "still no downloaded-data event validation",
        ),
        "dataset_landscape": (
            "Only FALCON H2 has downloaded-data artifact bundles",
            "not downloaded-data scoring evidence",
        ),
        "argument": (
            "does not observe true intent directly",
            "one dataset family and one baseline family",
        ),
    }
    sources = {
        "evidence_status": _normalize_text(evidence_status),
        "dataset_landscape": _normalize_text(dataset_landscape),
        "argument": _normalize_text(argument),
    }
    missing = {
        source_name: [
            phrase for phrase in phrases if phrase not in sources[source_name]
        ]
        for source_name, phrases in required_phrases.items()
    }
    missing = {
        source_name: phrases for source_name, phrases in missing.items() if phrases
    }

    return AuditCheck(
        name="evidence_boundaries",
        passed=not missing,
        message=(
            "Evidence boundary docs include the required scope limitations."
            if not missing
            else "Evidence boundary docs are missing required scope language."
        ),
        details={"missing_phrases": missing},
    )


def _db_state_check(root: Path) -> AuditCheck:
    matches = [
        str(path.relative_to(root))
        for path in _iter_scanned_files(root)
        if path.suffix.lower() in DB_STATE_SUFFIXES
    ]
    return AuditCheck(
        name="db_state_files",
        passed=not matches,
        message=(
            "No repository DB/state files were found in the source tree."
            if not matches
            else "Repository DB/state files were found in the source tree."
        ),
        details={
            "matches": matches,
            "suffixes": list(DB_STATE_SUFFIXES),
            "excluded_dirs": sorted(SCAN_EXCLUDED_DIRS),
        },
    )


def _iter_scanned_files(root: Path) -> Iterator[Path]:
    for path in root.rglob("*"):
        if any(part in SCAN_EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            yield path


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalize_text(text: str) -> str:
    return " ".join(text.split())
