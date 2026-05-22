from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any

from intentfidelity.ingest.schemas import IngestSplit


SESSION_PATTERN = re.compile(r"ses-(?P<date>\d{8})")


@dataclass(frozen=True)
class FalconSessionKey:
    dataset_id: str
    split: IngestSplit
    session_date: str
    source_path: Path
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("dataset_id must be set")
        if not self.session_date.strip():
            raise ValueError("session_date must be set")
        object.__setattr__(self, "source_path", Path(self.source_path))
        object.__setattr__(self, "metadata", dict(self.metadata))


def session_date_from_path(path: str | Path) -> str:
    name = Path(path).name
    match = SESSION_PATTERN.search(name)
    if match is None:
        raise ValueError(f"cannot infer session date from path: {name}")
    raw = match.group("date")
    return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"

