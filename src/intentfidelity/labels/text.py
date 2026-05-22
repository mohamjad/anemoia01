from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any


WHITESPACE_PATTERN = re.compile(r"\s+")


@dataclass(frozen=True)
class TextTarget:
    sample_id: str
    text: str
    source_type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sample_id.strip():
            raise ValueError("sample_id must be set")
        if not self.source_type.strip():
            raise ValueError("source_type must be set")
        object.__setattr__(self, "text", normalize_text(self.text))
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True)
class TextPrediction:
    sample_id: str
    text: str
    method_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sample_id.strip():
            raise ValueError("sample_id must be set")
        if not self.method_id.strip():
            raise ValueError("method_id must be set")
        object.__setattr__(self, "text", normalize_text(self.text))
        object.__setattr__(self, "metadata", dict(self.metadata))


def normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    return WHITESPACE_PATTERN.sub(" ", lowered)

