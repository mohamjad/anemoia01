from __future__ import annotations

from bisect import bisect_left
from pathlib import Path

import h5py

from intentfidelity.baselines.examples import LabeledExample
from intentfidelity.ingest.falcon_trials import load_falcon_h2_trials
from intentfidelity.ingest.nwb_hdf5 import require_dataset
from intentfidelity.ingest.schemas import IngestSplit
from intentfidelity.labels.falcon_h2 import handwriting_cues_from_trial


def load_falcon_h2_labeled_examples(
    path: str | Path,
    split: IngestSplit,
) -> tuple[LabeledExample, ...]:
    source_path = Path(path)
    trials = load_falcon_h2_trials(source_path, split)
    with h5py.File(source_path, "r") as handle:
        spikes = require_dataset(handle, "acquisition/binned_spikes/data")[()]
        timestamps = tuple(
            float(value)
            for value in require_dataset(
                handle,
                "acquisition/binned_spikes/timestamps",
            )[()]
        )

    examples: list[LabeledExample] = []
    for trial in trials:
        for cue in handwriting_cues_from_trial(trial):
            start_index = bisect_left(timestamps, cue.window_start)
            stop_index = bisect_left(timestamps, cue.window_end)
            if start_index >= stop_index:
                continue
            examples.append(
                LabeledExample(
                    sample_id=cue.sample_id,
                    label=cue.prompted_label,
                    features=_mean_rows(spikes, start_index, stop_index),
                    session_id=trial.session_date,
                    metadata={
                        "source_path": str(source_path),
                        "trial_sample_id": trial.sample_id,
                        "window_start": cue.window_start,
                        "window_end": cue.window_end,
                    },
                )
            )
    return tuple(examples)


def _mean_rows(matrix, start_index: int, stop_index: int) -> tuple[float, ...]:
    return tuple(float(value) for value in matrix[start_index:stop_index].mean(axis=0))
