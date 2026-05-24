from __future__ import annotations

from pathlib import Path

from intentfidelity.ingest import BigP3BCIDataFile, BigP3BCIPhase, inventory_bigp3bci

from edf_fixtures import write_numeric_edf


def write_bigp3bci_event_fixture(tmp_path: Path) -> BigP3BCIDataFile:
    edf_path = (
        tmp_path
        / "bigP3BCI-data"
        / "StudyA"
        / "A_01"
        / "SE001"
        / "Train"
        / "speller"
        / "copy"
        / "A_01_SE001_Train01.edf"
    )
    write_numeric_edf(
        edf_path,
        {
            "StimulusBegin": (0, 1, 1, 0, 1, 1),
            "StimulusType": (0, 1, 0, 0, 0, 1),
            "CurrentTarget": (0, 1, 1, 0, 2, 2),
            "SelectedTarget": (0, 0, 1, 0, 0, 2),
            "A_1_1": (0, 0, 0, 0, 0, 0),
            "B_1_2": (0, 0, 0, 0, 0, 0),
        },
    )
    inventory = inventory_bigp3bci(tmp_path)
    assert inventory.is_valid is True
    return inventory.files_for_phase(BigP3BCIPhase.TRAIN)[0]
