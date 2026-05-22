from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from intentfidelity.labels import NaturalisticEvent


@dataclass(frozen=True)
class NaturalisticProxySummary:
    event_count: int
    mean_confidence: float
    mean_ambiguity: float
    session_count: int

    def to_dict(self) -> dict[str, float | int]:
        return {
            "event_count": self.event_count,
            "mean_confidence": self.mean_confidence,
            "mean_ambiguity": self.mean_ambiguity,
            "session_count": self.session_count,
        }


def summarize_naturalistic_proxy(
    events: Iterable[NaturalisticEvent],
) -> NaturalisticProxySummary:
    event_tuple = tuple(events)
    if not event_tuple:
        raise ValueError("naturalistic proxy summary requires at least one event")
    confidences = tuple(event.confidence for event in event_tuple)
    sessions = {event.session_id for event in event_tuple if event.session_id is not None}
    mean_confidence = sum(confidences) / len(confidences)
    return NaturalisticProxySummary(
        event_count=len(event_tuple),
        mean_confidence=mean_confidence,
        mean_ambiguity=1.0 - mean_confidence,
        session_count=len(sessions),
    )
