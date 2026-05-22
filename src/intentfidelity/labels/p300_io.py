from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from intentfidelity.labels.p300 import P300SelectionEvent


def write_p300_events_jsonl(
    events: Iterable[P300SelectionEvent], path: str | Path
) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(_event_to_dict(event), sort_keys=True) + "\n")


def read_p300_events_jsonl(path: str | Path) -> tuple[P300SelectionEvent, ...]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return tuple(
            P300SelectionEvent(
                sample_id=row["sample_id"],
                target_symbol=row["target_symbol"],
                candidate_symbols=tuple(row["candidate_symbols"]),
                confidence=float(row.get("confidence", 1.0)),
                selected_symbol=row.get("selected_symbol"),
                session_id=row.get("session_id"),
                start_time=row.get("start_time"),
                stop_time=row.get("stop_time"),
                metadata=row.get("metadata", {}),
            )
            for row in (json.loads(line) for line in handle if line.strip())
        )


def _event_to_dict(event: P300SelectionEvent) -> dict:
    return {
        "sample_id": event.sample_id,
        "target_symbol": event.target_symbol,
        "candidate_symbols": list(event.candidate_symbols),
        "confidence": event.confidence,
        "selected_symbol": event.selected_symbol,
        "session_id": event.session_id,
        "start_time": event.start_time,
        "stop_time": event.stop_time,
        "metadata": event.metadata,
    }
