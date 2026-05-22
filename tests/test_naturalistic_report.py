from intentfidelity.labels import NaturalisticEvent, Prediction
from intentfidelity.protocols import naturalistic_eval_result
from intentfidelity.reports import render_naturalistic_markdown


def test_render_naturalistic_markdown_includes_proxy_summary() -> None:
    result = naturalistic_eval_result(
        (NaturalisticEvent("s0", "reach", ("reach", "rest"), 0.75, "session-1"),),
        {"decoder": (Prediction("s0", {"reach": 0.75, "rest": 0.25}, "decoder"),)},
        dataset_id="ajile12",
    )

    markdown = render_naturalistic_markdown(result)

    assert "Naturalistic Weak-Label Evaluation" in markdown
    assert "Mean confidence: 0.750" in markdown
    assert "decoder:" in markdown
    assert "behaviorally confounded" in markdown
