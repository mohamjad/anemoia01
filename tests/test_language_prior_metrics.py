from intentfidelity.metrics import MethodScore
from intentfidelity.metrics.language_prior import language_prior_attribution


def test_language_prior_attribution_reports_heavy_minus_light_delta() -> None:
    report = language_prior_attribution(
        MethodScore("lm_light", 0.1, 0.2),
        MethodScore("lm_heavy", 0.1, 0.4),
    )

    assert report.heavy_minus_light == 0.2
    assert report.interpretation == "lm_heavy_worse"

