import json
from pathlib import Path

import pytest

from intentfidelity.ingest import (
    BigP3BCIPhase,
    bigp3bci_event_extraction_contract,
    infer_bigp3bci_symbol_map,
    inventory_bigp3bci,
    load_bigp3bci_selection_events,
)
from intentfidelity.cli.main import main
from intentfidelity.labels import read_p300_events_jsonl

from edf_fixtures import write_numeric_edf


def test_infer_bigp3bci_symbol_map_uses_grid_labels() -> None:
    assert infer_bigp3bci_symbol_map(("A_1_1", "B_1_2", "C_2_1")) == {
        1: "A",
        2: "B",
        3: "C",
    }


def test_bigp3bci_event_extraction_contract_is_not_scoring() -> None:
    contract = bigp3bci_event_extraction_contract()

    assert contract["output_type"] == "P300SelectionEvent"
    assert "Typed event extraction only" in contract["evidence_scope"]


def test_load_bigp3bci_selection_events_from_synthetic_edf(tmp_path: Path) -> None:
    data_file = _write_bigp3bci_event_fixture(tmp_path)
    events = load_bigp3bci_selection_events(data_file)

    assert [event.target_symbol for event in events] == ["A", "B"]
    assert [event.selected_symbol for event in events] == ["A", "B"]
    assert events[0].candidate_symbols == ("A", "B")
    assert events[0].session_id == "A_01:SE001"
    assert events[0].start_time == pytest.approx(1 / 6)
    assert events[0].stop_time == pytest.approx(3 / 6)
    assert events[0].metadata["target_stimulus_count"] == 1
    assert events[1].metadata["stimulus_count"] == 2
    assert events[0].sample_id.startswith("bigp3bci:StudyA:A_01:SE001:Train")


def test_bigp3bci_events_command_writes_jsonl(tmp_path: Path, capsys) -> None:
    _write_bigp3bci_event_fixture(tmp_path)
    output = tmp_path / "events.jsonl"

    assert main(["ingest", "bigp3bci-events", str(tmp_path), str(output)]) == 0

    assert "Wrote 2 bigP3BCI selection events" in capsys.readouterr().out
    assert len(read_p300_events_jsonl(output)) == 2
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    assert rows[0]["metadata"]["dataset_id"] == "bigp3bci"


def _write_bigp3bci_event_fixture(tmp_path: Path):
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
