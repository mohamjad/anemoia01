"""Weak target and prediction schemas."""

from intentfidelity.labels.schemas import (
    DistributionValidationError,
    Prediction,
    WeakTarget,
    align_probabilities,
    normalize_probabilities,
    require_same_support,
)

__all__ = [
    "DistributionValidationError",
    "Prediction",
    "WeakTarget",
    "align_probabilities",
    "normalize_probabilities",
    "require_same_support",
]

