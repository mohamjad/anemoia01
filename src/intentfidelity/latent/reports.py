from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

from intentfidelity.baselines import LabeledExample
from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.metrics import log_loss

ParameterValue = str | int | float | bool | None


@dataclass(frozen=True)
class LatentProbeConfig:
    method_id: str = "pca_svd_latent_probe"
    n_components: int = 3
    fit_scope: str = "train_examples"
    parameters: tuple[tuple[str, ParameterValue], ...] = ()

    def __post_init__(self) -> None:
        if not self.method_id.strip():
            raise ValueError("method_id must be set")
        if self.n_components <= 0:
            raise ValueError("n_components must be positive")
        if not self.fit_scope.strip():
            raise ValueError("fit_scope must be set")
        normalized_parameters = tuple(
            (str(key), _coerce_parameter_value(value))
            for key, value in self.parameters
        )
        if any(not key.strip() for key, _ in normalized_parameters):
            raise ValueError("parameter names must be non-empty")
        object.__setattr__(
            self,
            "parameters",
            tuple(sorted(normalized_parameters, key=lambda item: item[0])),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "method_id": self.method_id,
            "n_components": self.n_components,
            "fit_scope": self.fit_scope,
            "parameters": dict(self.parameters),
        }


@dataclass(frozen=True)
class LatentSample:
    sample_id: str
    session_id: str
    label: str
    vector: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.sample_id.strip():
            raise ValueError("sample_id must be set")
        if not self.session_id.strip():
            raise ValueError("session_id must be set")
        if self.label == "":
            raise ValueError("label must be set")
        if not self.vector:
            raise ValueError("vector cannot be empty")
        object.__setattr__(self, "vector", tuple(float(value) for value in self.vector))

    def to_dict(self) -> dict[str, object]:
        return {
            "sample_id": self.sample_id,
            "session_id": self.session_id,
            "label": self.label,
            "vector": list(self.vector),
        }


@dataclass(frozen=True)
class LatentDriftReport:
    config: LatentProbeConfig
    fit_sample_count: int
    evaluated_sample_count: int
    input_dimension: int
    latent_dimension: int
    explained_variance_ratio: tuple[float, ...]
    latent_centroid_shift: float
    latent_covariance_shift: float
    latent_mean_step_size: float
    latent_velocity_volatility: float
    latent_loss_correlation: float | None
    samples: tuple[LatentSample, ...]
    scope: str

    def to_dict(self) -> dict[str, object]:
        return {
            "config": self.config.to_dict(),
            "fit_sample_count": self.fit_sample_count,
            "evaluated_sample_count": self.evaluated_sample_count,
            "input_dimension": self.input_dimension,
            "latent_dimension": self.latent_dimension,
            "explained_variance_ratio": list(self.explained_variance_ratio),
            "latent_centroid_shift": self.latent_centroid_shift,
            "latent_covariance_shift": self.latent_covariance_shift,
            "latent_mean_step_size": self.latent_mean_step_size,
            "latent_velocity_volatility": self.latent_velocity_volatility,
            "latent_loss_correlation": self.latent_loss_correlation,
            "samples": [sample.to_dict() for sample in self.samples],
            "scope": self.scope,
        }


def build_latent_drift_report(
    *,
    config: LatentProbeConfig,
    fit_examples: Sequence[LabeledExample],
    evaluated_examples: Sequence[LabeledExample],
    targets: Sequence[WeakTarget],
    predictions: Sequence[Prediction],
    latent: np.ndarray,
    input_dimension: int,
    explained_variance_ratio: Sequence[float] = (),
    scope: str,
) -> LatentDriftReport:
    fit_tuple = tuple(fit_examples)
    evaluated_tuple = tuple(evaluated_examples)
    latent_matrix = _latent_matrix(latent)
    if latent_matrix.shape[0] != len(evaluated_tuple):
        raise ValueError("latent rows must match evaluated example count")

    samples = tuple(
        LatentSample(
            sample_id=example.sample_id,
            session_id=example.session_id,
            label=example.label,
            vector=tuple(float(value) for value in row),
        )
        for example, row in zip(evaluated_tuple, latent_matrix)
    )
    losses = _losses_by_evaluated_sample(evaluated_tuple, targets, predictions)
    step_sizes = _step_sizes(latent_matrix)
    return LatentDriftReport(
        config=LatentProbeConfig(
            method_id=config.method_id,
            n_components=latent_matrix.shape[1],
            fit_scope=config.fit_scope,
            parameters=config.parameters,
        ),
        fit_sample_count=len(fit_tuple),
        evaluated_sample_count=len(evaluated_tuple),
        input_dimension=input_dimension,
        latent_dimension=latent_matrix.shape[1],
        explained_variance_ratio=tuple(
            float(value) for value in explained_variance_ratio
        ),
        latent_centroid_shift=_session_centroid_shift(samples),
        latent_covariance_shift=_latent_covariance_shift(latent_matrix),
        latent_mean_step_size=float(step_sizes.mean()) if step_sizes.size else 0.0,
        latent_velocity_volatility=float(step_sizes.std()) if step_sizes.size else 0.0,
        latent_loss_correlation=_safe_correlation(_row_norms(latent_matrix), losses),
        samples=samples,
        scope=scope,
    )


