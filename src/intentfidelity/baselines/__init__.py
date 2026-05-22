"""Baseline method registry."""

from intentfidelity.baselines.registry import BaselineSpec, get_baseline, list_baselines
from intentfidelity.baselines.predictions import proxy_oracle_prediction, uniform_prediction
from intentfidelity.baselines.examples import (
    LabeledExample,
    feature_dimension,
    labels_from_examples,
    sessions_from_examples,
)

__all__ = [
    "BaselineSpec",
    "LabeledExample",
    "feature_dimension",
    "get_baseline",
    "labels_from_examples",
    "list_baselines",
    "proxy_oracle_prediction",
    "sessions_from_examples",
    "uniform_prediction",
]
