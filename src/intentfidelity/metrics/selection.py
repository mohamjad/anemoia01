from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from intentfidelity.labels import P300SelectionEvent


@dataclass(frozen=True)
class SelectionProxySummary:
    event_count: int
    mean_confidence: float
    observed_selection_accuracy: float | None
    session_count: int

    def to_dict(self) -> dict[str, float | int | None]:
        return {
            "event_count": self.event_count,
            "mean_confidence": self.mean_confidence,
            "observed_selection_accuracy": self.observed_selection_accuracy,
            "session_count": self.session_count,
        }


def summarize_selection_proxy(
    events: Iterable[P300SelectionEvent],
) -> SelectionProxySummary:
    event_tuple = tuple(events)
    if not event_tuple:
        raise ValueError("selection proxy summary requires at least one event")
    selected = tuple(event for event in event_tuple if event.selected_symbol is not None)
    observed_accuracy = (
        sum(event.selected_symbol == event.target_symbol for event in selected)
        / len(selected)
        if selected
        else None
    )
    return SelectionProxySummary(
        event_count=len(event_tuple),
        mean_confidence=sum(event.confidence for event in event_tuple) / len(event_tuple),
        observed_selection_accuracy=observed_accuracy,
        session_count=len(
            {event.session_id for event in event_tuple if event.session_id is not None}
        ),
    )
