from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from intentfidelity.labels.naturalistic import NaturalisticEvent


def write_naturalistic_events_jsonl(
    events: Iterable[NaturalisticEvent], path: str | Path
) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(_event_to_dict(event), sort_keys=True) + "\n")


def read_naturalistic_events_jsonl(path: str | Path) -> tuple[NaturalisticEvent, ...]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return tuple(
            NaturalisticEvent(
                sample_id=row["sample_id"],
                observed_label=row["observed_label"],
                candidate_labels=tuple(row["candidate_labels"]),
                confidence=float(row["confidence"]),
                session_id=row.get("session_id"),
                start_time=row.get("start_time"),
                stop_time=row.get("stop_time"),
                metadata=row.get("metadata", {}),
            )
            for row in (json.loads(line) for line in handle if line.strip())
        )


def _event_to_dict(event: NaturalisticEvent) -> dict:
    return {
        "sample_id": event.sample_id,
        "observed_label": event.observed_label,
        "candidate_labels": list(event.candidate_labels),
        "confidence": event.confidence,
        "session_id": event.session_id,
        "start_time": event.start_time,
        "stop_time": event.stop_time,
        "metadata": event.metadata,
    }
