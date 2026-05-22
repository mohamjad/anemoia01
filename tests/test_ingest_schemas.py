from pathlib import Path

from intentfidelity.ingest import (
    DataFile,
    DatasetInventory,
    IngestSplit,
    ValidationIssue,
    ValidationSeverity,
)


def test_inventory_validity_depends_on_error_issues() -> None:
    inventory = DatasetInventory(
        dataset_id="falcon_h2",
        root=Path("data/h2"),
        files=(
            DataFile(
                dataset_id="falcon_h2",
                split=IngestSplit.HELD_IN_CALIB,
                path=Path("data/h2/held_in_calib/example.nwb"),
                size_bytes=12,
            ),
        ),
        issues=(
            ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="example_warning",
                message="warning only",
            ),
        ),
    )

    assert inventory.is_valid is True
    assert len(inventory.files_for_split(IngestSplit.HELD_IN_CALIB)) == 1


def test_inventory_serializes_paths_and_issues() -> None:
    inventory = DatasetInventory(
        dataset_id="falcon_h2",
        root=Path("data/h2"),
        files=(),
        issues=(
            ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="missing_split",
                message="split is missing",
                path="data/h2/minival",
            ),
        ),
    )

    payload = inventory.to_dict()

    assert payload["is_valid"] is False
    assert payload["issues"][0]["path"] == "data/h2/minival"

