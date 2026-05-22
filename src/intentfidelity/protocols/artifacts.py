from __future__ import annotations

import json
from dataclasses import dataclass, field
from collections.abc import Iterable
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping

from intentfidelity.protocols.schemas import ProtocolType


class EvidenceLevel(StrEnum):
    MANIFEST_ONLY = "manifest_only"
    SYNTHETIC_PROTOCOL_SCAFFOLD = "synthetic_protocol_scaffold"
    FIXTURE_EVIDENCE = "fixture_evidence"
    DOWNLOADED_DATASET_EVIDENCE = "downloaded_dataset_evidence"
    REPORTED_RESULT = "reported_result"


class ArtifactValidationSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class GeneratedArtifact:
    kind: str
    path: Path
    description: str

    def __post_init__(self) -> None:
        if not self.kind.strip():
            raise ValueError("artifact kind must be set")
        if not self.description.strip():
            raise ValueError("artifact description must be set")
        object.__setattr__(self, "path", Path(self.path))

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "path": str(self.path),
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> GeneratedArtifact:
        return cls(
            kind=str(payload["kind"]),
            path=Path(str(payload["path"])),
            description=str(payload["description"]),
        )


@dataclass(frozen=True)
class ArtifactBundle:
    dataset_id: str
    protocol: ProtocolType
    evidence_level: EvidenceLevel
    source_path: Path
    output_dir: Path
    generated_files: tuple[GeneratedArtifact, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("dataset_id must be set")
        if not self.generated_files:
            raise ValueError("artifact bundle requires at least one generated file")
        object.__setattr__(self, "source_path", Path(self.source_path))
        object.__setattr__(self, "output_dir", Path(self.output_dir))
        object.__setattr__(self, "generated_files", tuple(self.generated_files))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "protocol": self.protocol.value,
            "evidence_level": self.evidence_level.value,
            "source_path": str(self.source_path),
            "output_dir": str(self.output_dir),
            "generated_files": [artifact.to_dict() for artifact in self.generated_files],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ArtifactBundle:
        return cls(
            dataset_id=str(payload["dataset_id"]),
            protocol=ProtocolType(str(payload["protocol"])),
            evidence_level=EvidenceLevel(str(payload["evidence_level"])),
            source_path=Path(str(payload["source_path"])),
            output_dir=Path(str(payload["output_dir"])),
            generated_files=tuple(
                GeneratedArtifact.from_dict(item)
                for item in payload["generated_files"]
            ),
            metadata=dict(payload.get("metadata", {})),
        )


def save_artifact_bundle(bundle: ArtifactBundle, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(bundle.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_artifact_bundle(path: str | Path) -> ArtifactBundle:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return ArtifactBundle.from_dict(payload)


@dataclass(frozen=True)
class ArtifactValidationIssue:
    severity: ArtifactValidationSeverity
    code: str
    message: str
    path: Path | None = None

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("validation issue code must be set")
        if not self.message.strip():
            raise ValueError("validation issue message must be set")
        if self.path is not None:
            object.__setattr__(self, "path", Path(self.path))

    def to_dict(self) -> dict[str, str | None]:
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "path": str(self.path) if self.path is not None else None,
        }


@dataclass(frozen=True)
class ArtifactValidationReport:
    bundle_dir: Path
    manifest_path: Path
    checked_files: tuple[Path, ...]
    issues: tuple[ArtifactValidationIssue, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "bundle_dir", Path(self.bundle_dir))
        object.__setattr__(self, "manifest_path", Path(self.manifest_path))
        object.__setattr__(self, "checked_files", tuple(Path(path) for path in self.checked_files))
        object.__setattr__(self, "issues", tuple(self.issues))

    @property
    def is_valid(self) -> bool:
        return not any(
            issue.severity == ArtifactValidationSeverity.ERROR
            for issue in self.issues
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle_dir": str(self.bundle_dir),
            "manifest_path": str(self.manifest_path),
            "is_valid": self.is_valid,
            "checked_files": [str(path) for path in self.checked_files],
            "issues": [issue.to_dict() for issue in self.issues],
        }


def validate_artifact_bundle(
    bundle_dir: str | Path,
    *,
    required_kinds: Iterable[str] = (),
) -> ArtifactValidationReport:
    root = Path(bundle_dir)
    manifest_path = root / "bundle_manifest.json"
    issues: list[ArtifactValidationIssue] = []
    checked_files: list[Path] = []

    if not manifest_path.exists():
        return ArtifactValidationReport(
            bundle_dir=root,
            manifest_path=manifest_path,
            checked_files=(),
            issues=(
                ArtifactValidationIssue(
                    ArtifactValidationSeverity.ERROR,
                    "missing_bundle_manifest",
                    "bundle_manifest.json is required.",
                    manifest_path,
                ),
            ),
        )

    try:
        bundle = load_artifact_bundle(manifest_path)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return ArtifactValidationReport(
            bundle_dir=root,
            manifest_path=manifest_path,
            checked_files=(manifest_path,),
            issues=(
                ArtifactValidationIssue(
                    ArtifactValidationSeverity.ERROR,
                    "invalid_bundle_manifest",
                    f"bundle_manifest.json could not be loaded: {exc}",
                    manifest_path,
                ),
            ),
        )

    generated_by_kind = {artifact.kind: artifact for artifact in bundle.generated_files}
    for kind in sorted(set(required_kinds) - set(generated_by_kind)):
        issues.append(
            ArtifactValidationIssue(
                ArtifactValidationSeverity.ERROR,
                "missing_required_artifact_kind",
                f"bundle manifest is missing required artifact kind: {kind}",
                manifest_path,
            )
        )

    for artifact in bundle.generated_files:
        checked_files.append(artifact.path)
        if not artifact.path.exists():
            issues.append(
                ArtifactValidationIssue(
                    ArtifactValidationSeverity.ERROR,
                    "missing_generated_artifact",
                    f"generated artifact is missing: {artifact.kind}",
                    artifact.path,
                )
            )

    return ArtifactValidationReport(
        bundle_dir=root,
        manifest_path=manifest_path,
        checked_files=tuple(checked_files),
        issues=tuple(issues),
    )
