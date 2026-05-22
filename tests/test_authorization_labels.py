from intentfidelity.labels.authorization import (
    AuthorizationEvent,
    AuthorizationState,
    weak_target_from_authorization_event,
)


def test_authorized_event_creates_authorization_target() -> None:
    event = AuthorizationEvent("sample-1", AuthorizationState.AUTHORIZED)

    target = weak_target_from_authorization_event(event)

    assert target.probabilities == {"authorized": 1.0, "not_authorized": 0.0}
    assert target.source_type == "authorization_state_proxy"


def test_uncertain_authorization_event_is_uniform_proxy() -> None:
    event = AuthorizationEvent("sample-1", AuthorizationState.UNCERTAIN)

    target = weak_target_from_authorization_event(event)

    assert target.probabilities == {"authorized": 0.5, "not_authorized": 0.5}

