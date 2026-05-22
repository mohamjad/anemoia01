"""Baseline method registry."""

from intentfidelity.baselines.registry import (
    BaselineSpec,
    get_baseline,
    list_baselines,
    list_implemented_baselines,
)
from intentfidelity.baselines.predictions import (
    project_prediction_to_target_support,
    proxy_oracle_prediction,
    uniform_prediction,
)
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
from intentfidelity.baselines.nearest_centroid import (
    NearestCentroidModel,
    fit_nearest_centroid,
)
from intentfidelity.baselines.runner import (
    BaselineRun,
    run_centroid_baseline,
    run_default_centroid_baselines,
)
from intentfidelity.baselines.io import (
    read_labeled_examples_csv,
    write_labeled_examples_csv,
)
from intentfidelity.baselines.synthetic import synthetic_shift_examples

__all__ = [
    "BaselineRun",
    "BaselineSpec",
    "FeatureTransform",
    "LabeledExample",
    "NearestCentroidModel",
    "feature_dimension",
    "fit_nearest_centroid",
    "get_baseline",
    "identity_transform",
    "labels_from_examples",
    "list_baselines",
    "list_implemented_baselines",
    "proxy_oracle_prediction",
    "project_prediction_to_target_support",
    "read_labeled_examples_csv",
    "run_centroid_baseline",
    "run_default_centroid_baselines",
    "sessions_from_examples",
    "session_centering_transform",
    "synthetic_shift_examples",
    "uniform_prediction",
    "whitening_coloring_transform",
    "whitening_transform",
    "write_labeled_examples_csv",
]
