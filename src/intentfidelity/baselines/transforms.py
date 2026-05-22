from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Sequence

from intentfidelity.baselines.examples import LabeledExample, feature_dimension


@dataclass(frozen=True)
class FeatureTransform:
    method_id: str
    offsets: dict[str, tuple[float, ...]]
    scales: dict[str, tuple[float, ...]]

    def transform(self, examples: Sequence[LabeledExample]) -> tuple[LabeledExample, ...]:
        return tuple(
            LabeledExample(
                sample_id=example.sample_id,
                label=example.label,
                features=_apply_affine(
                    example.features,
                    self.offsets.get(example.session_id),
                    self.scales.get(example.session_id),
                ),
                session_id=example.session_id,
                metadata={**example.metadata, "transform": self.method_id},
            )
            for example in examples
        )


def identity_transform(examples: Sequence[LabeledExample]) -> FeatureTransform:
    dimension = feature_dimension(examples)
    sessions = sorted({example.session_id for example in examples})
    return FeatureTransform(
        method_id="identity",
        offsets={session: (0.0,) * dimension for session in sessions},
        scales={session: (1.0,) * dimension for session in sessions},
    )


def _apply_affine(
    features: tuple[float, ...],
    offset: tuple[float, ...] | None,
    scale: tuple[float, ...] | None,
) -> tuple[float, ...]:
    offset = offset or (0.0,) * len(features)
    scale = scale or (1.0,) * len(features)
    return tuple((value - center) * factor for value, center, factor in zip(features, offset, scale))


def _examples_by_session(
    examples: Sequence[LabeledExample],
) -> dict[str, list[LabeledExample]]:
    grouped: dict[str, list[LabeledExample]] = defaultdict(list)
    for example in examples:
        grouped[example.session_id].append(example)
    return grouped

