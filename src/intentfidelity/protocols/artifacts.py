from __future__ import annotations

import json
from dataclasses import dataclass, field
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
