from __future__ import annotations

from typing import Sequence

import numpy as np

from intentfidelity.baselines import LabeledExample
from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.latent.reports import (
    LatentDriftReport,
    LatentProbeConfig,
    build_latent_drift_report,
    explained_variance_ratio,
    feature_matrix,
)

PCA_SCOPE = (
    "PCA/SVD latent probes summarize neural feature-state movement. "
    "They do not recover true intent or replace decoder evaluation."
)


def fit_pca_latent_probe(
    fit_examples: Sequence[LabeledExample],
    evaluated_examples: Sequence[LabeledExample],
    targets: Sequence[WeakTarget],
    predictions: Sequence[Prediction],
    *,
    config: LatentProbeConfig | None = None,
) -> LatentDriftReport:
    config = config or LatentProbeConfig()
    fit_tuple = tuple(fit_examples)
    evaluated_tuple = tuple(evaluated_examples)
    if not fit_tuple:
        raise ValueError("latent probe requires fit examples")
    if not evaluated_tuple:
        raise ValueError("latent probe requires evaluated examples")

    fit_matrix = feature_matrix(fit_tuple)
    evaluated_matrix = feature_matrix(evaluated_tuple)
    if fit_matrix.shape[1] != evaluated_matrix.shape[1]:
        raise ValueError("fit and evaluated examples must share feature dimension")

    component_count = min(config.n_components, fit_matrix.shape[0], fit_matrix.shape[1])
    if component_count <= 0:
        raise ValueError("latent probe could not infer any components")
    mean = fit_matrix.mean(axis=0, keepdims=True)
    centered_fit = fit_matrix - mean
    _, singular_values, vt = np.linalg.svd(centered_fit, full_matrices=False)
    components = vt[:component_count]
    latent = (evaluated_matrix - mean) @ components.T
    return build_latent_drift_report(
        config=LatentProbeConfig(
            method_id=config.method_id,
            n_components=component_count,
            fit_scope=config.fit_scope,
            parameters=config.parameters,
        ),
        fit_examples=fit_tuple,
        evaluated_examples=evaluated_tuple,
        targets=targets,
        predictions=predictions,
        latent=latent,
        input_dimension=fit_matrix.shape[1],
        explained_variance_ratio=explained_variance_ratio(
            singular_values,
            component_count,
        ),
        scope=PCA_SCOPE,
    )
