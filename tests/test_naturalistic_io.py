from intentfidelity.labels import NaturalisticEvent
from intentfidelity.labels.naturalistic_io import (
    read_naturalistic_events_jsonl,
    write_naturalistic_events_jsonl,
)


def test_naturalistic_events_jsonl_roundtrip(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    events = (
        NaturalisticEvent(
            sample_id="s0",
            observed_label="reach",
            candidate_labels=("reach", "rest"),
            confidence=0.75,
            session_id="session-1",
            start_time=1.0,
            stop_time=1.5,
            metadata={"source": "behavior"},
        ),
    )

    write_naturalistic_events_jsonl(events, path)

    assert read_naturalistic_events_jsonl(path) == events
