from intentfidelity.labels import (
    AuthorizationEvent,
    AuthorizationState,
    Prediction,
)
from intentfidelity.protocols import authorization_eval_result
from intentfidelity.reports.authorization import render_authorization_markdown


def test_render_authorization_markdown_describes_uncertainty_scope() -> None:
    result = authorization_eval_result(
        (AuthorizationEvent("s0", AuthorizationState.UNCERTAIN),),
        {
            "baseline": (
                Prediction("s0", {"authorized": 0.5, "not_authorized": 0.5}, "baseline"),
            )
        },
        dataset_id="kunz2025",
    )

    markdown = render_authorization_markdown(result)

    assert "Authorization Evaluation" in markdown
    assert "baseline:" in markdown
    assert "weak target distributions" in markdown
    assert "proxy uncertainty" in markdown
