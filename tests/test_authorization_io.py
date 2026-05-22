from intentfidelity.labels import (
    AuthorizationEvent,
    AuthorizationState,
    read_authorization_events_jsonl,
    write_authorization_events_jsonl,
)


def test_authorization_events_jsonl_roundtrip(tmp_path):
    path = tmp_path / "events.jsonl"
    events = (
        AuthorizationEvent(
            sample_id="s0",
            state=AuthorizationState.AUTHORIZED,
            metadata={"source": "button"},
        ),
        AuthorizationEvent(
            sample_id="s1",
            state=AuthorizationState.NOT_AUTHORIZED,
        ),
    )

    write_authorization_events_jsonl(events, path)

    assert read_authorization_events_jsonl(path) == events
