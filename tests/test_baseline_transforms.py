from intentfidelity.baselines.examples import LabeledExample
from intentfidelity.baselines.transforms import (
    identity_transform,
    session_centering_transform,
    whitening_transform,
    whitening_coloring_transform,
)


def test_identity_transform_preserves_features() -> None:
    examples = (LabeledExample("s1", "a", [1, 2], "session-1"),)

    transformed = identity_transform(examples).transform(examples)

    assert transformed[0].features == (1.0, 2.0)
    assert transformed[0].metadata["transform"] == "identity"


def test_session_centering_subtracts_session_mean() -> None:
    examples = (
        LabeledExample("s1", "a", [1, 3], "session-1"),
        LabeledExample("s2", "b", [3, 5], "session-1"),
    )

    transformed = session_centering_transform(examples).transform(examples)

    assert transformed[0].features == (-1.0, -1.0)
    assert transformed[1].features == (1.0, 1.0)


def test_whitening_transform_scales_session_variance() -> None:
    examples = (
        LabeledExample("s1", "a", [1], "session-1"),
        LabeledExample("s2", "b", [3], "session-1"),
    )

    transformed = whitening_transform(examples).transform(examples)

    assert transformed[0].features == (-1.0,)
    assert transformed[1].features == (1.0,)


def test_whitening_coloring_matches_reference_scale() -> None:
    source = (
        LabeledExample("s1", "a", [1], "source"),
        LabeledExample("s2", "b", [3], "source"),
    )
    reference = (
        LabeledExample("r1", "a", [0], "reference"),
        LabeledExample("r2", "b", [4], "reference"),
    )

    transformed = whitening_coloring_transform(source, reference).transform(source)

    assert transformed[0].features == (0.0,)
    assert transformed[1].features == (4.0,)
