from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from intentfidelity.labels.schemas import (
    Prediction,
    WeakTarget,
    prediction_from_dict,
    weak_target_from_dict,
)


def write_weak_targets_jsonl(targets: Iterable[WeakTarget], path: str | Path) -> None:
    _write_jsonl((target.to_dict() for target in targets), path)


def read_weak_targets_jsonl(path: str | Path) -> tuple[WeakTarget, ...]:
    return tuple(weak_target_from_dict(item) for item in _read_jsonl(path))


def write_predictions_jsonl(predictions: Iterable[Prediction], path: str | Path) -> None:
    _write_jsonl((prediction.to_dict() for prediction in predictions), path)


def read_predictions_jsonl(path: str | Path) -> tuple[Prediction, ...]:
    return tuple(prediction_from_dict(item) for item in _read_jsonl(path))


def _write_jsonl(rows, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _read_jsonl(path: str | Path) -> tuple[dict, ...]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return tuple(json.loads(line) for line in handle if line.strip())

