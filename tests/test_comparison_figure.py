from intentfidelity.figures.comparison import render_comparison_table
from intentfidelity.metrics import MethodScore
from intentfidelity.protocols import EvalResult, ProtocolType, compare_eval_results


def test_render_comparison_table_outputs_csv_like_summary() -> None:
    result = EvalResult(
        dataset_id="falcon_h2",
        protocol=ProtocolType.HELD_OUT_SESSION,
        method_scores=(MethodScore("a", 0.1, 0.2), MethodScore("b", 0.2, 0.1)),
        primary_metric="intent_fidelity_log_loss",
    )

    rendered = render_comparison_table(compare_eval_results(result))

    assert "reversal_rate,1.000000" in rendered

