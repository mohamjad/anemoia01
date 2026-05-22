from __future__ import annotations

from intentfidelity.protocols.comparison import MethodComparisonReport


def render_comparison_markdown(report: MethodComparisonReport) -> str:
    lines = [
        "# Method Comparison Report",
        "",
        f"**Dataset:** {report.dataset_id}",
        "",
        f"**Protocol:** {report.protocol}",
        "",
        "## Rankings",
        f"- Conventional: {' -> '.join(report.ranking.conventional_ranking)}",
        f"- Intent fidelity: {' -> '.join(report.ranking.intent_fidelity_ranking)}",
        f"- Kendall tau distance: {report.ranking.kendall_tau_distance}",
        f"- Reversal rate: {report.ranking.reversal_rate:.3f}",
        "",
        "## Over-Adaptation",
    ]
    if not report.over_adaptation_events:
        lines.append("- None detected")
    else:
        lines.extend(
            f"- {event.method_id}: {event.reason}"
            for event in report.over_adaptation_events
        )
    return "\n".join(lines) + "\n"
