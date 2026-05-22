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
from intentfidelity.labels.text import TextPrediction, TextTarget, normalize_text
from intentfidelity.labels.text_io import (
    read_text_predictions_jsonl,
    read_text_targets_jsonl,
    write_text_predictions_jsonl,
    write_text_targets_jsonl,
)
from intentfidelity.labels.authorization import (
    AuthorizationEvent,
    AuthorizationState,
    weak_target_from_authorization_event,
)
from intentfidelity.labels.authorization_io import (
    read_authorization_events_jsonl,
    write_authorization_events_jsonl,
)
from intentfidelity.labels.naturalistic import (
    NATURALISTIC_SOURCE_TYPE,
    NaturalisticEvent,
    weak_target_from_naturalistic_event,
)
from intentfidelity.labels.naturalistic_io import (
    read_naturalistic_events_jsonl,
    write_naturalistic_events_jsonl,
)
from intentfidelity.labels.p300 import (
    P300_SOURCE_TYPE,
    P300SelectionEvent,
    weak_target_from_p300_event,
)
from intentfidelity.labels.p300_io import (
    read_p300_events_jsonl,
    write_p300_events_jsonl,
)

__all__ = [
    "AuthorizationEvent",
    "AuthorizationState",
    "DistributionValidationError",
    "HANDWRITING_SOURCE_TYPE",
    "NATURALISTIC_SOURCE_TYPE",
    "NaturalisticEvent",
    "P300_SOURCE_TYPE",
    "P300SelectionEvent",
    "Prediction",
    "SPACE_TOKEN",
    "TextPrediction",
    "TextTarget",
    "HandwritingCue",
    "WeakTarget",
    "align_probabilities",
    "cue_character_sequence",
    "cue_support",
    "normalize_probabilities",
    "normalize_h2_cue",
    "normalize_text",
    "prediction_from_dict",
    "read_predictions_jsonl",
    "read_authorization_events_jsonl",
    "read_naturalistic_events_jsonl",
    "read_p300_events_jsonl",
    "read_text_predictions_jsonl",
    "read_text_targets_jsonl",
    "read_weak_targets_jsonl",
    "require_same_support",
    "weak_target_from_dict",
    "weak_target_from_handwriting_cue",
    "weak_target_from_authorization_event",
    "weak_target_from_naturalistic_event",
    "weak_target_from_p300_event",
    "handwriting_cues_from_trial",
    "weak_targets_from_trials",
    "write_predictions_jsonl",
    "write_authorization_events_jsonl",
    "write_naturalistic_events_jsonl",
    "write_p300_events_jsonl",
    "write_text_predictions_jsonl",
    "write_text_targets_jsonl",
    "write_weak_targets_jsonl",
]
