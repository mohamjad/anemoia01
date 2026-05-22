from __future__ import annotations

import json

from intentfidelity.labels import P300SelectionEvent, Prediction
from intentfidelity.protocols import selection_eval_result


def build_result():
    events = (
        P300SelectionEvent(
            "bigp3bci:session-1:event-0",
            "A",
            ("A", "B", "C"),
            0.9,
            "A",
            "session-1",
            1.0,
            2.0,
        ),
        P300SelectionEvent(
            "bigp3bci:session-1:event-1",
            "B",
            ("A", "B", "C"),
            0.85,
            "C",
            "session-1",
            3.0,
            4.0,
        ),
    )
    predictions = {
        "selection_proxy_decoder": (
            Prediction(
                "bigp3bci:session-1:event-0",
                {"A": 0.85, "B": 0.1, "C": 0.05},
                "selection_proxy_decoder",
            ),
            Prediction(
                "bigp3bci:session-1:event-1",
                {"A": 0.1, "B": 0.75, "C": 0.15},
                "selection_proxy_decoder",
            ),
        )
    }
    result = selection_eval_result(events, predictions, dataset_id="bigp3bci")
    result.metadata["evidence_stage"] = "synthetic_protocol_scaffold"
    return result


def main() -> int:
    print(json.dumps(build_result().to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
