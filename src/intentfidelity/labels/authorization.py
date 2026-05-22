from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from intentfidelity.labels.schemas import WeakTarget


class AuthorizationState(StrEnum):
    AUTHORIZED = "authorized"
    NOT_AUTHORIZED = "not_authorized"
    UNCERTAIN = "uncertain"


@dataclass(frozen=True)
class AuthorizationEvent:
    sample_id: str
    state: AuthorizationState
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sample_id.strip():
            raise ValueError("sample_id must be set")
        object.__setattr__(self, "metadata", dict(self.metadata))


def weak_target_from_authorization_event(event: AuthorizationEvent) -> WeakTarget:
    if event.state == AuthorizationState.AUTHORIZED:
        probabilities = {"authorized": 1.0, "not_authorized": 0.0}
    elif event.state == AuthorizationState.NOT_AUTHORIZED:
        probabilities = {"authorized": 0.0, "not_authorized": 1.0}
    else:
        probabilities = {"authorized": 0.5, "not_authorized": 0.5}
    return WeakTarget(
        sample_id=event.sample_id,
        probabilities=probabilities,
        source_type="authorization_state_proxy",
        metadata={"authorization_state": event.state.value, **event.metadata},
    )

