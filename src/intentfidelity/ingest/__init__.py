"""Dataset ingestion interfaces."""

from intentfidelity.ingest.schemas import (
    DataFile,
    DatasetInventory,
    IngestSplit,
    ValidationIssue,
    ValidationSeverity,
)
from intentfidelity.ingest.falcon_h2 import (
    FALCON_H2_DATASET_ID,
    FALCON_H2_EXPECTED_SPLITS,
    inventory_falcon_h2,
    resolve_falcon_h2_root,
)

__all__ = [
    "DataFile",
    "DatasetInventory",
    "IngestSplit",
    "FALCON_H2_DATASET_ID",
    "FALCON_H2_EXPECTED_SPLITS",
    "ValidationIssue",
    "ValidationSeverity",
    "inventory_falcon_h2",
    "resolve_falcon_h2_root",
]
