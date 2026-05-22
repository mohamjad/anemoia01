from intentfidelity.metrics.edit_distance import edit_distance, normalized_edit_distance


def test_edit_distance_counts_insertions_deletions_and_substitutions() -> None:
    assert edit_distance(tuple("kitten"), tuple("sitting")) == 3


def test_normalized_edit_distance_divides_by_reference_length() -> None:
    assert normalized_edit_distance(tuple("abcd"), tuple("abxd")) == 0.25


def test_normalized_edit_distance_handles_empty_reference() -> None:
    assert normalized_edit_distance((), tuple("x")) == 1.0

