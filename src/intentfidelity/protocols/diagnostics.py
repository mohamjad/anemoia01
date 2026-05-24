from __future__ import annotations

from dataclasses import dataclass
import math
import random

from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.metrics import brier_score, log_loss


@dataclass(frozen=True)
class MethodDiagnostics:
    method_id: str
    sample_count: int
    mean_log_loss: float
    mean_brier_score: float
    proxy_top1_accuracy: float

    def to_dict(self) -> dict[str, float | int | str]:
        return {
            "method_id": self.method_id,
            "sample_count": self.sample_count,
            "mean_log_loss": self.mean_log_loss,
            "mean_brier_score": self.mean_brier_score,
            "proxy_top1_accuracy": self.proxy_top1_accuracy,
        }


@dataclass(frozen=True)
class BootstrapRankingDiagnostics:
    n_resamples: int
    seed: int
    top_method_frequencies: dict[str, float]
    mean_ranks: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        return {
            "n_resamples": self.n_resamples,
            "seed": self.seed,
            "top_method_frequencies": self.top_method_frequencies,
            "mean_ranks": self.mean_ranks,
        }


@dataclass(frozen=True)
class MethodProxyStateDynamics:
    method_id: str
    mean_prediction_shift: float
    mean_shift_tracking_error: float
    loss_volatility: float

    def to_dict(self) -> dict[str, float | str]:
        return {
            "method_id": self.method_id,
            "mean_prediction_shift": self.mean_prediction_shift,
            "mean_shift_tracking_error": self.mean_shift_tracking_error,
            "loss_volatility": self.loss_volatility,
        }


@dataclass(frozen=True)
class ProxyStateDynamics:
    transition_count: int
    mean_target_shift: float
    max_target_shift: float
    target_top_label_switch_rate: float
    method_dynamics: tuple[MethodProxyStateDynamics, ...]
    scope: str = (
        "Proxy-state dynamics describe changes in declared weak targets and "
        "prediction streams; they do not reveal latent intent directly."
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "transition_count": self.transition_count,
            "mean_target_shift": self.mean_target_shift,
            "max_target_shift": self.max_target_shift,
            "target_top_label_switch_rate": self.target_top_label_switch_rate,
            "method_dynamics": [item.to_dict() for item in self.method_dynamics],
            "scope": self.scope,
        }


@dataclass(frozen=True)
class EvaluationDiagnostics:
    sample_count: int
    method_count: int
    method_diagnostics: tuple[MethodDiagnostics, ...]
    bootstrap_ranking: BootstrapRankingDiagnostics
    proxy_state_dynamics: ProxyStateDynamics
    scope: str = (
        "Diagnostics are computed against declared weak target distributions, "
        "not directly observed true intent."
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "sample_count": self.sample_count,
            "method_count": self.method_count,
            "method_diagnostics": [
                diagnostics.to_dict() for diagnostics in self.method_diagnostics
            ],
            "bootstrap_ranking": self.bootstrap_ranking.to_dict(),
            "proxy_state_dynamics": self.proxy_state_dynamics.to_dict(),
            "scope": self.scope,
        }


def evaluation_diagnostics(
    targets: tuple[WeakTarget, ...],
    predictions: tuple[Prediction, ...],
    *,
    n_resamples: int = 200,
    seed: int = 0,
) -> EvaluationDiagnostics:
    if not targets:
        raise ValueError("diagnostics require at least one target")
    if n_resamples <= 0:
        raise ValueError("n_resamples must be positive")

    targets_by_id = {target.sample_id: target for target in targets}
    predictions_by_method = _predictions_by_method(predictions)
    if not predictions_by_method:
        raise ValueError("diagnostics require at least one prediction method")
    _require_complete_predictions(targets_by_id, predictions_by_method)

    ordered_sample_ids = tuple(target.sample_id for target in targets)
    losses_by_method = {
        method_id: tuple(
            log_loss(targets_by_id[sample_id], predictions_by_id[sample_id])
            for sample_id in ordered_sample_ids
        )
        for method_id, predictions_by_id in predictions_by_method.items()
    }
    method_diagnostics = tuple(
        _method_diagnostics(
            method_id,
            targets_by_id,
            predictions_by_id,
            ordered_sample_ids,
        )
        for method_id, predictions_by_id in sorted(predictions_by_method.items())
    )
    return EvaluationDiagnostics(
        sample_count=len(targets),
        method_count=len(method_diagnostics),
        method_diagnostics=method_diagnostics,
        bootstrap_ranking=_bootstrap_ranking(
            losses_by_method,
            sample_count=len(targets),
            n_resamples=n_resamples,
            seed=seed,
        ),
        proxy_state_dynamics=_proxy_state_dynamics(
            targets_by_id,
            predictions_by_method,
            ordered_sample_ids,
        ),
    )


