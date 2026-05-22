from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from intentfidelity.labels.authorization import AuthorizationEvent, AuthorizationState


def write_authorization_events_jsonl(
    events: Iterable[AuthorizationEvent], path: str | Path
) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(_event_to_dict(event), sort_keys=True) + "\n")


def read_authorization_events_jsonl(path: str | Path) -> tuple[AuthorizationEvent, ...]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return tuple(
            AuthorizationEvent(
                sample_id=row["sample_id"],
                state=AuthorizationState(row["state"]),
                metadata=row.get("metadata", {}),
            )
            for row in (json.loads(line) for line in handle if line.strip())
        )


def _event_to_dict(event: AuthorizationEvent) -> dict:
    return {
        "sample_id": event.sample_id,
        "state": event.state.value,
        "metadata": event.metadata,
    }
