from intentfidelity.metrics import MethodScore
from intentfidelity.protocols import held_out_session_result
from intentfidelity.reports import (
    DatasetCard,
    EvalCard,
    default_claim_card,
    render_json,
    render_markdown,
)
from intentfidelity.resources import get_manifest


def test_dataset_card_renders_manifest_proxy_sources() -> None:
    card = DatasetCard.from_manifest(get_manifest("falcon_h2"))
    markdown = render_markdown(card)

    assert "FALCON H2" in markdown
    assert "task prompts" in markdown
    assert "direct access to intent" in markdown


def test_eval_card_uses_weak_target_summary() -> None:
    result = held_out_session_result(
        "falcon_h2",
        (MethodScore("baseline", 0.1, 0.2),),
    )
    card = EvalCard.from_result(result)

    assert "declared weak target" in card.summary
    assert card.method_count == 1


def test_claim_card_json_keeps_claim_narrow() -> None:
    rendered = render_json(default_claim_card())

    assert "can be insufficient" in rendered
    assert "No direct access to true intent" in rendered

