from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from intentfidelity.labels.text import TextPrediction, TextTarget


def write_text_targets_jsonl(targets: Iterable[TextTarget], path: str | Path) -> None:
    _write_jsonl(
        (
            {
                "sample_id": target.sample_id,
                "text": target.text,
                "source_type": target.source_type,
                "metadata": target.metadata,
            }
            for target in targets
        ),
        path,
    )


def read_text_targets_jsonl(path: str | Path) -> tuple[TextTarget, ...]:
    return tuple(
        TextTarget(
            sample_id=row["sample_id"],
            text=row["text"],
            source_type=row["source_type"],
            metadata=row.get("metadata", {}),
        )
        for row in _read_jsonl(path)
    )


def write_text_predictions_jsonl(
    predictions: Iterable[TextPrediction], path: str | Path
) -> None:
    _write_jsonl(
        (
            {
                "sample_id": prediction.sample_id,
                "text": prediction.text,
                "method_id": prediction.method_id,
                "metadata": prediction.metadata,
            }
            for prediction in predictions
        ),
        path,
    )


def read_text_predictions_jsonl(path: str | Path) -> tuple[TextPrediction, ...]:
    return tuple(
        TextPrediction(
            sample_id=row["sample_id"],
            text=row["text"],
            method_id=row["method_id"],
            metadata=row.get("metadata", {}),
        )
        for row in _read_jsonl(path)
    )


def _write_jsonl(rows, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _read_jsonl(path: str | Path) -> tuple[dict, ...]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return tuple(json.loads(line) for line in handle if line.strip())

