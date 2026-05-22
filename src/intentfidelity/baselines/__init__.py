"""Baseline method registry."""

from intentfidelity.baselines.registry import BaselineSpec, get_baseline, list_baselines
from intentfidelity.baselines.predictions import proxy_oracle_prediction, uniform_prediction
from intentfidelity.baselines.examples import (
    LabeledExample,
    feature_dimension,
    labels_from_examples,
    sessions_from_examples,
)
from intentfidelity.baselines.transforms import (
    FeatureTransform,
    identity_transform,
    session_centering_transform,
    whitening_coloring_transform,
    whitening_transform,
)

__all__ = [
    "BaselineSpec",
    "FeatureTransform",
    "LabeledExample",
    "feature_dimension",
    "get_baseline",
    "identity_transform",
    "labels_from_examples",
    "list_baselines",
    "proxy_oracle_prediction",
    "sessions_from_examples",
    "session_centering_transform",
    "uniform_prediction",
    "whitening_coloring_transform",
    "whitening_transform",
]
