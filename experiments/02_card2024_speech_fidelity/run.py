from __future__ import annotations

import json

from intentfidelity.labels import TextPrediction, TextTarget
from intentfidelity.protocols import communication_eval_result


def build_result():
    targets = (
        TextTarget("card2024:sample-0", "turn on the light", "synthetic_transcript"),
        TextTarget("card2024:sample-1", "open the door", "synthetic_transcript"),
    )
    predictions = (
        TextPrediction("card2024:sample-0", "turn on the light", "proxy_faithful"),
        TextPrediction("card2024:sample-1", "open the door", "proxy_faithful"),
        TextPrediction("card2024:sample-0", "turn on light", "compressed_decoder"),
        TextPrediction("card2024:sample-1", "open door", "compressed_decoder"),
    )
    result = communication_eval_result(
        targets,
        predictions,
        dataset_id="card2024",
    )
    result.metadata["evidence_stage"] = "synthetic_protocol_scaffold"
    return result


def main() -> int:
    print(json.dumps(build_result().to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
