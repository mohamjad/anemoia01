import h5py

from intentfidelity.ingest import IngestSplit
from intentfidelity.ingest.falcon_examples import load_falcon_h2_labeled_examples


def test_load_falcon_h2_labeled_examples_extracts_window_means(tmp_path) -> None:
    path = tmp_path / "sub-T5-held-out-calib_ses-20230417.nwb"
    with h5py.File(path, "w") as handle:
        trials = handle.create_group("intervals/trials")
        trials.create_dataset("cue", data=[b"ab"])
        trials.create_dataset("start_time", data=[0.0])
        trials.create_dataset("stop_time", data=[2.0])
        trials.create_dataset("id", data=[1])
        handle.create_dataset("acquisition/binned_spikes/data", data=[[1, 3], [5, 7]])
        handle.create_dataset("acquisition/binned_spikes/timestamps", data=[0.25, 1.25])

    examples = load_falcon_h2_labeled_examples(path, IngestSplit.HELD_OUT_CALIB)

    assert [example.label for example in examples] == ["a", "b"]
    assert examples[0].features == (1.0, 3.0)
    assert examples[1].features == (5.0, 7.0)


def test_load_falcon_h2_labeled_examples_excludes_window_end(tmp_path) -> None:
    path = tmp_path / "sub-T5-held-out-calib_ses-20230417.nwb"
    with h5py.File(path, "w") as handle:
        trials = handle.create_group("intervals/trials")
        trials.create_dataset("cue", data=[b"ab"])
        trials.create_dataset("start_time", data=[0.0])
        trials.create_dataset("stop_time", data=[2.0])
        trials.create_dataset("id", data=[1])
        handle.create_dataset(
            "acquisition/binned_spikes/data",
            data=[[1, 1], [9, 9], [2, 2]],
        )
        handle.create_dataset(
            "acquisition/binned_spikes/timestamps",
            data=[0.0, 1.0, 1.5],
        )

    examples = load_falcon_h2_labeled_examples(path, IngestSplit.HELD_OUT_CALIB)

    assert examples[0].features == (1.0, 1.0)
    assert examples[1].features == (5.5, 5.5)
