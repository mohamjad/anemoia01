from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from intentfidelity.labels.schemas import DistributionValidationError, WeakTarget


HANDWRITING_SOURCE_TYPE = "handwriting_prompt_window"


@dataclass(frozen=True)
class HandwritingCue:
    sample_id: str
    prompted_label: str
    window_start: float
    window_end: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sample_id.strip():
            raise DistributionValidationError("sample_id must be a non-empty string")
        if self.prompted_label == "":
            raise DistributionValidationError("prompted_label must be a non-empty string")
        if self.window_end <= self.window_start:
            raise DistributionValidationError("window_end must be greater than window_start")
        object.__setattr__(self, "metadata", dict(self.metadata))


def weak_target_from_handwriting_cue(
    cue: HandwritingCue,
    support: Sequence[str],
    *,
    off_target_mass: float = 0.0,
) -> WeakTarget:
    if not support:
        raise DistributionValidationError("support cannot be empty")
    if cue.prompted_label not in support:
        raise DistributionValidationError("prompted_label must be present in support")
    if off_target_mass < 0 or off_target_mass >= 1:
        raise DistributionValidationError("off_target_mass must be in [0, 1)")

    unique_support = tuple(dict.fromkeys(support))
    if len(unique_support) != len(tuple(support)):
        raise DistributionValidationError("support labels must be unique")

    remaining_labels = [label for label in unique_support if label != cue.prompted_label]
    probabilities = {label: 0.0 for label in unique_support}
    probabilities[cue.prompted_label] = 1.0 - off_target_mass
    if remaining_labels:
        share = off_target_mass / len(remaining_labels)
        for label in remaining_labels:
            probabilities[label] = share

    metadata = {
        "window_start": cue.window_start,
        "window_end": cue.window_end,
        "prompted_label": cue.prompted_label,
        **cue.metadata,
    }
    return WeakTarget(
        sample_id=cue.sample_id,
        probabilities=probabilities,
        source_type=HANDWRITING_SOURCE_TYPE,
        metadata=metadata,
    )
