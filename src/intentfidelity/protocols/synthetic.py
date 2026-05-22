from __future__ import annotations

from intentfidelity.baselines import (
    synthetic_shift_examples,
    run_centroid_baseline,
)
from intentfidelity.baselines.transforms import identity_transform, session_centering_transform
from intentfidelity.labels import WeakTarget
from intentfidelity.metrics import MethodScore, intent_fidelity_loss, ranking_disagreement
from intentfidelity.protocols.schemas import EvalResult, ProtocolType


def synthetic_baseline_eval() -> EvalResult:
    train, test = synthetic_shift_examples()
    targets = tuple(
        WeakTarget(
            sample_id=example.sample_id,
            probabilities={label: 1.0 if label == example.label else 0.0 for label in ("a", "b")},
            source_type="synthetic_label",
        )
        for example in test
    )
    runs = (
        run_centroid_baseline(train, test, method_id="identity_centroid", transform_factory=identity_transform),
        run_centroid_baseline(train, test, method_id="session_centered_centroid", transform_factory=session_centering_transform),
    )
    scores = tuple(_score_run(run.predictions, targets) for run in runs)
    return EvalResult(
        dataset_id="synthetic_shift",
        protocol=ProtocolType.HELD_OUT_SESSION,
        method_scores=scores,
        primary_metric="intent_fidelity_log_loss",
        ranking_disagreement=ranking_disagreement(scores),
        metadata={"evidence_scope": "synthetic sanity check"},
    )


def _score_run(predictions, targets: tuple[WeakTarget, ...]) -> MethodScore:
    target_by_id = {target.sample_id: target for target in targets}
    losses = [
        intent_fidelity_loss(target_by_id[prediction.sample_id], prediction).value
        for prediction in predictions
    ]
    mean_loss = sum(losses) / len(losses)
    return MethodScore(predictions[0].method_id, mean_loss, mean_loss)

