from __future__ import annotations

from typing import Literal, Sequence

from intentfidelity.baselines import LabeledExample
from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.latent.cebra_backend import (
    CebraLatentProbeConfig,
    fit_cebra_latent_probe,
)
from intentfidelity.latent.pca import fit_pca_latent_probe
from intentfidelity.latent.reports import LatentDriftReport, LatentProbeConfig

LatentBackend = Literal["pca_svd", "cebra"]


def fit_latent_probe(
    fit_examples: Sequence[LabeledExample],
    evaluated_examples: Sequence[LabeledExample],
    targets: Sequence[WeakTarget],
    predictions: Sequence[Prediction],
    *,
    backend: LatentBackend = "pca_svd",
    n_components: int = 3,
    cebra_max_iterations: int = 100,
) -> LatentDriftReport:
    if backend == "pca_svd":
        return fit_pca_latent_probe(
            fit_examples,
            evaluated_examples,
            targets,
            predictions,
            config=LatentProbeConfig(n_components=n_components),
        )
    if backend == "cebra":
        return fit_cebra_latent_probe(
            fit_examples,
            evaluated_examples,
            targets,
            predictions,
            config=CebraLatentProbeConfig(
                n_components=n_components,
                max_iterations=cebra_max_iterations,
            ),
        )
    raise ValueError(f"unsupported latent backend: {backend}")
