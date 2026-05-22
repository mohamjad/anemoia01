from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from intentfidelity.baselines.examples import LabeledExample
from intentfidelity.baselines.nearest_centroid import fit_nearest_centroid
from intentfidelity.baselines.transforms import FeatureTransform, identity_transform
from intentfidelity.labels import Prediction


TransformFactory = Callable[[Sequence[LabeledExample]], FeatureTransform]


@dataclass(frozen=True)
class BaselineRun:
    method_id: str
    train_count: int
    test_count: int
    predictions: tuple[Prediction, ...]


def run_centroid_baseline(
    train_examples: Sequence[LabeledExample],
    test_examples: Sequence[LabeledExample],
    *,
    method_id: str = "identity_centroid",
    transform_factory: TransformFactory = identity_transform,
) -> BaselineRun:
    transform = transform_factory(tuple(train_examples) + tuple(test_examples))
    transformed_train = transform.transform(train_examples)
    transformed_test = transform.transform(test_examples)
    model = fit_nearest_centroid(transformed_train, method_id=method_id)
    return BaselineRun(
        method_id=method_id,
        train_count=len(transformed_train),
        test_count=len(transformed_test),
        predictions=model.predict(transformed_test),
    )

