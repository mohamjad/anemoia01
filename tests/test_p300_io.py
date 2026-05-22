from intentfidelity.labels import P300SelectionEvent
from intentfidelity.labels.p300_io import read_p300_events_jsonl, write_p300_events_jsonl


def test_p300_events_jsonl_roundtrip(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    events = (
        P300SelectionEvent(
            sample_id="s0",
            target_symbol="A",
            candidate_symbols=("A", "B"),
            confidence=0.9,
            selected_symbol="A",
            session_id="session-1",
            start_time=1.0,
            stop_time=2.0,
            metadata={"matrix": "row_col"},
        ),
    )

    write_p300_events_jsonl(events, path)

    assert read_p300_events_jsonl(path) == events
