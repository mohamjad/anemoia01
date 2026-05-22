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


def session_centering_transform(examples: Sequence[LabeledExample]) -> FeatureTransform:
    dimension = feature_dimension(examples)
    grouped = _examples_by_session(examples)
    return FeatureTransform(
        method_id="session_centering",
        offsets={
            session: _mean_vector([example.features for example in session_examples], dimension)
            for session, session_examples in grouped.items()
        },
        scales={session: (1.0,) * dimension for session in grouped},
    )


def whitening_transform(examples: Sequence[LabeledExample], epsilon: float = 1e-9) -> FeatureTransform:
    dimension = feature_dimension(examples)
    grouped = _examples_by_session(examples)
    offsets: dict[str, tuple[float, ...]] = {}
    scales: dict[str, tuple[float, ...]] = {}
    for session, session_examples in grouped.items():
        vectors = [example.features for example in session_examples]
        mean = _mean_vector(vectors, dimension)
        offsets[session] = mean
        scales[session] = tuple(
            1.0 / max(_std_at_index(vectors, mean, index), epsilon)
            for index in range(dimension)
        )
    return FeatureTransform("whitening", offsets=offsets, scales=scales)


def whitening_coloring_transform(
    source_examples: Sequence[LabeledExample],
    reference_examples: Sequence[LabeledExample],
    epsilon: float = 1e-9,
) -> FeatureTransform:
    dimension = feature_dimension(source_examples)
    if feature_dimension(reference_examples) != dimension:
        raise ValueError("source and reference examples must share feature dimension")

    reference_mean = _mean_vector([example.features for example in reference_examples], dimension)
    reference_std = tuple(
        _std_at_index([example.features for example in reference_examples], reference_mean, index)
        for index in range(dimension)
    )
    grouped = _examples_by_session(source_examples)
    offsets: dict[str, tuple[float, ...]] = {}
    scales: dict[str, tuple[float, ...]] = {}
    for session, session_examples in grouped.items():
        vectors = [example.features for example in session_examples]
        session_mean = _mean_vector(vectors, dimension)
        session_scales = tuple(
            reference_std[index] / max(_std_at_index(vectors, session_mean, index), epsilon)
            for index in range(dimension)
        )
        offsets[session] = tuple(
            session_mean[index] - reference_mean[index] / max(session_scales[index], epsilon)
            for index in range(dimension)
        )
        scales[session] = session_scales
    return FeatureTransform("whitening_coloring", offsets=offsets, scales=scales)


def _mean_vector(vectors: Sequence[tuple[float, ...]], dimension: int) -> tuple[float, ...]:
    return tuple(sum(vector[index] for vector in vectors) / len(vectors) for index in range(dimension))


def _std_at_index(
    vectors: Sequence[tuple[float, ...]],
    mean: tuple[float, ...],
    index: int,
) -> float:
    variance = sum((vector[index] - mean[index]) ** 2 for vector in vectors) / len(vectors)
    return variance**0.5


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
