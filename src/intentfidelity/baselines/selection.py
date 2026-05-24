from __future__ import annotations

from intentfidelity.baselines.predictions import proxy_oracle_prediction, uniform_prediction
from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.labels.p300 import P300SelectionEvent, weak_target_from_p300_event


def selection_sanity_predictions(
    events: tuple[P300SelectionEvent, ...],
) -> tuple[Prediction, ...]:
    targets = tuple(weak_target_from_p300_event(event) for event in events)
    return (
        *(
            proxy_oracle_prediction(target, method_id="selection_proxy_oracle")
            for target in targets
        ),
        *(
            uniform_prediction(target, method_id="selection_uniform_prior")
            for target in targets
        ),
        *(
            observed_selection_feedback_prediction(event, target)
            for event, target in zip(events, targets)
        ),
    )


def observed_selection_feedback_prediction(
    event: P300SelectionEvent,
    target: WeakTarget | None = None,
) -> Prediction:
    target = target or weak_target_from_p300_event(event)
    if event.selected_symbol is None:
        prediction = uniform_prediction(
            target,
            method_id="observed_selection_feedback",
        )
        return Prediction(
            prediction.sample_id,
            prediction.probabilities,
            prediction.method_id,
            {
                **prediction.metadata,
                "baseline_type": "missing_selected_symbol_falls_back_to_uniform",
                "proxy_boundary": "does_not_use_neural_features_or_true_intent",
            },
        )
    return Prediction(
        sample_id=event.sample_id,
        probabilities={
            symbol: (1.0 if symbol == event.selected_symbol else 0.0)
            for symbol in event.candidate_symbols
        },
        method_id="observed_selection_feedback",
        metadata={
            "baseline_type": "uses_optional_selected_symbol_feedback",
            "proxy_boundary": "does_not_use_neural_features_or_true_intent",
        },
    )
