from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from intentfidelity.baselines.examples import LabeledExample, feature_dimension, labels_from_examples
from intentfidelity.labels import Prediction


@dataclass(frozen=True)
class NearestCentroidModel:
    method_id: str
    centroids: dict[str, tuple[float, ...]]

    def predict(self, examples: Sequence[LabeledExample]) -> tuple[Prediction, ...]:
        return tuple(
            Prediction(
                sample_id=example.sample_id,
                probabilities=_inverse_distance_probabilities(example.features, self.centroids),
                method_id=self.method_id,
                metadata={"baseline_type": "nearest_centroid"},
            )
            for example in examples
        )


def fit_nearest_centroid(
    examples: Sequence[LabeledExample],
    method_id: str = "nearest_centroid",
) -> NearestCentroidModel:
    dimension = feature_dimension(examples)
    centroids: dict[str, tuple[float, ...]] = {}
    for label in labels_from_examples(examples):
        label_vectors = [example.features for example in examples if example.label == label]
        centroids[label] = tuple(
            sum(vector[index] for vector in label_vectors) / len(label_vectors)
            for index in range(dimension)
        )
    return NearestCentroidModel(method_id=method_id, centroids=centroids)


def _inverse_distance_probabilities(
    features: tuple[float, ...],
    centroids: dict[str, tuple[float, ...]],
) -> dict[str, float]:
    weights = {
        label: 1.0 / (_euclidean_distance(features, centroid) + 1e-9)
        for label, centroid in centroids.items()
    }
    total = sum(weights.values())
    return {label: weight / total for label, weight in weights.items()}


def _euclidean_distance(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return sum((a - b) ** 2 for a, b in zip(left, right)) ** 0.5

