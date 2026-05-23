from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
import re
from typing import Any

from intentfidelity.ingest.schemas import ValidationIssue, ValidationSeverity


BIGP3BCI_DATASET_ID = "bigp3bci"
BIGP3BCI_DATASET_DIRECTORY = "bigP3BCI-data"
BIGP3BCI_VERSION = "1.0.0"
BIGP3BCI_PHYSIONET_URL = "https://physionet.org/content/bigp3bci/1.0.0/"
BIGP3BCI_FILE_SUFFIX = ".edf"

BIGP3BCI_REQUIRED_RECORD_LABELS: tuple[str, ...] = (
    "StimulusBegin",
    "StimulusType",
    "CurrentTarget",
)
BIGP3BCI_OPTIONAL_FEEDBACK_LABEL_PREFIXES: tuple[str, ...] = (
    "SelectedTarget",
    "SelectedRow",
    "SelectedColumn",
    "DisplayResult",
    "FakeFeedback",
)

_SUBJECT_PATTERN = re.compile(r"^[A-Z][0-9]?_[0-9]{2}$")
_SESSION_PATTERN = re.compile(r"^SE[0-9]{3}$")
_FILE_INDEX_PATTERN = re.compile(r"(?P<phase>Train|Test)(?P<index>[0-9]+)\.edf$")


class BigP3BCIPhase(StrEnum):
    TRAIN = "Train"
    TEST = "Test"


@dataclass(frozen=True)
class BigP3BCIDataFile:
    study_id: str
    subject_id: str
    session_id: str
    phase: BigP3BCIPhase
    condition_path: tuple[str, ...]
    file_index: int
    path: Path
    size_bytes: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.study_id.strip():
            raise ValueError("study_id must be set")
        if not _SUBJECT_PATTERN.match(self.subject_id):
            raise ValueError("subject_id must follow the bigP3BCI subject pattern")
        if not _SESSION_PATTERN.match(self.session_id):
            raise ValueError("session_id must follow the bigP3BCI session pattern")
        if self.file_index <= 0:
            raise ValueError("file_index must be positive")
        if self.size_bytes < 0:
            raise ValueError("size_bytes cannot be negative")
        object.__setattr__(self, "condition_path", tuple(self.condition_path))
        object.__setattr__(self, "path", Path(self.path))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": BIGP3BCI_DATASET_ID,
            "study_id": self.study_id,
            "subject_id": self.subject_id,
            "session_id": self.session_id,
            "phase": self.phase.value,
            "condition_path": list(self.condition_path),
            "file_index": self.file_index,
            "path": str(self.path),
            "size_bytes": self.size_bytes,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class BigP3BCIInventory:
    root: Path
    files: tuple[BigP3BCIDataFile, ...]
    issues: tuple[ValidationIssue, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", Path(self.root))
        object.__setattr__(self, "files", tuple(self.files))
        object.__setattr__(self, "issues", tuple(self.issues))

    @property
    def dataset_id(self) -> str:
        return BIGP3BCI_DATASET_ID

    @property
    def is_valid(self) -> bool:
        return not any(
            issue.severity == ValidationSeverity.ERROR for issue in self.issues
        )

    def files_for_phase(self, phase: BigP3BCIPhase) -> tuple[BigP3BCIDataFile, ...]:
        return tuple(file for file in self.files if file.phase == phase)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "root": str(self.root),
            "is_valid": self.is_valid,
            "file_count": len(self.files),
            "train_file_count": len(self.files_for_phase(BigP3BCIPhase.TRAIN)),
            "test_file_count": len(self.files_for_phase(BigP3BCIPhase.TEST)),
            "files": [file.to_dict() for file in self.files],
            "issues": [issue.to_dict() for issue in self.issues],
            "contract": bigp3bci_raw_data_contract(),
        }


def resolve_bigp3bci_root(data_root: str | Path) -> Path:
    root = Path(data_root)
    if root.name == BIGP3BCI_DATASET_DIRECTORY:
        return root
    return root / BIGP3BCI_DATASET_DIRECTORY


