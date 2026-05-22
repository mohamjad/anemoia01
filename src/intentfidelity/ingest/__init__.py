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
from intentfidelity.ingest.nwb_hdf5 import (
    Hdf5DatasetInfo,
    NwbParseError,
    decode_array,
    decode_scalar,
    list_hdf5_datasets,
    require_dataset,
)
from intentfidelity.ingest.falcon_session import FalconSessionKey, session_date_from_path
from intentfidelity.ingest.falcon_trials import FalconH2Trial, load_falcon_h2_trials

__all__ = [
    "DataFile",
    "DatasetInventory",
    "IngestSplit",
    "FALCON_H2_DATASET_ID",
    "FALCON_H2_EXPECTED_SPLITS",
    "FalconSessionKey",
    "FalconH2Trial",
    "ValidationIssue",
    "ValidationSeverity",
    "Hdf5DatasetInfo",
    "NwbParseError",
    "decode_array",
    "decode_scalar",
    "inventory_falcon_h2",
    "list_hdf5_datasets",
    "load_falcon_h2_trials",
    "require_dataset",
    "resolve_falcon_h2_root",
    "session_date_from_path",
]
