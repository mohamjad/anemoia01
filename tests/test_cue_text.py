from intentfidelity.labels.cue_text import cue_character_sequence, cue_support, normalize_h2_cue


def test_normalize_h2_cue_converts_space_and_period_markers() -> None:
    assert normalize_h2_cue("hello>world~") == "hello world."


def test_cue_character_sequence_returns_prompt_characters() -> None:
    assert cue_character_sequence("a>b") == ("a", " ", "b")


def test_cue_support_collects_sorted_unique_characters() -> None:
    assert cue_support(("ba", "a>c")) == (" ", "a", "b", "c")

