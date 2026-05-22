from intentfidelity.metrics import MethodScore
from intentfidelity.protocols import held_out_session_result, load_eval_result, save_eval_result


def test_eval_result_file_round_trip(tmp_path) -> None:
    result = held_out_session_result(
        "falcon_h2",
        (MethodScore("baseline", 0.1, 0.2),),
    )
    path = tmp_path / "nested" / "result.json"

    save_eval_result(result, path)
    restored = load_eval_result(path)

    assert restored.dataset_id == "falcon_h2"
    assert restored.method_scores == result.method_scores

