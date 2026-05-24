from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Sequence

import numpy as np

from intentfidelity.baselines import LabeledExample
from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.latent.reports import (
    LatentDriftReport,
    LatentProbeConfig,
    build_latent_drift_report,
    feature_matrix,
)

CEBRA_SCOPE = (
    "CEBRA latent probes summarize learned neural feature-state embeddings "
    "under optional nonlinear representation learning. They do not recover "
    "true intent, and any proxy labels used during fitting must be treated as "
    "part of the evidence scope."
)


@dataclass(frozen=True)
class CebraLatentProbeConfig:
    method_id: str = "cebra_self_supervised_latent_probe"
    n_components: int = 3
    fit_scope: str = "train_examples"
    max_iterations: int = 100
    batch_size: int | None = 512
    model_architecture: str = "offset10-model"
    distance: str = "cosine"
    conditional: str | None = None
    time_offsets: int = 10
    device: str = "cpu"

    def __post_init__(self) -> None:
        if not self.method_id.strip():
            raise ValueError("method_id must be set")
        if self.n_components <= 0:
            raise ValueError("n_components must be positive")
        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        if self.batch_size is not None and self.batch_size <= 0:
            raise ValueError("batch_size must be positive when set")
        if not self.model_architecture.strip():
            raise ValueError("model_architecture must be set")
        if not self.distance.strip():
            raise ValueError("distance must be set")
        if self.conditional is not None and not self.conditional.strip():
            raise ValueError("conditional must be non-empty when set")
        if self.time_offsets <= 0:
            raise ValueError("time_offsets must be positive")
        if not self.device.strip():
            raise ValueError("device must be set")

    def to_probe_config(self) -> LatentProbeConfig:
        return LatentProbeConfig(
            method_id=self.method_id,
            n_components=self.n_components,
            fit_scope=self.fit_scope,
            parameters=(
                ("batch_size", self.batch_size),
                ("conditional", self.conditional),
                ("device", self.device),
                ("distance", self.distance),
                ("max_iterations", self.max_iterations),
                ("model_architecture", self.model_architecture),
                ("time_offsets", self.time_offsets),
            ),
        )


def fit_cebra_latent_probe(
    fit_examples: Sequence[LabeledExample],
    evaluated_examples: Sequence[LabeledExample],
    targets: Sequence[WeakTarget],
    predictions: Sequence[Prediction],
    *,
    config: CebraLatentProbeConfig | None = None,
) -> LatentDriftReport:
    config = config or CebraLatentProbeConfig()
    fit_tuple = tuple(fit_examples)
    evaluated_tuple = tuple(evaluated_examples)
    if not fit_tuple:
        raise ValueError("CEBRA latent probe requires fit examples")
    if not evaluated_tuple:
        raise ValueError("CEBRA latent probe requires evaluated examples")

    fit_matrix = feature_matrix(fit_tuple)
    evaluated_matrix = feature_matrix(evaluated_tuple)
    if fit_matrix.shape[1] != evaluated_matrix.shape[1]:
        raise ValueError("fit and evaluated examples must share feature dimension")

    cebra_module = _load_cebra()
    _seed_torch_if_available(0)
    model = cebra_module.CEBRA(**_model_kwargs(config))
    model.fit(fit_matrix)
    latent = np.asarray(model.transform(evaluated_matrix), dtype=np.float64)
    return build_latent_drift_report(
        config=config.to_probe_config(),
        fit_examples=fit_tuple,
        evaluated_examples=evaluated_tuple,
        targets=targets,
        predictions=predictions,
        latent=latent,
        input_dimension=fit_matrix.shape[1],
        explained_variance_ratio=(),
        scope=CEBRA_SCOPE,
    )


def _model_kwargs(config: CebraLatentProbeConfig) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "output_dimension": config.n_components,
        "max_iterations": config.max_iterations,
        "model_architecture": config.model_architecture,
        "distance": config.distance,
        "time_offsets": config.time_offsets,
        "device": config.device,
        "verbose": False,
    }
    if config.batch_size is not None:
        kwargs["batch_size"] = config.batch_size
    if config.conditional is not None:
        kwargs["conditional"] = config.conditional
    return kwargs


def _load_cebra():
    try:
        return import_module("cebra")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "CEBRA latent backend requires the optional dependency. Install it "
            "with `pip install 'intentfidelity[latent-cebra]'` and rerun with "
            "`--latent-backend cebra`."
        ) from exc


def _seed_torch_if_available(seed: int) -> None:
    try:
        torch = import_module("torch")
    except ModuleNotFoundError:
        return
    manual_seed = getattr(torch, "manual_seed", None)
    if callable(manual_seed):
        manual_seed(seed)
