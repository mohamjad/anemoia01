"""Weak target and prediction schemas."""

from intentfidelity.labels.schemas import (
    DistributionValidationError,
    Prediction,
    WeakTarget,
    align_probabilities,
    normalize_probabilities,
    prediction_from_dict,
    require_same_support,
    weak_target_from_dict,
)
from intentfidelity.labels.handwriting import (
    HANDWRITING_SOURCE_TYPE,
    HandwritingCue,
    weak_target_from_handwriting_cue,
)
from intentfidelity.labels.cue_text import (
    SPACE_TOKEN,
    cue_character_sequence,
    cue_support,
    normalize_h2_cue,
)
from intentfidelity.labels.falcon_h2 import (
    handwriting_cues_from_trial,
    weak_targets_from_trials,
)
from intentfidelity.labels.io import (
    read_predictions_jsonl,
    read_weak_targets_jsonl,
    write_predictions_jsonl,
    write_weak_targets_jsonl,
)

__all__ = [
    "DistributionValidationError",
    "HANDWRITING_SOURCE_TYPE",
    "Prediction",
    "SPACE_TOKEN",
    "HandwritingCue",
    "WeakTarget",
    "align_probabilities",
    "cue_character_sequence",
    "cue_support",
    "normalize_probabilities",
    "normalize_h2_cue",
    "prediction_from_dict",
    "read_predictions_jsonl",
    "read_weak_targets_jsonl",
    "require_same_support",
    "weak_target_from_dict",
    "weak_target_from_handwriting_cue",
    "handwriting_cues_from_trial",
    "weak_targets_from_trials",
    "write_predictions_jsonl",
    "write_weak_targets_jsonl",
]
