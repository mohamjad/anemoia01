from __future__ import annotations

from intentfidelity.metrics import LanguagePriorAttribution


def render_language_prior_markdown(attribution: LanguagePriorAttribution) -> str:
    return "\n".join(
        [
            "# Language Prior Attribution",
            "",
            f"**LM-light method:** {attribution.lm_light_method_id}",
            "",
            f"**LM-heavy method:** {attribution.lm_heavy_method_id}",
            "",
            f"**Heavy minus light:** {attribution.heavy_minus_light:.3f}",
            "",
            f"**Interpretation:** {attribution.interpretation}",
            "",
            "## Scope",
            "- Attribution compares method scores under declared transcript proxies.",
            "- It does not isolate language-model effects without matched ablations.",
        ]
    ) + "\n"
