from intentfidelity.labels import TextPrediction, TextTarget
from intentfidelity.protocols import communication_eval_result
from intentfidelity.reports import render_communication_markdown


def test_render_communication_markdown_describes_proxy_scope() -> None:
    result = communication_eval_result(
        (TextTarget("s0", "open", "prompt"),),
        (TextPrediction("s0", "open", "baseline"),),
        dataset_id="card2024",
    )

    markdown = render_communication_markdown(result)

    assert "Communication Evaluation" in markdown
    assert "baseline: 0.000" in markdown
    assert "declared transcript proxies" in markdown
    assert "direct access to true intent" in markdown
