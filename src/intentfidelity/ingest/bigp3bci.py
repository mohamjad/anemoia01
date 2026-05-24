from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
import re
from typing import Any, Iterable

from intentfidelity.ingest.edf import EdfNumericSignals, read_edf_numeric_signals
from intentfidelity.ingest.schemas import ValidationIssue, ValidationSeverity
from intentfidelity.labels.p300 import P300SelectionEvent


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
_SYMBOL_LABEL_PATTERN = re.compile(
    r"^(?P<symbol>.+)_(?P<row>[0-9]+)_(?P<column>[0-9]+)$"
)


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
            "Raw-file inventory contract only; event extraction and scoring "
            "are separate implementation steps."
        ),
    }


def bigp3bci_event_extraction_contract() -> dict[str, Any]:
    return {
        "dataset_id": BIGP3BCI_DATASET_ID,
        "source": BIGP3BCI_PHYSIONET_URL,
        "version": BIGP3BCI_VERSION,
        "input_contract": "numeric EDF+ records from valid bigP3BCI files",
        "required_record_labels": list(BIGP3BCI_REQUIRED_RECORD_LABELS),
        "optional_record_labels": ["SelectedTarget"],
        "symbol_grid_label_pattern": "<symbol>_<row>_<column>",
        "output_type": "P300SelectionEvent",
        "evidence_scope": (
            "Typed event extraction only; prediction generation, scoring, and "
            "artifact bundles remain separate protocol steps."
        ),
    }


def load_bigp3bci_selection_events(
    data_file: BigP3BCIDataFile,
) -> tuple[P300SelectionEvent, ...]:
    signals = read_edf_numeric_signals(data_file.path)
    return bigp3bci_selection_events_from_signals(data_file, signals)


def load_bigp3bci_selection_events_from_root(
    data_root: str | Path,
) -> tuple[P300SelectionEvent, ...]:
    inventory = inventory_bigp3bci(data_root)
    if not inventory.is_valid:
        errors = [
            f"{issue.code}: {issue.message}"
            for issue in inventory.issues
            if issue.severity == ValidationSeverity.ERROR
        ]
        raise ValueError(f"invalid bigP3BCI inventory: {'; '.join(errors)}")
    events: list[P300SelectionEvent] = []
    for data_file in inventory.files:
        events.extend(load_bigp3bci_selection_events(data_file))
    return tuple(events)


def bigp3bci_selection_events_from_signals(
    data_file: BigP3BCIDataFile,
    signals: EdfNumericSignals,
) -> tuple[P300SelectionEvent, ...]:
    symbol_by_index = infer_bigp3bci_symbol_map(signals.signal_info_by_label().keys())
    if not symbol_by_index:
        raise ValueError("bigP3BCI EDF signals did not expose symbol-grid labels")

    stimulus_begin = _int_series(signals.require_signal("StimulusBegin"))
    stimulus_type = _int_series(signals.require_signal("StimulusType"))
    current_target = _int_series(signals.require_signal("CurrentTarget"))
    _require_equal_lengths(
        {
            "StimulusBegin": stimulus_begin,
            "StimulusType": stimulus_type,
            "CurrentTarget": current_target,
        }
    )

    selected_target = None
    if "SelectedTarget" in signals.signals:
        selected_target = _int_series(signals.signals["SelectedTarget"])
        _require_equal_lengths(
            {
                "CurrentTarget": current_target,
                "SelectedTarget": selected_target,
            }
        )

    candidate_symbols = tuple(
        symbol_by_index[index] for index in sorted(symbol_by_index)
    )
    sample_rate = signals.sample_rate("CurrentTarget")
    events: list[P300SelectionEvent] = []
    for event_index, span in enumerate(_target_spans(current_target)):
        start_index, stop_index, target_index = span
        target_symbol = _symbol_for_index(symbol_by_index, target_index)
        selected_symbol = None
        if selected_target is not None:
            selected_symbol = _selected_symbol_for_span(
                symbol_by_index,
                selected_target[start_index:stop_index],
            )
        stimulus_count = sum(stimulus_begin[start_index:stop_index])
        target_stimulus_count = sum(
            1
            for begin, kind in zip(
                stimulus_begin[start_index:stop_index],
                stimulus_type[start_index:stop_index],
            )
            if begin and kind == 1
        )
        events.append(
            P300SelectionEvent(
                sample_id=_bigp3bci_event_id(data_file, event_index),
                target_symbol=target_symbol,
                candidate_symbols=candidate_symbols,
                confidence=1.0,
                selected_symbol=selected_symbol,
                session_id=f"{data_file.subject_id}:{data_file.session_id}",
                start_time=start_index / sample_rate,
                stop_time=stop_index / sample_rate,
                metadata={
                    "dataset_id": BIGP3BCI_DATASET_ID,
                    "study_id": data_file.study_id,
                    "phase": data_file.phase.value,
                    "condition_path": list(data_file.condition_path),
                    "source_file": str(data_file.path),
                    "target_index": target_index,
                    "stimulus_count": stimulus_count,
                    "target_stimulus_count": target_stimulus_count,
                },
            )
        )
    return tuple(events)


