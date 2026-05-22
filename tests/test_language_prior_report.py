from intentfidelity.metrics import MethodScore, language_prior_attribution
from intentfidelity.reports import render_language_prior_markdown


def test_render_language_prior_markdown_keeps_scope_narrow() -> None:
    attribution = language_prior_attribution(
        MethodScore("lm_light", 0.2, 0.2),
        MethodScore("lm_heavy", 0.1, 0.4),
    )

    markdown = render_language_prior_markdown(attribution)

    assert "Language Prior Attribution" in markdown
    assert "**Heavy minus light:** 0.200" in markdown
    assert "declared transcript proxies" in markdown
    assert "does not isolate language-model effects" in markdown
