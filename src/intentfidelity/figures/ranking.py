from __future__ import annotations

from intentfidelity.protocols import EvalResult


def render_ranking_reversal(result: EvalResult) -> str:
    if result.ranking_disagreement is None:
        return "No ranking disagreement field is present in this eval result.\n"

    disagreement = result.ranking_disagreement
    lines = [
        "Ranking Reversal",
        f"Dataset: {result.dataset_id}",
        f"Protocol: {result.protocol.value}",
        "Conventional ranking: "
        + " -> ".join(disagreement.conventional_ranking),
        "Intent-fidelity ranking: "
        + " -> ".join(disagreement.intent_fidelity_ranking),
        f"Kendall tau distance: {disagreement.kendall_tau_distance}",
    ]
    return "\n".join(lines) + "\n"

