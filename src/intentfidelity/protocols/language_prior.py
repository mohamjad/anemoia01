from __future__ import annotations

from intentfidelity.metrics import LanguagePriorAttribution, language_prior_attribution
from intentfidelity.protocols.schemas import EvalResult


def language_prior_report(
    result: EvalResult,
    *,
    lm_light_method_id: str = "lm_light",
    lm_heavy_method_id: str = "lm_heavy",
) -> LanguagePriorAttribution:
    scores = {score.method_id: score for score in result.method_scores}
    if lm_light_method_id not in scores:
        raise ValueError(f"missing method score: {lm_light_method_id}")
    if lm_heavy_method_id not in scores:
        raise ValueError(f"missing method score: {lm_heavy_method_id}")
    return language_prior_attribution(
        scores[lm_light_method_id],
        scores[lm_heavy_method_id],
    )

