from __future__ import annotations

import json
from pathlib import Path

from intentfidelity.protocols.schemas import EvalResult


def save_eval_result(result: EvalResult, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_eval_result(path: str | Path) -> EvalResult:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return EvalResult.from_dict(payload)

