from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from intentfidelity.labels.schemas import WeakTarget


NATURALISTIC_SOURCE_TYPE = "naturalistic_behavior_proxy"


@dataclass(frozen=True)
class NaturalisticEvent:
    sample_id: str
    observed_label: str
    candidate_labels: tuple[str, ...]
    confidence: float
    session_id: str | None = None
    start_time: float | None = None
    stop_time: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sample_id.strip():
            raise ValueError("sample_id must be set")
        if not self.observed_label.strip():
            raise ValueError("observed_label must be set")
        if not self.candidate_labels:
            raise ValueError("candidate_labels cannot be empty")
        if self.observed_label not in self.candidate_labels:
            raise ValueError("observed_label must be in candidate_labels")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.start_time is not None and self.stop_time is not None:
            if self.stop_time < self.start_time:
                raise ValueError("stop_time cannot be earlier than start_time")
        object.__setattr__(self, "candidate_labels", tuple(self.candidate_labels))
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "metadata", dict(self.metadata))


def weak_target_from_naturalistic_event(event: NaturalisticEvent) -> WeakTarget:
    other_labels = tuple(
        label for label in event.candidate_labels if label != event.observed_label
    )
    residual = 1.0 - event.confidence
    probabilities = {
        label: (residual / len(other_labels) if other_labels else 0.0)
        for label in event.candidate_labels
    }
    probabilities[event.observed_label] = event.confidence if other_labels else 1.0
    return WeakTarget(
        sample_id=event.sample_id,
        probabilities=probabilities,
        source_type=NATURALISTIC_SOURCE_TYPE,
        metadata={
            "observed_label": event.observed_label,
            "confidence": event.confidence,
            "session_id": event.session_id,
            "start_time": event.start_time,
            "stop_time": event.stop_time,
            **event.metadata,
        },
    )
