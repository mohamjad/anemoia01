from __future__ import annotations

from intentfidelity.baselines.examples import LabeledExample


def synthetic_shift_examples() -> tuple[tuple[LabeledExample, ...], tuple[LabeledExample, ...]]:
    train = (
        LabeledExample("train-a-1", "a", (0.0, 0.0), "session-1"),
        LabeledExample("train-a-2", "a", (0.5, 0.0), "session-1"),
        LabeledExample("train-b-1", "b", (5.0, 5.0), "session-1"),
        LabeledExample("train-b-2", "b", (5.5, 5.0), "session-1"),
    )
    test = (
        LabeledExample("test-a-1", "a", (1.0, 0.0), "session-2"),
        LabeledExample("test-b-1", "b", (6.0, 5.0), "session-2"),
    )
    return train, test

