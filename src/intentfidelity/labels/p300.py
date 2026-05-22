from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from intentfidelity.labels.schemas import WeakTarget


P300_SOURCE_TYPE = "p300_selection_proxy"


@dataclass(frozen=True)
class P300SelectionEvent:
    sample_id: str
    target_symbol: str
    candidate_symbols: tuple[str, ...]
    confidence: float = 1.0
    selected_symbol: str | None = None
    session_id: str | None = None
    start_time: float | None = None
    stop_time: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sample_id.strip():
            raise ValueError("sample_id must be set")
        if not self.target_symbol.strip():
            raise ValueError("target_symbol must be set")
        if not self.candidate_symbols:
            raise ValueError("candidate_symbols cannot be empty")
        if self.target_symbol not in self.candidate_symbols:
            raise ValueError("target_symbol must be in candidate_symbols")
        if self.selected_symbol is not None and self.selected_symbol not in self.candidate_symbols:
            raise ValueError("selected_symbol must be in candidate_symbols when set")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.start_time is not None and self.stop_time is not None:
            if self.stop_time < self.start_time:
                raise ValueError("stop_time cannot be earlier than start_time")
        object.__setattr__(self, "candidate_symbols", tuple(self.candidate_symbols))
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "metadata", dict(self.metadata))


def weak_target_from_p300_event(event: P300SelectionEvent) -> WeakTarget:
    other_symbols = tuple(
        symbol for symbol in event.candidate_symbols if symbol != event.target_symbol
    )
    residual = 1.0 - event.confidence
    probabilities = {
        symbol: (residual / len(other_symbols) if other_symbols else 0.0)
        for symbol in event.candidate_symbols
    }
    probabilities[event.target_symbol] = event.confidence if other_symbols else 1.0
    return WeakTarget(
        sample_id=event.sample_id,
        probabilities=probabilities,
        source_type=P300_SOURCE_TYPE,
        metadata={
            "target_symbol": event.target_symbol,
            "selected_symbol": event.selected_symbol,
            "confidence": event.confidence,
            "session_id": event.session_id,
            "start_time": event.start_time,
            "stop_time": event.stop_time,
            **event.metadata,
        },
    )
