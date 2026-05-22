from intentfidelity.metrics import MethodScore
from intentfidelity.protocols import EvalResult, ProtocolType, compare_eval_results
from intentfidelity.reports.comparison import render_comparison_markdown


def test_render_comparison_markdown_includes_rankings() -> None:
    result = EvalResult(
        dataset_id="falcon_h2",
        protocol=ProtocolType.HELD_OUT_SESSION,
        method_scores=(
            MethodScore("a", 0.1, 0.4),
            MethodScore("b", 0.3, 0.2),
        ),
        primary_metric="intent_fidelity_log_loss",
    )

    markdown = render_comparison_markdown(compare_eval_results(result))

    assert "Conventional: a -> b" in markdown
    assert "Intent fidelity: b -> a" in markdown

