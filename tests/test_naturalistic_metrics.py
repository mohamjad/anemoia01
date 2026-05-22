import pytest

from intentfidelity.labels import NaturalisticEvent
from intentfidelity.metrics import summarize_naturalistic_proxy


def test_summarize_naturalistic_proxy_reports_confidence_and_sessions() -> None:
    summary = summarize_naturalistic_proxy(
        (
            NaturalisticEvent("s0", "reach", ("reach", "rest"), 0.8, "a"),
            NaturalisticEvent("s1", "rest", ("reach", "rest"), 0.6, "b"),
        )
    )

    assert summary.event_count == 2
    assert summary.mean_confidence == pytest.approx(0.7)
    assert summary.mean_ambiguity == pytest.approx(0.3)
    assert summary.session_count == 2


def test_summarize_naturalistic_proxy_rejects_empty_events() -> None:
    with pytest.raises(ValueError, match="at least one"):
        summarize_naturalistic_proxy(())
