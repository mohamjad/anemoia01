from __future__ import annotations

import json

from intentfidelity.metrics import MethodScore
from intentfidelity.protocols import EvalResult, ProtocolType, language_prior_report


def build_result() -> EvalResult:
    return EvalResult(
        dataset_id="willett2023",
        protocol=ProtocolType.COMMUNICATION,
        method_scores=(
            MethodScore("lm_light", 0.28, 0.28),
            MethodScore("lm_heavy", 0.18, 0.36),
        ),
        primary_metric="character_error_rate",
        metadata={"evidence_stage": "synthetic_protocol_scaffold"},
    )


def main() -> int:
    attribution = language_prior_report(build_result())
    print(json.dumps(attribution.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
