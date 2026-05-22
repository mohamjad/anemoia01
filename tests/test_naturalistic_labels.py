import pytest

from intentfidelity.labels import (
    NATURALISTIC_SOURCE_TYPE,
    NaturalisticEvent,
    weak_target_from_naturalistic_event,
)


def test_naturalistic_event_builds_confidence_weighted_target() -> None:
    event = NaturalisticEvent(
        sample_id="s0",
        observed_label="reach",
        candidate_labels=("reach", "rest", "grasp"),
        confidence=0.8,
        session_id="session-1",
        start_time=1.0,
        stop_time=2.0,
    )

    target = weak_target_from_naturalistic_event(event)

    assert target.source_type == NATURALISTIC_SOURCE_TYPE
    assert target.probabilities == pytest.approx(
        {"reach": 0.8, "rest": 0.1, "grasp": 0.1}
    )
    assert target.metadata["session_id"] == "session-1"


def test_naturalistic_event_requires_observed_label_in_candidates() -> None:
    with pytest.raises(ValueError, match="observed_label"):
        NaturalisticEvent("s0", "reach", ("rest",), 0.8)