def render_evaluation_diagnostics_markdown(
    diagnostics: EvaluationDiagnostics,
) -> str:
    lines = [
        "# Evaluation Diagnostics",
        "",
        f"**Samples:** {diagnostics.sample_count}",
        "",
        f"**Methods:** {diagnostics.method_count}",
        "",
        "## Method Diagnostics",
        "| Method | Log loss | Brier | Proxy top-1 accuracy |",
        "|---|---:|---:|---:|",
    ]
    for item in diagnostics.method_diagnostics:
        lines.append(
            "| "
            f"{item.method_id} | "
            f"{item.mean_log_loss:.3f} | "
            f"{item.mean_brier_score:.3f} | "
            f"{item.proxy_top1_accuracy:.3f} |"
        )
    bootstrap = diagnostics.bootstrap_ranking
    lines.extend(
        [
            "",
            "## Bootstrap Ranking Stability",
            f"- Resamples: {bootstrap.n_resamples}",
            f"- Seed: {bootstrap.seed}",
        ]
    )
    for method_id, frequency in sorted(bootstrap.top_method_frequencies.items()):
        mean_rank = bootstrap.mean_ranks[method_id]
        lines.append(
            f"- {method_id}: top frequency {frequency:.3f}, mean rank {mean_rank:.3f}"
        )
    dynamics = diagnostics.proxy_state_dynamics
    lines.extend(
        [
            "",
            "## Proxy State Dynamics",
            f"- Transitions: {dynamics.transition_count}",
            f"- Mean target shift: {dynamics.mean_target_shift:.3f}",
            f"- Max target shift: {dynamics.max_target_shift:.3f}",
            (
                "- Target top-label switch rate: "
                f"{dynamics.target_top_label_switch_rate:.3f}"
            ),
            "| Method | Prediction shift | Shift tracking error | Loss volatility |",
            "|---|---:|---:|---:|",
        ]
    )
    for item in dynamics.method_dynamics:
        lines.append(
            "| "
            f"{item.method_id} | "
            f"{item.mean_prediction_shift:.3f} | "
            f"{item.mean_shift_tracking_error:.3f} | "
            f"{item.loss_volatility:.3f} |"
        )
    lines.extend(["", "## Scope", f"- {diagnostics.scope}"])
    lines.append(f"- {dynamics.scope}")
    return "\n".join(lines) + "\n"


def _method_diagnostics(
    method_id: str,
    targets_by_id: dict[str, WeakTarget],
    predictions_by_id: dict[str, Prediction],
    ordered_sample_ids: tuple[str, ...],
) -> MethodDiagnostics:
    losses = []
    brier_scores = []
    top1_hits = []
    for sample_id in ordered_sample_ids:
        target = targets_by_id[sample_id]
        prediction = predictions_by_id[sample_id]
        losses.append(log_loss(target, prediction))
        brier_scores.append(brier_score(target, prediction))
        target_top_label = _top_label(target.probabilities)
        prediction_top_label = _top_label(prediction.probabilities)
        top1_hits.append(1.0 if target_top_label == prediction_top_label else 0.0)
    return MethodDiagnostics(
        method_id=method_id,
        sample_count=len(ordered_sample_ids),
        mean_log_loss=sum(losses) / len(losses),
        mean_brier_score=sum(brier_scores) / len(brier_scores),
        proxy_top1_accuracy=sum(top1_hits) / len(top1_hits),
    )


def _bootstrap_ranking(
    losses_by_method: dict[str, tuple[float, ...]],
    *,
    sample_count: int,
    n_resamples: int,
    seed: int,
) -> BootstrapRankingDiagnostics:
    method_ids = tuple(sorted(losses_by_method))
    rng = random.Random(seed)
    top_counts = {method_id: 0 for method_id in method_ids}
    rank_totals = {method_id: 0.0 for method_id in method_ids}
    for _ in range(n_resamples):
        sample_indices = tuple(rng.randrange(sample_count) for _ in range(sample_count))
        ranking = tuple(
            method_id
            for method_id, _ in sorted(
                (
                    (
                        method_id,
                        sum(losses[index] for index in sample_indices)
                        / len(sample_indices),
                    )
                    for method_id, losses in losses_by_method.items()
                ),
                key=lambda item: (item[1], item[0]),
            )
        )
        top_counts[ranking[0]] += 1
        for rank, method_id in enumerate(ranking, start=1):
            rank_totals[method_id] += rank
    return BootstrapRankingDiagnostics(
        n_resamples=n_resamples,
        seed=seed,
        top_method_frequencies={
            method_id: top_counts[method_id] / n_resamples for method_id in method_ids
        },
        mean_ranks={
            method_id: rank_totals[method_id] / n_resamples for method_id in method_ids
        },
    )


