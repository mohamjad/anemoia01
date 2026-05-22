"""Weak target and prediction schemas."""

from intentfidelity.labels.schemas import (
    DistributionValidationError,
    Prediction,
    WeakTarget,
    align_probabilities,
    normalize_probabilities,
    prediction_from_dict,
    require_same_support,
    weak_target_from_dict,
)
from intentfidelity.labels.handwriting import (
    HANDWRITING_SOURCE_TYPE,
    HandwritingCue,
    weak_target_from_handwriting_cue,
)
from intentfidelity.labels.cue_text import (
    SPACE_TOKEN,
    cue_character_sequence,
    cue_support,
    normalize_h2_cue,
)

__all__ = [
    "DistributionValidationError",
    "HANDWRITING_SOURCE_TYPE",
    "Prediction",
    "SPACE_TOKEN",
    "HandwritingCue",
    "WeakTarget",
    "align_probabilities",
    "cue_character_sequence",
    "cue_support",
    "normalize_probabilities",
    "normalize_h2_cue",
    "prediction_from_dict",
    "require_same_support",
    "weak_target_from_dict",
    "weak_target_from_handwriting_cue",
]