def infer_bigp3bci_symbol_map(labels: Iterable[str]) -> dict[int, str]:
    grid_entries: list[tuple[int, int, str]] = []
    for label in labels:
        match = _SYMBOL_LABEL_PATTERN.match(label)
        if match is None:
            continue
        grid_entries.append(
            (
                int(match.group("row")),
                int(match.group("column")),
                match.group("symbol"),
            )
        )
    if not grid_entries:
        return {}
    column_count = max(column for _, column, _ in grid_entries)
    symbol_by_index: dict[int, str] = {}
    for row, column, symbol in grid_entries:
        index = (row - 1) * column_count + column
        if index in symbol_by_index:
            raise ValueError(f"duplicate bigP3BCI symbol index: {index}")
        symbol_by_index[index] = symbol
    return symbol_by_index


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


def _target_spans(values: tuple[int, ...]) -> tuple[tuple[int, int, int], ...]:
    spans: list[tuple[int, int, int]] = []
    active_target = 0
    start_index: int | None = None
    for index, value in enumerate(values):
        if value <= 0:
            if active_target > 0 and start_index is not None:
                spans.append((start_index, index, active_target))
            active_target = 0
            start_index = None
            continue
        if active_target == value:
            continue
        if active_target > 0 and start_index is not None:
            spans.append((start_index, index, active_target))
        active_target = value
        start_index = index
    if active_target > 0 and start_index is not None:
        spans.append((start_index, len(values), active_target))
    return tuple(spans)


def _int_series(values: tuple[float, ...]) -> tuple[int, ...]:
    return tuple(int(round(value)) for value in values)


def _require_equal_lengths(values_by_name: dict[str, tuple[int, ...]]) -> None:
    lengths = {name: len(values) for name, values in values_by_name.items()}
    if len(set(lengths.values())) > 1:
        raise ValueError(f"bigP3BCI signal lengths do not match: {lengths}")


def _symbol_for_index(symbol_by_index: dict[int, str], index: int) -> str:
    try:
        return symbol_by_index[index]
    except KeyError as exc:
        raise ValueError(f"missing bigP3BCI symbol for target index: {index}") from exc


def _selected_symbol_for_span(
    symbol_by_index: dict[int, str],
    values: tuple[int, ...],
) -> str | None:
    selected_values = [value for value in values if value > 0]
    if not selected_values:
        return None
    return _symbol_for_index(symbol_by_index, selected_values[-1])


def _bigp3bci_event_id(data_file: BigP3BCIDataFile, event_index: int) -> str:
    return (
        f"{BIGP3BCI_DATASET_ID}:{data_file.study_id}:{data_file.subject_id}:"
        f"{data_file.session_id}:{data_file.phase.value}:"
        f"file-{data_file.file_index:02d}:"
        f"event-{event_index:04d}"
    )


def _invalid_path_issue(path: Path, message: str) -> ValidationIssue:
    return ValidationIssue(
        ValidationSeverity.ERROR,
        "invalid_bigp3bci_edf_path",
        message,
        str(path),
    )
