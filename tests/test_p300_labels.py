import pytest

from intentfidelity.labels import (
    P300_SOURCE_TYPE,
    P300SelectionEvent,
    weak_target_from_p300_event,
)


def test_p300_event_builds_symbol_target_distribution() -> None:
    event = P300SelectionEvent(
        sample_id="s0",
        target_symbol="A",
        candidate_symbols=("A", "B", "C"),
        confidence=0.8,
        selected_symbol="A",
        session_id="session-1",
    )

    target = weak_target_from_p300_event(event)

    assert target.source_type == P300_SOURCE_TYPE
    assert target.probabilities == pytest.approx({"A": 0.8, "B": 0.1, "C": 0.1})
    assert target.metadata["selected_symbol"] == "A"


def test_p300_event_requires_target_symbol_in_candidates() -> None:
    with pytest.raises(ValueError, match="target_symbol"):
        P300SelectionEvent("s0", "A", ("B",), 1.0)
