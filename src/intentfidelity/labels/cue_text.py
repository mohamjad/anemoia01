from __future__ import annotations


SPACE_TOKEN = " "


def normalize_h2_cue(cue: str) -> str:
    return cue.replace(">", SPACE_TOKEN).replace("~", ".").strip()


def cue_character_sequence(cue: str) -> tuple[str, ...]:
    normalized = normalize_h2_cue(cue)
    return tuple(character for character in normalized if character)


def cue_support(cues: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    labels = {character for cue in cues for character in cue_character_sequence(cue)}
    return tuple(sorted(labels))

