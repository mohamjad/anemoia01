from intentfidelity.baselines.examples import LabeledExample
from intentfidelity.baselines.transforms import identity_transform


def test_identity_transform_preserves_features() -> None:
    examples = (LabeledExample("s1", "a", [1, 2], "session-1"),)

    transformed = identity_transform(examples).transform(examples)

    assert transformed[0].features == (1.0, 2.0)
    assert transformed[0].metadata["transform"] == "identity"

