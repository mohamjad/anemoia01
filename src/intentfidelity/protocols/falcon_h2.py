from __future__ import annotations

from intentfidelity.baselines import proxy_oracle_prediction, uniform_prediction
from intentfidelity.ingest import IngestSplit, load_falcon_h2_trials
from intentfidelity.labels import WeakTarget, weak_targets_from_trials
from intentfidelity.metrics import (
    DistributionMetric,
    MethodScore,
    intent_fidelity_loss,
    ranking_disagreement,
)
from intentfidelity.protocols.schemas import EvalResult, ProtocolType


def falcon_h2_targets_from_file(path) -> tuple[WeakTarget, ...]:
    split = _split_from_path(path)
    trials = load_falcon_h2_trials(path, split)
    return weak_targets_from_trials(trials)


def falcon_h2_baseline_eval(path) -> EvalResult:
    targets = falcon_h2_targets_from_file(path)
    if not targets:
        raise ValueError("cannot evaluate FALCON H2 file without weak targets")

    scores = (
        _score_baseline("proxy_oracle", targets),
        _score_baseline("uniform_prior", targets),
    )
    return EvalResult(
        dataset_id="falcon_h2",
        protocol=ProtocolType.HELD_OUT_SESSION,
        method_scores=scores,
        primary_metric="intent_fidelity_log_loss",
        ranking_disagreement=ranking_disagreement(scores),
        metadata={
            "source_path": str(path),
            "baseline_scope": "target-construction sanity baselines",
        },
    )


def falcon_h2_prediction_eval(
    path,
    predictions_by_method: dict[str, tuple],
) -> EvalResult:
    targets = falcon_h2_targets_from_file(path)
    if not targets:
        raise ValueError("cannot evaluate FALCON H2 file without weak targets")

    scores = tuple(
        _score_predictions(method_id, targets, predictions)
        for method_id, predictions in sorted(predictions_by_method.items())
    )
    return EvalResult(
        dataset_id="falcon_h2",
        protocol=ProtocolType.HELD_OUT_SESSION,
        method_scores=scores,
        primary_metric="intent_fidelity_log_loss",
        ranking_disagreement=ranking_disagreement(scores) if len(scores) > 1 else None,
        metadata={
            "source_path": str(path),
            "baseline_scope": "external predictions against declared weak targets",
        },
    )


def _score_baseline(method_id: str, targets: tuple[WeakTarget, ...]) -> MethodScore:
    metrics: list[DistributionMetric] = []
    for target in targets:
        prediction = (
            proxy_oracle_prediction(target, method_id)
            if method_id == "proxy_oracle"
            else uniform_prediction(target, method_id)
        )
        metrics.append(intent_fidelity_loss(target, prediction))
    mean_loss = sum(metric.value for metric in metrics) / len(metrics)
    return MethodScore(
        method_id=method_id,
        conventional_score=mean_loss,
        intent_fidelity_score=mean_loss,
    )


def _score_predictions(method_id: str, targets: tuple[WeakTarget, ...], predictions) -> MethodScore:
    predictions_by_sample = {prediction.sample_id: prediction for prediction in predictions}
    losses: list[float] = []
    for target in targets:
        prediction = predictions_by_sample.get(target.sample_id)
        if prediction is None:
            raise ValueError(f"missing prediction for sample_id: {target.sample_id}")
        losses.append(intent_fidelity_loss(target, prediction).value)
    mean_loss = sum(losses) / len(losses)
    return MethodScore(method_id=method_id, conventional_score=mean_loss, intent_fidelity_score=mean_loss)


def _split_from_path(path) -> IngestSplit:
    text = str(path)
    if "held-out-calib" in text or "held_out_calib" in text:
        return IngestSplit.HELD_OUT_CALIB
    if "minival" in text:
        return IngestSplit.MINIVAL
    return IngestSplit.HELD_IN_CALIB
