import h5py

from intentfidelity.ingest import IngestSplit
from intentfidelity.ingest.falcon_trials import load_falcon_h2_trials


def test_load_falcon_h2_trials_reads_trial_table(tmp_path) -> None:
    path = tmp_path / "sub-T5-held-out-calib_ses-20230417.nwb"
    with h5py.File(path, "w") as handle:
        handle.create_dataset("identifier", data=b"T5_2023.04.17_held_out_calib")
        trials = handle.create_group("intervals/trials")
        trials.create_dataset("cue", data=[b"abc", b"d>e"])
        trials.create_dataset("start_time", data=[0.0, 2.0])
        trials.create_dataset("stop_time", data=[1.0, 4.0])
        trials.create_dataset("id", data=[11, 12])
        trials.create_dataset("block_num", data=[5, 6])

    loaded = load_falcon_h2_trials(path, IngestSplit.HELD_OUT_CALIB)

    assert len(loaded) == 2
    assert loaded[0].sample_id == "falcon_h2:2023-04-17:trial-11"
    assert loaded[1].cue == "d>e"
    assert loaded[1].block_num == 6

