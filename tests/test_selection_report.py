from intentfidelity.labels import P300SelectionEvent, Prediction
from intentfidelity.protocols import selection_eval_result
from intentfidelity.reports.selection import render_selection_markdown


def test_render_selection_markdown_includes_proxy_summary() -> None:
    result = selection_eval_result(
        (P300SelectionEvent("s0", "A", ("A", "B"), 0.9, "A", "session-1"),),
        {"decoder": (Prediction("s0", {"A": 0.9, "B": 0.1}, "decoder"),)},
        dataset_id="bigp3bci",
    )

    markdown = render_selection_markdown(result)

    assert "Selection Evaluation" in markdown
    assert "Observed selection accuracy: 1.000" in markdown
    assert "decoder:" in markdown
    assert "intent proxies" in markdown
