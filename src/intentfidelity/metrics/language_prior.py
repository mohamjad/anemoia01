from __future__ import annotations

from dataclasses import dataclass

from intentfidelity.metrics.comparison import MethodScore


@dataclass(frozen=True)
class LanguagePriorAttribution:
    lm_light_method_id: str
    lm_heavy_method_id: str
    light_intent_fidelity_score: float
    heavy_intent_fidelity_score: float
    heavy_minus_light: float
    interpretation: str

    def to_dict(self) -> dict[str, float | str]:
        return {
            "lm_light_method_id": self.lm_light_method_id,
            "lm_heavy_method_id": self.lm_heavy_method_id,
            "light_intent_fidelity_score": self.light_intent_fidelity_score,
            "heavy_intent_fidelity_score": self.heavy_intent_fidelity_score,
            "heavy_minus_light": self.heavy_minus_light,
            "interpretation": self.interpretation,
        }


def language_prior_attribution(
    lm_light: MethodScore,
    lm_heavy: MethodScore,
) -> LanguagePriorAttribution:
    delta = lm_heavy.intent_fidelity_score - lm_light.intent_fidelity_score
    interpretation = (
        "lm_heavy_worse"
        if delta > 0
        else "lm_heavy_better"
        if delta < 0
        else "no_difference"
    )
    return LanguagePriorAttribution(
        lm_light_method_id=lm_light.method_id,
        lm_heavy_method_id=lm_heavy.method_id,
        light_intent_fidelity_score=lm_light.intent_fidelity_score,
        heavy_intent_fidelity_score=lm_heavy.intent_fidelity_score,
        heavy_minus_light=delta,
        interpretation=interpretation,
    )
