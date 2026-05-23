from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import h5py

from intentfidelity.ingest.falcon_h2 import FALCON_H2_DATASET_ID
from intentfidelity.ingest.falcon_session import session_date_from_path
from intentfidelity.ingest.nwb_hdf5 import decode_array, decode_scalar, require_dataset
from intentfidelity.ingest.schemas import IngestSplit


@dataclass(frozen=True)
class FalconH2Trial:
    sample_id: str
    session_date: str
    split: IngestSplit
    cue: str
    start_time: float
    stop_time: float
    block_num: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.stop_time <= self.start_time:
            raise ValueError("stop_time must be greater than start_time")
        object.__setattr__(self, "metadata", dict(self.metadata))


def load_falcon_h2_trials(path: str | Path, split: IngestSplit) -> tuple[FalconH2Trial, ...]:
    source_path = Path(path)
    with h5py.File(source_path, "r") as handle:
        cues = decode_array(require_dataset(handle, "intervals/trials/cue")[()])
        starts = require_dataset(handle, "intervals/trials/start_time")[()]
        stops = require_dataset(handle, "intervals/trials/stop_time")[()]
        ids = require_dataset(handle, "intervals/trials/id")[()]
        block_nums = _optional_array(handle, "intervals/trials/block_num")
        identifier = _optional_scalar(handle, "identifier")

    session_date = session_date_from_path(source_path)
    trials: list[FalconH2Trial] = []
    for index, cue in enumerate(cues):
        trial_id = int(ids[index])
        block_num = int(block_nums[index]) if block_nums is not None else None
        trials.append(
            FalconH2Trial(
                sample_id=(
                    f"{FALCON_H2_DATASET_ID}:{split.value}:"
                    f"{session_date}:trial-{trial_id}"
                ),
                session_date=session_date,
                split=split,
                cue=str(cue),
                start_time=float(starts[index]),
                stop_time=float(stops[index]),
                block_num=block_num,
                metadata={
                    "source_path": str(source_path),
                    "source_identifier": identifier,
                    "trial_id": trial_id,
                },
            )
        )
    return tuple(trials)


def _optional_array(handle: h5py.File, path: str):
    if path not in handle:
        return None
    return handle[path][()]


def _optional_scalar(handle: h5py.File, path: str) -> Any:
    if path not in handle:
        return None
    return decode_scalar(handle[path][()])
