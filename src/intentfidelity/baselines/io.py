from __future__ import annotations

import csv
from pathlib import Path

from intentfidelity.baselines.examples import LabeledExample


def read_labeled_examples_csv(path: str | Path) -> tuple[LabeledExample, ...]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return tuple(_row_to_example(row) for row in reader)


def write_labeled_examples_csv(examples: tuple[LabeledExample, ...], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    feature_count = len(examples[0].features) if examples else 0
    fieldnames = ["sample_id", "label", "session_id"] + [
        f"feature_{index}" for index in range(feature_count)
    ]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for example in examples:
            row = {
                "sample_id": example.sample_id,
                "label": example.label,
                "session_id": example.session_id,
            }
            row.update(
                {f"feature_{index}": value for index, value in enumerate(example.features)}
            )
            writer.writerow(row)


def _row_to_example(row: dict[str, str]) -> LabeledExample:
    feature_keys = sorted(key for key in row if key.startswith("feature_"))
    return LabeledExample(
        sample_id=row["sample_id"],
        label=row["label"],
        session_id=row["session_id"],
        features=tuple(float(row[key]) for key in feature_keys),
    )

