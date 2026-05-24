from __future__ import annotations

import sys
from types import SimpleNamespace

import numpy as np
import pytest

from intentfidelity.baselines import LabeledExample
from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.latent import CebraLatentProbeConfig, fit_cebra_latent_probe


def test_fit_cebra_latent_probe_uses_optional_backend_contract(monkeypatch) -> None:
    seen: dict[str, object] = {}

    class FakeCebraModel:
        def __init__(self, **kwargs: object) -> None:
            seen["kwargs"] = kwargs
            self.output_dimension = int(kwargs["output_dimension"])

        def fit(self, matrix: np.ndarray):
            seen["fit_shape"] = matrix.shape
            return self

        def transform(self, matrix: np.ndarray) -> np.ndarray:
            seen["transform_shape"] = matrix.shape
            columns = matrix[:, : self.output_dimension]
            if columns.shape[1] == self.output_dimension:
                return columns
            padding = np.zeros(
                (matrix.shape[0], self.output_dimension - columns.shape[1])
            )
            return np.hstack((columns, padding))

    monkeypatch.setitem(sys.modules, "cebra", SimpleNamespace(CEBRA=FakeCebraModel))

    report = fit_cebra_latent_probe(
        _train_examples(),
        _test_examples(),
        _targets(),
        _predictions(),
        config=CebraLatentProbeConfig(n_components=2, max_iterations=7),
    )

    assert report.config.method_id == "cebra_self_supervised_latent_probe"
    assert report.config.to_dict()["parameters"]["max_iterations"] == 7
    assert report.latent_dimension == 2
    assert report.evaluated_sample_count == 3
    assert report.explained_variance_ratio == ()
    assert "true intent" in report.scope
    assert seen["fit_shape"] == (3, 3)
    assert seen["transform_shape"] == (3, 3)
    assert seen["kwargs"] == {
        "batch_size": 512,
        "device": "cpu",
        "distance": "cosine",
        "max_iterations": 7,
        "model_architecture": "offset10-model",
        "output_dimension": 2,
        "time_offsets": 10,
        "verbose": False,
    }


def test_fit_cebra_latent_probe_reports_missing_optional_dependency(monkeypatch) -> None:
    def fake_import_module(name: str):
        if name == "cebra":
            raise ModuleNotFoundError(name)
        return __import__(name)

    monkeypatch.setattr(
        "intentfidelity.latent.cebra_backend.import_module",
        fake_import_module,
    )

    with pytest.raises(RuntimeError, match="latent-cebra"):
        fit_cebra_latent_probe(
            _train_examples(),
            _test_examples(),
            _targets(),
            _predictions(),
        )


def _train_examples() -> tuple[LabeledExample, ...]:
    return (
        LabeledExample("train-a", "A", (0.0, 0.0, 0.0), "s1"),
        LabeledExample("train-b", "B", (2.0, 0.0, 0.0), "s1"),
        LabeledExample("train-c", "A", (0.0, 2.0, 0.0), "s1"),
    )


def _test_examples() -> tuple[LabeledExample, ...]:
    return (
        LabeledExample("s0", "A", (0.0, 0.0, 0.0), "s1"),
        LabeledExample("s1", "B", (2.0, 0.0, 0.0), "s1"),
        LabeledExample("s2", "A", (0.0, 2.0, 0.0), "s2"),
    )


def _targets() -> tuple[WeakTarget, ...]:
    return (
        WeakTarget("s0", {"A": 1.0, "B": 0.0}, "prompt"),
        WeakTarget("s1", {"A": 0.0, "B": 1.0}, "prompt"),
        WeakTarget("s2", {"A": 1.0, "B": 0.0}, "prompt"),
    )


def _predictions() -> tuple[Prediction, ...]:
    return (
        Prediction("s0", {"A": 0.8, "B": 0.2}, "decoder"),
        Prediction("s1", {"A": 0.2, "B": 0.8}, "decoder"),
        Prediction("s2", {"A": 0.5, "B": 0.5}, "decoder"),
    )
