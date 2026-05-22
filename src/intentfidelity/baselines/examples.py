from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass(frozen=True)
class LabeledExample:
    sample_id: str
    label: str
    features: tuple[float, ...]
    session_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sample_id.strip():
            raise ValueError("sample_id must be set")
        if self.label == "":
            raise ValueError("label must be set")
        if not self.features:
            raise ValueError("features cannot be empty")
        if not self.session_id.strip():
            raise ValueError("session_id must be set")
        object.__setattr__(self, "features", tuple(float(value) for value in self.features))
        object.__setattr__(self, "metadata", dict(self.metadata))


def feature_dimension(examples: Sequence[LabeledExample]) -> int:
    if not examples:
        raise ValueError("examples cannot be empty")
    dimension = len(examples[0].features)
    if any(len(example.features) != dimension for example in examples):
        raise ValueError("all examples must have the same feature dimension")
    return dimension


def labels_from_examples(examples: Sequence[LabeledExample]) -> tuple[str, ...]:
    return tuple(sorted({example.label for example in examples}))


def sessions_from_examples(examples: Sequence[LabeledExample]) -> tuple[str, ...]:
    return tuple(sorted({example.session_id for example in examples}))

