from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


class DistributionValidationError(ValueError):
    """Raised when a weak target or prediction distribution is invalid."""


@dataclass(frozen=True)
class WeakTarget:
    sample_id: str
    probabilities: dict[str, float]
    source_type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_id(self.sample_id, "sample_id")
        _validate_id(self.source_type, "source_type")
        normalized = normalize_probabilities(self.probabilities)
        object.__setattr__(self, "probabilities", normalized)
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def support(self) -> tuple[str, ...]:
        return tuple(self.probabilities)


@dataclass(frozen=True)
class Prediction:
    sample_id: str
    probabilities: dict[str, float]
    method_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_id(self.sample_id, "sample_id")
        _validate_id(self.method_id, "method_id")
        normalized = normalize_probabilities(self.probabilities)
        object.__setattr__(self, "probabilities", normalized)
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def support(self) -> tuple[str, ...]:
        return tuple(self.probabilities)


def normalize_probabilities(probabilities: Mapping[str, float]) -> dict[str, float]:
    if not probabilities:
        raise DistributionValidationError("probability distribution cannot be empty")

    clean: dict[str, float] = {}
    total = 0.0
    for label, value in probabilities.items():
        if not isinstance(label, str) or not label.strip():
            raise DistributionValidationError("distribution labels must be non-empty strings")
        if not isinstance(value, int | float) or isinstance(value, bool):
            raise DistributionValidationError("distribution probabilities must be numeric")
        probability = float(value)
        if probability < 0:
            raise DistributionValidationError("distribution probabilities cannot be negative")
        clean[label] = probability
        total += probability

    if total <= 0:
        raise DistributionValidationError("probability distribution must have positive mass")

    return {label: probability / total for label, probability in clean.items()}


def require_same_support(target: WeakTarget, prediction: Prediction) -> None:
    if target.sample_id != prediction.sample_id:
        raise DistributionValidationError("target and prediction sample_id values differ")
    target_support = set(target.support)
    prediction_support = set(prediction.support)
    if target_support != prediction_support:
        missing = sorted(target_support - prediction_support)
        extra = sorted(prediction_support - target_support)
        parts = []
        if missing:
            parts.append(f"missing labels: {', '.join(missing)}")
        if extra:
            parts.append(f"extra labels: {', '.join(extra)}")
        raise DistributionValidationError("; ".join(parts))


def align_probabilities(
    target: WeakTarget, prediction: Prediction
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[str, ...]]:
    require_same_support(target, prediction)
    labels = tuple(sorted(target.support))
    target_values = tuple(target.probabilities[label] for label in labels)
    prediction_values = tuple(prediction.probabilities[label] for label in labels)
    return target_values, prediction_values, labels


def _validate_id(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise DistributionValidationError(f"{field_name} must be a non-empty string")

