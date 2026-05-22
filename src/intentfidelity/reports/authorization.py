from __future__ import annotations

from intentfidelity.protocols import EvalResult


def render_authorization_markdown(result: EvalResult) -> str:
    lines = [
        "# Authorization Evaluation",
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
            "- Scores use authorization states as weak target distributions.",
            "- Uncertain authorization states remain explicit proxy uncertainty.",
        ]
    )
    return "\n".join(lines) + "\n"
