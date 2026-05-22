from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import h5py

from intentfidelity.ingest.nwb_hdf5 import require_dataset


@dataclass(frozen=True)
class FalconH2NeuralSummary:
    source_path: Path
    bin_count: int
    channel_count: int
    timestamp_count: int
    eval_mask_count: int
    eval_mask_true_count: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_path", Path(self.source_path))


def summarize_falcon_h2_neural(path: str | Path) -> FalconH2NeuralSummary:
    source_path = Path(path)
    with h5py.File(source_path, "r") as handle:
        spikes = require_dataset(handle, "acquisition/binned_spikes/data")
        spike_shape = tuple(spikes.shape)
        timestamps = require_dataset(handle, "acquisition/binned_spikes/timestamps")
        timestamp_shape = tuple(timestamps.shape)
        eval_mask = require_dataset(handle, "acquisition/eval_mask/data")[()]

    if len(spike_shape) != 2:
        raise ValueError("binned_spikes/data must be a 2D matrix")
    return FalconH2NeuralSummary(
        source_path=source_path,
        bin_count=int(spike_shape[0]),
        channel_count=int(spike_shape[1]),
        timestamp_count=int(timestamp_shape[0]),
        eval_mask_count=int(eval_mask.shape[0]),
        eval_mask_true_count=int(eval_mask.sum()),
    )
