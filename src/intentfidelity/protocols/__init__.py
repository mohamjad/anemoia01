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
from intentfidelity.protocols.artifacts import (
    ArtifactBundle,
    ArtifactValidationIssue,
    ArtifactValidationReport,
    ArtifactValidationSeverity,
    EvidenceLevel,
    GeneratedArtifact,
    load_artifact_bundle,
    save_artifact_bundle,
    validate_artifact_bundle,
)
from intentfidelity.protocols.io import load_eval_result, save_eval_result
from intentfidelity.protocols.falcon_h2 import (
    falcon_h2_baseline_eval,
    falcon_h2_baseline_predictions,
    falcon_h2_baseline_scores,
    falcon_h2_feature_baseline_eval,
    falcon_h2_prediction_eval,
    falcon_h2_prediction_result_from_targets,
    falcon_h2_split_from_path,
    falcon_h2_targets_from_file,
)
from intentfidelity.protocols.falcon_h2_artifacts import (
    validate_falcon_h2_artifact_bundle,
    write_falcon_h2_artifact_bundle,
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
from intentfidelity.protocols.selection import selection_eval_result

__all__ = [
    "EvalResult",
    "ArtifactBundle",
    "ArtifactValidationIssue",
    "ArtifactValidationReport",
    "ArtifactValidationSeverity",
    "EvidenceLevel",
    "GeneratedArtifact",
    "MethodComparisonReport",
    "ProtocolType",
    "authorization_result",
    "authorization_eval_result",
    "communication_result",
    "communication_eval_result",
    "compare_eval_results",
    "few_shot_recalibration_result",
    "falcon_h2_baseline_eval",
    "falcon_h2_baseline_predictions",
    "falcon_h2_baseline_scores",
    "falcon_h2_feature_baseline_eval",
    "falcon_h2_prediction_eval",
    "falcon_h2_prediction_result_from_targets",
    "falcon_h2_split_from_path",
    "falcon_h2_targets_from_file",
    "held_out_session_result",
    "load_artifact_bundle",
    "load_eval_result",
    "language_prior_report",
    "naturalistic_weak_label_result",
    "naturalistic_eval_result",
    "save_artifact_bundle",
    "save_eval_result",
    "selection_result",
    "selection_eval_result",
    "synthetic_baseline_eval",
    "validate_artifact_bundle",
    "validate_falcon_h2_artifact_bundle",
    "write_falcon_h2_artifact_bundle",
]
