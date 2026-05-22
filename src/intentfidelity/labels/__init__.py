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

__all__ = [
    "DistributionValidationError",
    "HANDWRITING_SOURCE_TYPE",
    "Prediction",
    "HandwritingCue",
    "WeakTarget",
    "align_probabilities",
    "normalize_probabilities",
    "prediction_from_dict",
    "require_same_support",
    "weak_target_from_dict",
    "weak_target_from_handwriting_cue",
]