def render_latent_drift_markdown(report: LatentDriftReport) -> str:
    lines = [
        "# Latent Drift Report",
        "",
        f"**Method:** {report.config.method_id}",
        "",
        f"**Fit samples:** {report.fit_sample_count}",
        "",
        f"**Evaluated samples:** {report.evaluated_sample_count}",
        "",
        f"**Input dimension:** {report.input_dimension}",
        "",
        f"**Latent dimension:** {report.latent_dimension}",
        "",
        "## Drift Metrics",
        f"- Latent centroid shift: {report.latent_centroid_shift:.3f}",
        f"- Latent covariance shift: {report.latent_covariance_shift:.3f}",
        f"- Latent mean step size: {report.latent_mean_step_size:.3f}",
        f"- Latent velocity volatility: {report.latent_velocity_volatility:.3f}",
        (
            "- Latent/loss correlation: "
            f"{_format_optional_float(report.latent_loss_correlation)}"
        ),
        "",
        "## Method Parameters",
    ]
    if report.config.parameters:
        for key, value in report.config.parameters:
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- none")
    lines.extend(["", "## Explained Variance"])
    if report.explained_variance_ratio:
        for index, ratio in enumerate(report.explained_variance_ratio, start=1):
            lines.append(f"- component_{index}: {ratio:.3f}")
    else:
        lines.append("- unavailable for this latent backend")
    lines.extend(
        [
            "",
            "## Scope",
            f"- {report.scope}",
            (
                "- Use this as a neural feature-state probe alongside "
                "proxy-fidelity artifacts, not as a direct intent readout."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def feature_matrix(examples: Sequence[LabeledExample]) -> np.ndarray:
    matrix = np.asarray([example.features for example in examples], dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[1] == 0:
        raise ValueError("examples must produce a non-empty feature matrix")
    return matrix


def explained_variance_ratio(
    singular_values: np.ndarray,
    component_count: int,
) -> tuple[float, ...]:
    variances = singular_values**2
    total = float(variances.sum())
    if total <= 0:
        return tuple(0.0 for _ in range(component_count))
    return tuple(float(value / total) for value in variances[:component_count])


def _latent_matrix(latent: np.ndarray) -> np.ndarray:
    matrix = np.asarray(latent, dtype=np.float64)
    if matrix.ndim == 1:
        matrix = matrix.reshape((-1, 1))
    if matrix.ndim != 2 or matrix.shape[1] == 0:
        raise ValueError("latent embedding must be a non-empty 2D matrix")
    return matrix


def _session_centroid_shift(samples: tuple[LatentSample, ...]) -> float:
    by_session: dict[str, list[tuple[float, ...]]] = {}
    for sample in samples:
        by_session.setdefault(sample.session_id, []).append(sample.vector)
    if len(by_session) < 2:
        return 0.0
    centroids = [
        np.asarray(vectors, dtype=np.float64).mean(axis=0)
        for _, vectors in sorted(by_session.items())
    ]
    shifts = [
        float(np.linalg.norm(right - left))
        for left, right in zip(centroids, centroids[1:])
    ]
    return sum(shifts) / len(shifts)


def _latent_covariance_shift(latent: np.ndarray) -> float:
    if latent.shape[0] < 2:
        return 0.0
    covariance = np.cov(latent, rowvar=False)
    if covariance.ndim == 0:
        return float(abs(covariance))
    return float(np.linalg.norm(covariance, ord="fro"))


def _step_sizes(latent: np.ndarray) -> np.ndarray:
    if latent.shape[0] < 2:
        return np.asarray((), dtype=np.float64)
    return np.linalg.norm(np.diff(latent, axis=0), axis=1)


def _row_norms(latent: np.ndarray) -> tuple[float, ...]:
    return tuple(float(value) for value in np.linalg.norm(latent, axis=1))


def _losses_by_evaluated_sample(
    examples: tuple[LabeledExample, ...],
    targets: Sequence[WeakTarget],
    predictions: Sequence[Prediction],
) -> tuple[float, ...]:
    targets_by_id = {target.sample_id: target for target in targets}
    predictions_by_sample: dict[str, list[Prediction]] = {}
    for prediction in predictions:
        predictions_by_sample.setdefault(prediction.sample_id, []).append(prediction)
    losses = []
    for example in examples:
        target = targets_by_id.get(example.sample_id)
        sample_predictions = predictions_by_sample.get(example.sample_id, [])
        if target is None or not sample_predictions:
            continue
        losses.append(
            sum(log_loss(target, prediction) for prediction in sample_predictions)
            / len(sample_predictions)
        )
    if len(losses) != len(examples):
        return ()
    return tuple(float(value) for value in losses)


def _safe_correlation(
    left: Sequence[float],
    right: Sequence[float],
) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    left_centered = [value - left_mean for value in left]
    right_centered = [value - right_mean for value in right]
    left_norm = math.sqrt(sum(value * value for value in left_centered))
    right_norm = math.sqrt(sum(value * value for value in right_centered))
    if left_norm == 0.0 or right_norm == 0.0:
        return None
    numerator = sum(
        left_value * right_value
        for left_value, right_value in zip(left_centered, right_centered)
    )
    return numerator / (left_norm * right_norm)


def _format_optional_float(value: float | None) -> str:
    return "unavailable" if value is None else f"{value:.3f}"


def _coerce_parameter_value(value: object) -> ParameterValue:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    return str(value)
