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
from intentfidelity.ingest.bigp3bci import (
    BIGP3BCI_DATASET_ID,
    BIGP3BCI_PHYSIONET_URL,
    BIGP3BCI_REQUIRED_RECORD_LABELS,
    BIGP3BCI_VERSION,
    BigP3BCIDataFile,
    BigP3BCIInventory,
    BigP3BCIPhase,
    bigp3bci_event_extraction_contract,
    bigp3bci_raw_data_contract,
    bigp3bci_selection_events_from_signals,
    infer_bigp3bci_symbol_map,
    inventory_bigp3bci,
    load_bigp3bci_selection_events,
    load_bigp3bci_selection_events_from_root,
    resolve_bigp3bci_root,
)
from intentfidelity.ingest.edf import (
    EdfNumericSignals,
    EdfParseError,
    EdfSignalInfo,
    read_edf_numeric_signals,
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
from intentfidelity.ingest.falcon_neural import (
    FalconH2NeuralSummary,
    summarize_falcon_h2_neural,
)

__all__ = [
    "DataFile",
    "DatasetInventory",
    "IngestSplit",
    "FALCON_H2_DATASET_ID",
    "FALCON_H2_EXPECTED_SPLITS",
    "BIGP3BCI_DATASET_ID",
    "BIGP3BCI_PHYSIONET_URL",
    "BIGP3BCI_REQUIRED_RECORD_LABELS",
    "BIGP3BCI_VERSION",
    "BigP3BCIDataFile",
    "BigP3BCIInventory",
    "BigP3BCIPhase",
    "EdfNumericSignals",
    "EdfParseError",
    "EdfSignalInfo",
    "FalconSessionKey",
    "FalconH2Trial",
    "FalconH2NeuralSummary",
    "ValidationIssue",
    "ValidationSeverity",
    "Hdf5DatasetInfo",
    "NwbParseError",
    "decode_array",
    "decode_scalar",
    "bigp3bci_event_extraction_contract",
    "bigp3bci_raw_data_contract",
    "bigp3bci_selection_events_from_signals",
    "infer_bigp3bci_symbol_map",
    "inventory_falcon_h2",
    "inventory_bigp3bci",
    "list_hdf5_datasets",
    "load_falcon_h2_trials",
    "load_bigp3bci_selection_events",
    "load_bigp3bci_selection_events_from_root",
    "read_edf_numeric_signals",
    "require_dataset",
    "resolve_bigp3bci_root",
    "resolve_falcon_h2_root",
    "session_date_from_path",
    "summarize_falcon_h2_neural",
]
