from intentfidelity.metrics import MethodScore
from intentfidelity.protocols import EvalResult, ProtocolType
from intentfidelity.protocols.language_prior import language_prior_report


def test_language_prior_report_extracts_method_scores() -> None:
    result = EvalResult(
        dataset_id="willett2023",
        protocol=ProtocolType.COMMUNICATION,
        method_scores=(
            MethodScore("lm_light", 0.2, 0.2),
            MethodScore("lm_heavy", 0.1, 0.4),
        ),
        primary_metric="character_error_rate",
    )

    report = language_prior_report(result)

    assert report.heavy_minus_light == 0.2

