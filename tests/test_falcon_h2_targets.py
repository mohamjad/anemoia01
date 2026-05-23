from intentfidelity.ingest import IngestSplit
from intentfidelity.ingest.falcon_trials import FalconH2Trial
from intentfidelity.labels.falcon_h2 import (
    handwriting_cues_from_trial,
    weak_targets_from_trials,
)


def test_handwriting_cues_from_trial_allocates_character_windows() -> None:
    trial = FalconH2Trial(
        sample_id="falcon_h2:held_out_calib:2023-04-17:trial-1",
        session_date="2023-04-17",
        split=IngestSplit.HELD_OUT_CALIB,
        cue="a>b",
        start_time=10.0,
        stop_time=13.0,
    )

    cues = handwriting_cues_from_trial(trial)

    assert [cue.prompted_label for cue in cues] == ["a", " ", "b"]
    assert cues[1].window_start == 11.0
    assert cues[1].window_end == 12.0


def test_weak_targets_from_trials_uses_shared_support() -> None:
    trials = (
        FalconH2Trial(
            "falcon_h2:minival:2023-04-17:trial-1",
            "2023-04-17",
            IngestSplit.MINIVAL,
            "ab",
            0,
            2,
        ),
        FalconH2Trial(
            "falcon_h2:minival:2023-04-17:trial-2",
            "2023-04-17",
            IngestSplit.MINIVAL,
            "c",
            2,
            3,
        ),
    )

    targets = weak_targets_from_trials(trials)

    assert len(targets) == 3
    assert targets[0].support == ("a", "b", "c")
