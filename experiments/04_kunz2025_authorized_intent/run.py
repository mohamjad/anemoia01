from __future__ import annotations

import json

from intentfidelity.labels import AuthorizationEvent, AuthorizationState, Prediction
from intentfidelity.protocols import authorization_eval_result


def build_result():
    events = (
        AuthorizationEvent("kunz2025:sample-0", AuthorizationState.AUTHORIZED),
        AuthorizationEvent("kunz2025:sample-1", AuthorizationState.UNCERTAIN),
    )
    predictions = {
        "intent_proxy_decoder": (
            Prediction(
                "kunz2025:sample-0",
                {"authorized": 0.9, "not_authorized": 0.1},
                "intent_proxy_decoder",
            ),
            Prediction(
                "kunz2025:sample-1",
                {"authorized": 0.5, "not_authorized": 0.5},
                "intent_proxy_decoder",
            ),
        )
    }
    result = authorization_eval_result(events, predictions, dataset_id="kunz2025")
    result.metadata["evidence_stage"] = "synthetic_protocol_scaffold"
    return result


def main() -> int:
    print(json.dumps(build_result().to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
