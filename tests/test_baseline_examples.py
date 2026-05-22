import pytest

from intentfidelity.baselines.examples import (
    LabeledExample,
    feature_dimension,
    labels_from_examples,
    sessions_from_examples,
)


def test_labeled_example_normalizes_features() -> None:
    example = LabeledExample("s1", "a", [1, 2], "session-1")

    assert example.features == (1.0, 2.0)


def test_feature_dimension_requires_consistent_width() -> None:
    examples = [
        LabeledExample("s1", "a", [1, 2], "session-1"),
        LabeledExample("s2", "b", [1], "session-1"),
    ]

    with pytest.raises(ValueError, match="same feature dimension"):
        feature_dimension(examples)


def test_label_and_session_helpers_return_sorted_values() -> None:
    examples = [
        LabeledExample("s1", "b", [1], "session-2"),
        LabeledExample("s2", "a", [1], "session-1"),
    ]

    assert labels_from_examples(examples) == ("a", "b")
    assert sessions_from_examples(examples) == ("session-1", "session-2")

