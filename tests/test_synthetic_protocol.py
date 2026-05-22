from intentfidelity.protocols.synthetic import synthetic_baseline_eval


def test_synthetic_baseline_eval_produces_eval_result() -> None:
    result = synthetic_baseline_eval()

    assert result.dataset_id == "synthetic_shift"
    assert len(result.method_scores) == 2
    assert result.ranking_disagreement is not None

