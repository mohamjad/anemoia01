import h5py

from intentfidelity.ingest.falcon_neural import summarize_falcon_h2_neural


def test_summarize_falcon_h2_neural_reads_shapes(tmp_path) -> None:
    path = tmp_path / "sample.nwb"
    with h5py.File(path, "w") as handle:
        handle.create_dataset("acquisition/binned_spikes/data", data=[[1, 2], [3, 4]])
        handle.create_dataset("acquisition/binned_spikes/timestamps", data=[0.0, 0.02])
        handle.create_dataset("acquisition/eval_mask/data", data=[True, False])

    summary = summarize_falcon_h2_neural(path)

    assert summary.bin_count == 2
    assert summary.channel_count == 2
    assert summary.eval_mask_true_count == 1

