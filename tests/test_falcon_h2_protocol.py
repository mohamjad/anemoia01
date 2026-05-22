import h5py

from intentfidelity.protocols.falcon_h2 import (
    falcon_h2_baseline_eval,
    falcon_h2_targets_from_file,
)


def test_falcon_h2_targets_from_file_extracts_character_targets(tmp_path) -> None:
    path = _write_h2_file(tmp_path)

    targets = falcon_h2_targets_from_file(path)

    assert len(targets) == 2
    assert targets[0].metadata["session_date"] == "2023-04-17"


def test_falcon_h2_baseline_eval_returns_ranked_result(tmp_path) -> None:
    path = _write_h2_file(tmp_path)

    result = falcon_h2_baseline_eval(path)

    assert result.dataset_id == "falcon_h2"
    assert [score.method_id for score in result.method_scores] == [
        "proxy_oracle",
        "uniform_prior",
    ]
    assert result.ranking_disagreement is not None


def _write_h2_file(tmp_path):
    path = tmp_path / "sub-T5-held-out-calib_ses-20230417.nwb"
    with h5py.File(path, "w") as handle:
        trials = handle.create_group("intervals/trials")
        trials.create_dataset("cue", data=[b"ab"])
        trials.create_dataset("start_time", data=[0.0])
        trials.create_dataset("stop_time", data=[2.0])
        trials.create_dataset("id", data=[1])
        handle.create_dataset("acquisition/binned_spikes/data", data=[[0, 1]])
        handle.create_dataset("acquisition/binned_spikes/timestamps", data=[0.0])
        handle.create_dataset("acquisition/eval_mask/data", data=[True])
    return path

