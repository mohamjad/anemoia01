import pytest

from intentfidelity.labels import (
    HANDWRITING_SOURCE_TYPE,
    DistributionValidationError,
    HandwritingCue,
    weak_target_from_handwriting_cue,
)


def test_handwriting_cue_builds_declared_weak_target() -> None:
    cue = HandwritingCue(
        sample_id="trial-001",
        prompted_label="a",
        window_start=1.0,
        window_end=2.0,
        metadata={"session": "s1"},
    )

    target = weak_target_from_handwriting_cue(cue, support=["a", "b", "c"])

    assert target.source_type == HANDWRITING_SOURCE_TYPE
    assert target.probabilities == {"a": 1.0, "b": 0.0, "c": 0.0}
    assert target.metadata["window_start"] == 1.0
    assert target.metadata["session"] == "s1"


def test_handwriting_target_can_reserve_off_target_mass() -> None:
    cue = HandwritingCue("trial-001", "a", 1.0, 2.0)

    target = weak_target_from_handwriting_cue(
        cue,
        support=["a", "b", "c"],
        off_target_mass=0.2,
    )

    assert target.probabilities["a"] == pytest.approx(0.8)
    assert target.probabilities["b"] == pytest.approx(0.1)
    assert target.probabilities["c"] == pytest.approx(0.1)


def test_handwriting_target_requires_prompt_in_support() -> None:
    cue = HandwritingCue("trial-001", "z", 1.0, 2.0)

    with pytest.raises(DistributionValidationError, match="present in support"):
        weak_target_from_handwriting_cue(cue, support=["a", "b"])

