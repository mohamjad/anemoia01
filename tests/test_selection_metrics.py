import pytest

from intentfidelity.labels import P300SelectionEvent
from intentfidelity.metrics import summarize_selection_proxy


def test_summarize_selection_proxy_reports_accuracy_and_sessions() -> None:
    summary = summarize_selection_proxy(
        (
            P300SelectionEvent("s0", "A", ("A", "B"), 0.8, "A", "session-1"),
            P300SelectionEvent("s1", "B", ("A", "B"), 1.0, "A", "session-2"),
        )
    )

    assert summary.event_count == 2
    assert summary.mean_confidence == pytest.approx(0.9)
    assert summary.observed_selection_accuracy == pytest.approx(0.5)
    assert summary.session_count == 2


def test_summarize_selection_proxy_rejects_empty_events() -> None:
    with pytest.raises(ValueError, match="at least one"):
        summarize_selection_proxy(())
