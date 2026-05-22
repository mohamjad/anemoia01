"""Metric implementations."""

from intentfidelity.metrics.scoring import (
    DistributionMetric,
    brier_score,
    energy_score,
    intent_fidelity_loss,
    jensen_shannon_divergence,
    kl_divergence,
    log_loss,
    mean_metric,
)
from intentfidelity.metrics.comparison import (
    MethodScore,
    OverAdaptationEvent,
    RankingDisagreement,
    detect_over_adaptation,
    expected_calibration_error,
    ranking_disagreement,
)
from intentfidelity.metrics.evaluation import score_predictions
from intentfidelity.metrics.method_scores import method_scores_from_metrics
from intentfidelity.metrics.edit_distance import edit_distance, normalized_edit_distance
from intentfidelity.metrics.text import character_error_rate, word_error_rate
from intentfidelity.metrics.language_prior import (
    LanguagePriorAttribution,
    language_prior_attribution,
)
from intentfidelity.metrics.naturalistic import (
    NaturalisticProxySummary,
    summarize_naturalistic_proxy,
)
from intentfidelity.metrics.selection import (
    SelectionProxySummary,
    summarize_selection_proxy,
)

__all__ = [
    "DistributionMetric",
    "MethodScore",
    "OverAdaptationEvent",
    "RankingDisagreement",
    "LanguagePriorAttribution",
    "NaturalisticProxySummary",
    "SelectionProxySummary",
    "brier_score",
    "detect_over_adaptation",
    "edit_distance",
    "energy_score",
    "expected_calibration_error",
    "intent_fidelity_loss",
    "jensen_shannon_divergence",
    "kl_divergence",
    "language_prior_attribution",
    "log_loss",
    "mean_metric",
    "method_scores_from_metrics",
    "normalized_edit_distance",
    "ranking_disagreement",
    "score_predictions",
    "summarize_naturalistic_proxy",
    "summarize_selection_proxy",
    "character_error_rate",
    "word_error_rate",
]
