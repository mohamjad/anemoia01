from pathlib import Path

from intentfidelity.ingest import (
    BIGP3BCI_PHYSIONET_URL,
    BIGP3BCI_REQUIRED_RECORD_LABELS,
    BIGP3BCI_VERSION,
    BigP3BCIPhase,
    bigp3bci_raw_data_contract,
    inventory_bigp3bci,
    resolve_bigp3bci_root,
)


def test_resolve_bigp3bci_root_accepts_parent_or_dataset_root(tmp_path: Path) -> None:
    assert resolve_bigp3bci_root(tmp_path) == tmp_path / "bigP3BCI-data"
    assert (
        resolve_bigp3bci_root(tmp_path / "bigP3BCI-data")
        == tmp_path / "bigP3BCI-data"
    )


def test_inventory_reports_missing_dataset_root(tmp_path: Path) -> None:
    inventory = inventory_bigp3bci(tmp_path)

    assert inventory.is_valid is False
    assert inventory.issues[0].code == "missing_dataset_root"
    assert inventory.to_dict()["contract"]["version"] == BIGP3BCI_VERSION


def test_inventory_parses_bigp3bci_edf_hierarchy(tmp_path: Path) -> None:
    train_file = _write_bigp3bci_edf(
        tmp_path,
        "StudyA",
        "A_01",
        "SE001",
        BigP3BCIPhase.TRAIN,
        ("speller", "copy"),
        "A_01_SE001_Train01.edf",
    )
    _write_bigp3bci_edf(
        tmp_path,
        "StudyA",
        "A_01",
        "SE001",
        BigP3BCIPhase.TEST,
        ("speller", "free"),
        "A_01_SE001_Test02.edf",
    )

    inventory = inventory_bigp3bci(tmp_path)

    assert inventory.dataset_id == "bigp3bci"
    assert inventory.is_valid is True
    assert len(inventory.files) == 2
    assert len(inventory.files_for_phase(BigP3BCIPhase.TRAIN)) == 1
    assert len(inventory.files_for_phase(BigP3BCIPhase.TEST)) == 1

    parsed = inventory.files_for_phase(BigP3BCIPhase.TRAIN)[0]
    assert parsed.study_id == "StudyA"
    assert parsed.subject_id == "A_01"
    assert parsed.session_id == "SE001"
    assert parsed.condition_path == ("speller", "copy")
    assert parsed.file_index == 1
    assert parsed.path == train_file
    assert parsed.size_bytes == 3

    payload = inventory.to_dict()
    assert payload["train_file_count"] == 1
    assert payload["test_file_count"] == 1
    assert payload["contract"]["source"] == BIGP3BCI_PHYSIONET_URL


def test_inventory_rejects_phase_mismatch(tmp_path: Path) -> None:
    _write_bigp3bci_edf(
        tmp_path,
        "StudyS1",
        "S1_01",
        "SE001",
        BigP3BCIPhase.TRAIN,
        ("condition",),
        "S1_01_SE001_Test01.edf",
    )

    inventory = inventory_bigp3bci(tmp_path)

    assert inventory.is_valid is False
    assert inventory.files == ()
    assert inventory.issues[0].code == "invalid_bigp3bci_edf_path"
    assert "phase must match" in inventory.issues[0].message


def test_inventory_reports_empty_root_as_warning(tmp_path: Path) -> None:
    (tmp_path / "bigP3BCI-data").mkdir()

    inventory = inventory_bigp3bci(tmp_path)

    assert inventory.is_valid is True
    assert inventory.files == ()
    assert inventory.issues[0].code == "no_edf_files"


def test_bigp3bci_raw_data_contract_stays_inventory_scoped() -> None:
    contract = bigp3bci_raw_data_contract()

    assert contract["dataset_id"] == "bigp3bci"
    assert contract["file_format"] == "EDF+"
    assert contract["required_record_labels"] == list(
        BIGP3BCI_REQUIRED_RECORD_LABELS
    )
    assert "Raw-file inventory contract only" in contract["evidence_scope"]


def _write_bigp3bci_edf(
    tmp_path: Path,
    study_id: str,
    subject_id: str,
    session_id: str,
    phase: BigP3BCIPhase,
    condition_path: tuple[str, ...],
    file_name: str,
) -> Path:
    path = (
        tmp_path
        / "bigP3BCI-data"
        / study_id
        / subject_id
        / session_id
        / phase.value
    )
    for condition in condition_path:
        path /= condition
    path.mkdir(parents=True)
    edf = path / file_name
    edf.write_bytes(b"edf")
    return edf
