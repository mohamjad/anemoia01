"""Evaluation protocol schemas."""

from intentfidelity.protocols.schemas import (
    EvalResult,
    ProtocolType,
    authorization_result,
    communication_result,
    few_shot_recalibration_result,
    held_out_session_result,
    naturalistic_weak_label_result,
    selection_result,
)
from intentfidelity.protocols.io import load_eval_result, save_eval_result
from intentfidelity.protocols.falcon_h2 import (
    falcon_h2_baseline_eval,
    falcon_h2_feature_baseline_eval,
    falcon_h2_prediction_eval,
    falcon_h2_targets_from_file,
)
from intentfidelity.protocols.comparison import (
    MethodComparisonReport,
    compare_eval_results,
)
from intentfidelity.protocols.synthetic import synthetic_baseline_eval
from intentfidelity.protocols.communication import communication_eval_result
from intentfidelity.protocols.language_prior import language_prior_report
from intentfidelity.protocols.authorization import authorization_eval_result
from intentfidelity.protocols.naturalistic import naturalistic_eval_result

__all__ = [
    "EvalResult",
    "MethodComparisonReport",
    "ProtocolType",
    "authorization_result",
    "authorization_eval_result",
    "communication_result",
    "communication_eval_result",
    "compare_eval_results",
    "few_shot_recalibration_result",
    "falcon_h2_baseline_eval",
    "falcon_h2_feature_baseline_eval",
    "falcon_h2_prediction_eval",
    "falcon_h2_targets_from_file",
    "held_out_session_result",
    "load_eval_result",
    "language_prior_report",
    "naturalistic_weak_label_result",
    "naturalistic_eval_result",
    "save_eval_result",
    "selection_result",
    "synthetic_baseline_eval",
]
