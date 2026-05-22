from __future__ import annotations

from pathlib import Path

from intentfidelity.ingest.schemas import (
    DataFile,
    DatasetInventory,
    IngestSplit,
    ValidationIssue,
    ValidationSeverity,
)


FALCON_H2_DATASET_ID = "falcon_h2"
FALCON_H2_DIRECTORY_NAME = "h2"
FALCON_H2_EXPECTED_SPLITS: tuple[IngestSplit, ...] = (
    IngestSplit.HELD_IN_CALIB,
    IngestSplit.HELD_OUT_CALIB,
    IngestSplit.MINIVAL,
)
FALCON_H2_SPLIT_DIRECTORIES: dict[IngestSplit, tuple[str, ...]] = {
    IngestSplit.HELD_IN_CALIB: ("sub-T5-held-in-calib", "held_in_calib"),
    IngestSplit.HELD_OUT_CALIB: ("sub-T5-held-out-calib", "held_out_calib"),
    IngestSplit.MINIVAL: ("sub-T5-held-in-minival", "minival"),
}
FALCON_H2_FILE_SUFFIXES = (".nwb", ".h5", ".hdf5")


def resolve_falcon_h2_root(data_root: str | Path) -> Path:
    root = Path(data_root)
    if root.name == FALCON_H2_DIRECTORY_NAME:
        return root
    return root / FALCON_H2_DIRECTORY_NAME


def inventory_falcon_h2(data_root: str | Path) -> DatasetInventory:
    h2_root = resolve_falcon_h2_root(data_root)
    files: list[DataFile] = []
    issues: list[ValidationIssue] = []

    if not h2_root.exists():
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="missing_dataset_root",
                message="FALCON H2 root directory is missing.",
                path=str(h2_root),
            )
        )
        return DatasetInventory(FALCON_H2_DATASET_ID, h2_root, (), tuple(issues))

    if not h2_root.is_dir():
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="dataset_root_not_directory",
                message="FALCON H2 root path is not a directory.",
                path=str(h2_root),
            )
        )
        return DatasetInventory(FALCON_H2_DATASET_ID, h2_root, (), tuple(issues))

    for split in FALCON_H2_EXPECTED_SPLITS:
        split_dir = _resolve_split_directory(h2_root, split)
        if not split_dir.exists():
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="missing_split_directory",
                    message=f"Required FALCON H2 split directory is missing: {split.value}.",
                    path=str(split_dir),
                )
            )
            continue
        if not split_dir.is_dir():
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="split_path_not_directory",
                    message=f"FALCON H2 split path is not a directory: {split.value}.",
                    path=str(split_dir),
                )
            )
            continue

        split_files = _find_data_files(split_dir)
        if not split_files:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="empty_split_directory",
                    message=f"No NWB/HDF5 files found in split: {split.value}.",
                    path=str(split_dir),
                )
            )
        files.extend(
            DataFile(
                dataset_id=FALCON_H2_DATASET_ID,
                split=split,
                path=file_path,
                size_bytes=file_path.stat().st_size,
                metadata={"suffix": file_path.suffix.lower()},
            )
            for file_path in split_files
        )

    return DatasetInventory(
        dataset_id=FALCON_H2_DATASET_ID,
        root=h2_root,
        files=tuple(files),
        issues=tuple(issues),
    )


def _resolve_split_directory(h2_root: Path, split: IngestSplit) -> Path:
    for directory_name in FALCON_H2_SPLIT_DIRECTORIES[split]:
        candidate = h2_root / directory_name
        if candidate.exists():
            return candidate
    return h2_root / FALCON_H2_SPLIT_DIRECTORIES[split][0]


def _find_data_files(directory: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            (
                path
                for path in directory.rglob("*")
                if path.is_file() and path.suffix.lower() in FALCON_H2_FILE_SUFFIXES
            ),
            key=lambda path: str(path),
        )
    )
