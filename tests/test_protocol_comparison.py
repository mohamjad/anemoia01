from intentfidelity.metrics import MethodScore
from intentfidelity.protocols import EvalResult, ProtocolType
from intentfidelity.protocols.comparison import compare_eval_results


def test_compare_eval_results_reports_ranking_disagreement() -> None:
    result = EvalResult(
        dataset_id="falcon_h2",
        protocol=ProtocolType.HELD_OUT_SESSION,
        method_scores=(
            MethodScore("a", conventional_score=0.1, intent_fidelity_score=0.4),
            MethodScore("b", conventional_score=0.3, intent_fidelity_score=0.2),
        ),
        primary_metric="intent_fidelity_log_loss",
    )

    report = compare_eval_results(result)

    assert report.ranking.has_disagreement is True


def test_compare_eval_results_reports_over_adaptation_between_runs() -> None:
    before = EvalResult(
        dataset_id="falcon_h2",
        protocol=ProtocolType.HELD_OUT_SESSION,
        method_scores=(
            MethodScore("adaptive", conventional_score=0.4, intent_fidelity_score=0.2),
            MethodScore("stable", conventional_score=0.5, intent_fidelity_score=0.3),
        ),
        primary_metric="intent_fidelity_log_loss",
    )
    after = EvalResult(
        dataset_id="falcon_h2",
        protocol=ProtocolType.HELD_OUT_SESSION,
        method_scores=(
            MethodScore("adaptive", conventional_score=0.2, intent_fidelity_score=0.5),
            MethodScore("stable", conventional_score=0.6, intent_fidelity_score=0.2),
        ),
        primary_metric="intent_fidelity_log_loss",
    )

    report = compare_eval_results(before, after)

    assert [event.method_id for event in report.over_adaptation_events] == ["adaptive"]