def inventory_bigp3bci(data_root: str | Path) -> BigP3BCIInventory:
    root = resolve_bigp3bci_root(data_root)
    issues: list[ValidationIssue] = []
    files: list[BigP3BCIDataFile] = []

    if not root.exists():
        issues.append(
            ValidationIssue(
                ValidationSeverity.ERROR,
                "missing_dataset_root",
                "bigP3BCI root directory is missing.",
                str(root),
            )
        )
        return BigP3BCIInventory(root, (), tuple(issues))

    if not root.is_dir():
        issues.append(
            ValidationIssue(
                ValidationSeverity.ERROR,
                "dataset_root_not_directory",
                "bigP3BCI root path is not a directory.",
                str(root),
            )
        )
        return BigP3BCIInventory(root, (), tuple(issues))

    for path in sorted(
        root.rglob(f"*{BIGP3BCI_FILE_SUFFIX}"),
        key=lambda item: str(item),
    ):
        parsed = _parse_bigp3bci_path(root, path)
        if isinstance(parsed, ValidationIssue):
            issues.append(parsed)
            continue
        files.append(parsed)

    if not files:
        issues.append(
            ValidationIssue(
                ValidationSeverity.WARNING,
                "no_edf_files",
                "No bigP3BCI EDF+ files were found under the dataset root.",
                str(root),
            )
        )

    return BigP3BCIInventory(root, tuple(files), tuple(issues))


def bigp3bci_raw_data_contract() -> dict[str, Any]:
    return {
        "dataset_id": BIGP3BCI_DATASET_ID,
        "source": BIGP3BCI_PHYSIONET_URL,
        "version": BIGP3BCI_VERSION,
        "root_directory": BIGP3BCI_DATASET_DIRECTORY,
        "file_format": "EDF+",
        "hierarchy": (
            "Study*/<subject_id>/<session_id>/<Train|Test>/"
            "<condition...>/*<Train|Test><index>.edf"
        ),
        "required_record_labels": list(BIGP3BCI_REQUIRED_RECORD_LABELS),
        "optional_feedback_label_prefixes": list(
            BIGP3BCI_OPTIONAL_FEEDBACK_LABEL_PREFIXES
        ),
        "evidence_scope": (
            "Raw-file inventory contract only; EDF+ signal and annotation "
            "parsing is a later implementation step."
        ),
    }


def _parse_bigp3bci_path(
    root: Path,
    path: Path,
) -> BigP3BCIDataFile | ValidationIssue:
    relative_parts = path.relative_to(root).parts
    if len(relative_parts) < 5:
        return _invalid_path_issue(
            path,
            "EDF+ file is too shallow for bigP3BCI hierarchy.",
        )

    study_id, subject_id, session_id, phase_text, *tail = relative_parts
    if not study_id.startswith("Study"):
        return _invalid_path_issue(path, "Study directory must start with 'Study'.")
    if not _SUBJECT_PATTERN.match(subject_id):
        return _invalid_path_issue(path, "Subject directory must look like A_01.")
    if not _SESSION_PATTERN.match(session_id):
        return _invalid_path_issue(path, "Session directory must look like SE001.")

    try:
        phase = BigP3BCIPhase(phase_text)
    except ValueError:
        return _invalid_path_issue(path, "Phase directory must be Train or Test.")

    file_match = _FILE_INDEX_PATTERN.search(path.name)
    if file_match is None:
        return _invalid_path_issue(
            path,
            "File name must end with Train##.edf or Test##.edf.",
        )
    if file_match.group("phase") != phase.value:
        return _invalid_path_issue(
            path,
            "File name phase must match the phase directory.",
        )

    return BigP3BCIDataFile(
        study_id=study_id,
        subject_id=subject_id,
        session_id=session_id,
        phase=phase,
        condition_path=tuple(tail[:-1]),
        file_index=int(file_match.group("index")),
        path=path,
        size_bytes=path.stat().st_size,
        metadata={"suffix": path.suffix.lower()},
    )


def _invalid_path_issue(path: Path, message: str) -> ValidationIssue:
    return ValidationIssue(
        ValidationSeverity.ERROR,
        "invalid_bigp3bci_edf_path",
        message,
        str(path),
    )
