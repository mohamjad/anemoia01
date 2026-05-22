"""Baseline method registry."""

from intentfidelity.baselines.registry import BaselineSpec, get_baseline, list_baselines
from intentfidelity.baselines.predictions import proxy_oracle_prediction, uniform_prediction

__all__ = [
    "BaselineSpec",
    "get_baseline",
    "list_baselines",
    "proxy_oracle_prediction",
    "uniform_prediction",
]
