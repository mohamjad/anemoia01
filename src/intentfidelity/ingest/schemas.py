from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class IngestSplit(StrEnum):
    HELD_IN_CALIB = "held_in_calib"
    HELD_OUT_CALIB = "held_out_calib"
    MINIVAL = "minival"


class ValidationSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class ValidationIssue:
    severity: ValidationSeverity
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }


@dataclass(frozen=True)
class DataFile:
    dataset_id: str
    split: IngestSplit
    path: Path
    size_bytes: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("dataset_id must be set")
        if self.size_bytes < 0:
            raise ValueError("size_bytes cannot be negative")
        object.__setattr__(self, "path", Path(self.path))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "split": self.split.value,
            "path": str(self.path),
            "size_bytes": self.size_bytes,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class DatasetInventory:
    dataset_id: str
    root: Path
    files: tuple[DataFile, ...]
    issues: tuple[ValidationIssue, ...] = ()

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("dataset_id must be set")
        object.__setattr__(self, "root", Path(self.root))
        object.__setattr__(self, "files", tuple(self.files))
        object.__setattr__(self, "issues", tuple(self.issues))

    @property
    def is_valid(self) -> bool:
        return not any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)

    def files_for_split(self, split: IngestSplit) -> tuple[DataFile, ...]:
        return tuple(file for file in self.files if file.split == split)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "root": str(self.root),
            "is_valid": self.is_valid,
            "file_count": len(self.files),
            "files": [file.to_dict() for file in self.files],
            "issues": [issue.to_dict() for issue in self.issues],
        }

