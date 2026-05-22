from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import h5py


class NwbParseError(ValueError):
    """Raised when an NWB/HDF5 file lacks required pass-2 structures."""


@dataclass(frozen=True)
class Hdf5DatasetInfo:
    path: str
    shape: tuple[int, ...]
    dtype: str


def list_hdf5_datasets(path: str | Path) -> tuple[Hdf5DatasetInfo, ...]:
    infos: list[Hdf5DatasetInfo] = []
    with h5py.File(path, "r") as handle:
        handle.visititems(
            lambda name, obj: infos.append(
                Hdf5DatasetInfo(path=name, shape=tuple(obj.shape), dtype=str(obj.dtype))
            )
            if isinstance(obj, h5py.Dataset)
            else None
        )
    return tuple(sorted(infos, key=lambda info: info.path))


def require_dataset(handle: h5py.File, dataset_path: str) -> h5py.Dataset:
    if dataset_path not in handle:
        raise NwbParseError(f"missing required NWB dataset: {dataset_path}")
    dataset = handle[dataset_path]
    if not isinstance(dataset, h5py.Dataset):
        raise NwbParseError(f"NWB path is not a dataset: {dataset_path}")
    return dataset


def decode_scalar(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if hasattr(value, "item"):
        return decode_scalar(value.item())
    return value


def decode_array(values: Any) -> tuple[Any, ...]:
    return tuple(decode_scalar(value) for value in values)

