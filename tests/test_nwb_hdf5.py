import h5py

from intentfidelity.ingest.nwb_hdf5 import (
    decode_array,
    decode_scalar,
    list_hdf5_datasets,
    require_dataset,
)


def test_list_hdf5_datasets_reports_paths_shapes_and_dtypes(tmp_path) -> None:
    path = tmp_path / "sample.nwb"
    with h5py.File(path, "w") as handle:
        handle.create_dataset("acquisition/binned_spikes/data", data=[[1, 2]])

    infos = list_hdf5_datasets(path)

    assert infos[0].path == "acquisition/binned_spikes/data"
    assert infos[0].shape == (1, 2)
    assert "int" in infos[0].dtype


def test_require_dataset_returns_existing_dataset(tmp_path) -> None:
    path = tmp_path / "sample.nwb"
    with h5py.File(path, "w") as handle:
        handle.create_dataset("x", data=[1])

    with h5py.File(path, "r") as handle:
        assert require_dataset(handle, "x").shape == (1,)


def test_decode_helpers_convert_bytes() -> None:
    assert decode_scalar(b"abc") == "abc"
    assert decode_array([b"a", b"b"]) == ("a", "b")

