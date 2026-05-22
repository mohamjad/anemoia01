from __future__ import annotations

from intentfidelity.protocols import EvalResult


def render_naturalistic_markdown(result: EvalResult) -> str:
    summary = result.metadata.get("proxy_summary", {})
    lines = [
        "# Naturalistic Weak-Label Evaluation",
        "",
        f"**Dataset:** {result.dataset_id}",
        "",
        f"**Primary metric:** {result.primary_metric}",
        "",
        "## Proxy Summary",
        f"- Events: {summary.get('event_count', 'unknown')}",
        f"- Sessions: {summary.get('session_count', 'unknown')}",
        f"- Mean confidence: {_format_float(summary.get('mean_confidence'))}",
        f"- Mean ambiguity: {_format_float(summary.get('mean_ambiguity'))}",
        "",
        "## Method Scores",
    ]
    for score in sorted(result.method_scores, key=lambda item: item.intent_fidelity_score):
        lines.append(f"- {score.method_id}: {score.intent_fidelity_score:.3f}")
    lines.extend(
        [
            "",
            "## Scope",
            "- Scores use behavioral outputs and timing windows as intent proxies.",
            "- Naturalistic weak labels can remain behaviorally confounded.",
        ]
    )
    return "\n".join(lines) + "\n"


def _format_float(value: object) -> str:
    return f"{value:.3f}" if isinstance(value, float) else "unknown"
