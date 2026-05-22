from __future__ import annotations

from intentfidelity.protocols.comparison import MethodComparisonReport


def render_comparison_table(report: MethodComparisonReport) -> str:
    lines = [
        "metric,value",
        f"dataset_id,{report.dataset_id}",
        f"protocol,{report.protocol}",
        f"kendall_tau_distance,{report.ranking.kendall_tau_distance}",
        f"reversal_rate,{report.ranking.reversal_rate:.6f}",
        f"over_adaptation_events,{len(report.over_adaptation_events)}",
    ]
    return "\n".join(lines) + "\n"

