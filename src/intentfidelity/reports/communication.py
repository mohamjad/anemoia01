from __future__ import annotations

from intentfidelity.protocols import EvalResult


def render_communication_markdown(result: EvalResult) -> str:
    lines = [
        "# Communication Evaluation",
        "",
        f"**Dataset:** {result.dataset_id}",
        "",
        f"**Primary metric:** {result.primary_metric}",
        "",
        "## Method Scores",
    ]
    for score in sorted(result.method_scores, key=lambda item: item.intent_fidelity_score):
        lines.append(f"- {score.method_id}: {score.intent_fidelity_score:.3f}")
    lines.extend(
        [
            "",
            "## Scope",
            "- Scores compare decoded text against declared transcript proxies.",
            "- This report does not claim direct access to true intent.",
        ]
    )
    return "\n".join(lines) + "\n"
