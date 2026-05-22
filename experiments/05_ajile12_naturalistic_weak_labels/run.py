from __future__ import annotations

import json

from intentfidelity.labels import NaturalisticEvent, Prediction
from intentfidelity.protocols import naturalistic_eval_result


def build_result():
    events = (
        NaturalisticEvent(
            "ajile12:session-1:event-0",
            "reach",
            ("reach", "rest", "grasp"),
            0.75,
            "session-1",
            1.0,
            2.0,
        ),
        NaturalisticEvent(
            "ajile12:session-2:event-0",
            "rest",
            ("reach", "rest", "grasp"),
            0.6,
            "session-2",
            3.0,
            4.0,
        ),
    )
    predictions = {
        "behavior_proxy_decoder": (
            Prediction(
                "ajile12:session-1:event-0",
                {"reach": 0.7, "rest": 0.2, "grasp": 0.1},
                "behavior_proxy_decoder",
            ),
            Prediction(
                "ajile12:session-2:event-0",
                {"reach": 0.2, "rest": 0.6, "grasp": 0.2},
                "behavior_proxy_decoder",
            ),
        )
    }
    result = naturalistic_eval_result(events, predictions, dataset_id="ajile12")
    result.metadata["evidence_stage"] = "synthetic_protocol_scaffold"
    return result


def main() -> int:
    print(json.dumps(build_result().to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