def _proxy_state_dynamics(
    targets_by_id: dict[str, WeakTarget],
    predictions_by_method: dict[str, dict[str, Prediction]],
    ordered_sample_ids: tuple[str, ...],
) -> ProxyStateDynamics:
    transition_pairs = tuple(zip(ordered_sample_ids, ordered_sample_ids[1:]))
    if not transition_pairs:
        return ProxyStateDynamics(
            transition_count=0,
            mean_target_shift=0.0,
            max_target_shift=0.0,
            target_top_label_switch_rate=0.0,
            method_dynamics=tuple(
                MethodProxyStateDynamics(method_id, 0.0, 0.0, 0.0)
                for method_id in sorted(predictions_by_method)
            ),
        )

    target_shifts = tuple(
        _distribution_shift(
            targets_by_id[left_id].probabilities,
            targets_by_id[right_id].probabilities,
        )
        for left_id, right_id in transition_pairs
    )
    target_switches = tuple(
        1.0
        if _top_label(targets_by_id[left_id].probabilities)
        != _top_label(targets_by_id[right_id].probabilities)
        else 0.0
        for left_id, right_id in transition_pairs
    )
    return ProxyStateDynamics(
        transition_count=len(transition_pairs),
        mean_target_shift=sum(target_shifts) / len(target_shifts),
        max_target_shift=max(target_shifts),
        target_top_label_switch_rate=sum(target_switches) / len(target_switches),
        method_dynamics=tuple(
            _method_proxy_state_dynamics(
                method_id,
                predictions_by_id,
                targets_by_id,
                ordered_sample_ids,
                target_shifts,
            )
            for method_id, predictions_by_id in sorted(predictions_by_method.items())
        ),
    )


def _method_proxy_state_dynamics(
    method_id: str,
    predictions_by_id: dict[str, Prediction],
    targets_by_id: dict[str, WeakTarget],
    ordered_sample_ids: tuple[str, ...],
    target_shifts: tuple[float, ...],
) -> MethodProxyStateDynamics:
    transition_pairs = tuple(zip(ordered_sample_ids, ordered_sample_ids[1:]))
    prediction_shifts = tuple(
        _distribution_shift(
            predictions_by_id[left_id].probabilities,
            predictions_by_id[right_id].probabilities,
        )
        for left_id, right_id in transition_pairs
    )
    losses = tuple(
        log_loss(targets_by_id[sample_id], predictions_by_id[sample_id])
        for sample_id in ordered_sample_ids
    )
    loss_deltas = tuple(
        abs(right_loss - left_loss)
        for left_loss, right_loss in zip(losses, losses[1:])
    )
    tracking_errors = tuple(
        abs(prediction_shift - target_shift)
        for prediction_shift, target_shift in zip(prediction_shifts, target_shifts)
    )
    return MethodProxyStateDynamics(
        method_id=method_id,
        mean_prediction_shift=sum(prediction_shifts) / len(prediction_shifts),
        mean_shift_tracking_error=sum(tracking_errors) / len(tracking_errors),
        loss_volatility=sum(loss_deltas) / len(loss_deltas),
    )


def _predictions_by_method(
    predictions: tuple[Prediction, ...],
) -> dict[str, dict[str, Prediction]]:
    grouped: dict[str, dict[str, Prediction]] = {}
    for prediction in predictions:
        grouped.setdefault(prediction.method_id, {})[prediction.sample_id] = prediction
    return grouped


def _require_complete_predictions(
    targets_by_id: dict[str, WeakTarget],
    predictions_by_method: dict[str, dict[str, Prediction]],
) -> None:
    target_ids = frozenset(targets_by_id)
    for method_id, predictions_by_id in predictions_by_method.items():
        prediction_ids = frozenset(predictions_by_id)
        if prediction_ids == target_ids:
            continue
        missing = sorted(target_ids - prediction_ids)
        extra = sorted(prediction_ids - target_ids)
        parts = []
        if missing:
            parts.append(f"missing predictions: {', '.join(missing)}")
        if extra:
            parts.append(f"unknown predictions: {', '.join(extra)}")
        raise ValueError(
            f"incomplete diagnostics predictions for {method_id}: {'; '.join(parts)}"
        )


def _top_label(probabilities: dict[str, float]) -> str:
    return min(
        probabilities,
        key=lambda label: (-probabilities[label], label),
    )


def _distribution_shift(
    left: dict[str, float],
    right: dict[str, float],
) -> float:
    labels = set(left) | set(right)
    midpoint = {
        label: (left.get(label, 0.0) + right.get(label, 0.0)) / 2.0
        for label in labels
    }
    return 0.5 * _kl_to_midpoint(left, midpoint, labels) + 0.5 * _kl_to_midpoint(
        right,
        midpoint,
        labels,
    )


def _kl_to_midpoint(
    values: dict[str, float],
    midpoint: dict[str, float],
    labels: set[str],
) -> float:
    total = 0.0
    for label in labels:
        probability = values.get(label, 0.0)
        if probability <= 0.0:
            continue
        total += probability * math.log(probability / max(midpoint[label], 1e-12))
    return total
