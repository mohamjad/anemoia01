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

__all__ = [
    "DistributionValidationError",
    "Prediction",
    "WeakTarget",
    "align_probabilities",
    "normalize_probabilities",
    "prediction_from_dict",
    "require_same_support",
    "weak_target_from_dict",
]
