from __future__ import annotations

from intentfidelity.ingest.falcon_trials import FalconH2Trial
from intentfidelity.labels.cue_text import cue_character_sequence, cue_support
from intentfidelity.labels.handwriting import HandwritingCue, weak_target_from_handwriting_cue
from intentfidelity.labels.schemas import WeakTarget


def handwriting_cues_from_trial(trial: FalconH2Trial) -> tuple[HandwritingCue, ...]:
    characters = cue_character_sequence(trial.cue)
    if not characters:
        return ()
    duration = trial.stop_time - trial.start_time
    bin_width = duration / len(characters)
    cues: list[HandwritingCue] = []
    for index, character in enumerate(characters):
        cues.append(
            HandwritingCue(
                sample_id=f"{trial.sample_id}:char-{index:03d}",
                prompted_label=character,
                window_start=trial.start_time + index * bin_width,
                window_end=trial.start_time + (index + 1) * bin_width,
                metadata={
                    "trial_sample_id": trial.sample_id,
                    "session_date": trial.session_date,
                    "split": trial.split.value,
                    "cue": trial.cue,
                    "character_index": index,
                },
            )
        )
    return tuple(cues)


def weak_targets_from_trials(
    trials: tuple[FalconH2Trial, ...],
    *,
    off_target_mass: float = 0.0,
) -> tuple[WeakTarget, ...]:
    support = cue_support(tuple(trial.cue for trial in trials))
    targets: list[WeakTarget] = []
    for trial in trials:
        targets.extend(
            weak_target_from_handwriting_cue(
                cue,
                support=support,
                off_target_mass=off_target_mass,
            )
            for cue in handwriting_cues_from_trial(trial)
        )
    return tuple(targets)

