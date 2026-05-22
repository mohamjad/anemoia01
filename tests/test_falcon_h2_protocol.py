import h5py

from intentfidelity.protocols.falcon_h2 import (
    falcon_h2_baseline_eval,
    falcon_h2_baseline_predictions,
    falcon_h2_feature_baseline_eval,
    falcon_h2_method_comparison_result_from_targets,
    falcon_h2_prediction_eval,
    falcon_h2_prediction_result_from_targets,
    falcon_h2_split_from_path,
    falcon_h2_targets_from_file,
)
from intentfidelity.labels import Prediction
from intentfidelity.ingest import IngestSplit


def test_falcon_h2_targets_from_file_extracts_character_targets(tmp_path) -> None:
    path = _write_h2_file(tmp_path)

    targets = falcon_h2_targets_from_file(path)

    assert len(targets) == 2
    assert targets[0].metadata["session_date"] == "2023-04-17"


def test_falcon_h2_split_from_path_uses_falcon_split_names() -> None:
    assert (
        falcon_h2_split_from_path("data/h2/sub-T5-held-out-calib/example.nwb")
        == IngestSplit.HELD_OUT_CALIB
    )
    assert (
        falcon_h2_split_from_path("data/h2/sub-T5-held-in-minival/example.nwb")
        == IngestSplit.MINIVAL
    )


def test_falcon_h2_baseline_eval_returns_ranked_result(tmp_path) -> None:
    path = _write_h2_file(tmp_path)

    result = falcon_h2_baseline_eval(path)

    assert result.dataset_id == "falcon_h2"
    assert [score.method_id for score in result.method_scores] == [
        "proxy_oracle",
        "uniform_prior",
    ]
    assert result.ranking_disagreement is not None


def test_falcon_h2_prediction_eval_scores_external_predictions(tmp_path) -> None:
    path = _write_h2_file(tmp_path)
    targets = falcon_h2_targets_from_file(path)
    predictions = tuple(
        Prediction(target.sample_id, target.probabilities, "decoder") for target in targets
    )

    result = falcon_h2_prediction_eval(path, {"decoder": predictions})

    assert result.method_scores[0].method_id == "decoder"
    assert result.method_scores[0].intent_fidelity_score == 0.0


def test_falcon_h2_baseline_predictions_cover_each_target(tmp_path) -> None:
    targets = falcon_h2_targets_from_file(_write_h2_file(tmp_path))

    predictions = falcon_h2_baseline_predictions(targets)

    assert len(predictions) == len(targets) * 2
    assert {prediction.method_id for prediction in predictions} == {
        "proxy_oracle",
        "uniform_prior",
    }


def test_falcon_h2_prediction_result_scores_existing_targets(tmp_path) -> None:
    targets = falcon_h2_targets_from_file(_write_h2_file(tmp_path))
    predictions = tuple(
        Prediction(target.sample_id, target.probabilities, "decoder") for target in targets
    )

    result = falcon_h2_prediction_result_from_targets(
        targets,
        {"decoder": predictions},
        metadata={"evidence_level": "fixture_evidence"},
    )

    assert result.metadata["evidence_level"] == "fixture_evidence"
    assert result.method_scores[0].intent_fidelity_score == 0.0


def test_falcon_h2_method_comparison_uses_top1_error_and_log_loss(tmp_path) -> None:
    targets = falcon_h2_targets_from_file(_write_h2_file(tmp_path))
    good = tuple(
        Prediction(target.sample_id, target.probabilities, "good") for target in targets
    )
    bad = tuple(
        Prediction(
            target.sample_id,
            {
                label: 1.0 if label != _top_target_label(target) else 0.0
                for label in target.support
            },
            "bad",
        )
        for target in targets
    )

    result = falcon_h2_method_comparison_result_from_targets(
        targets,
        {"good": good, "bad": bad},
    )

    scores = {score.method_id: score for score in result.method_scores}
    assert scores["good"].conventional_score == 0.0
    assert scores["good"].intent_fidelity_score == 0.0
    assert scores["bad"].conventional_score == 1.0
    assert scores["bad"].intent_fidelity_score > 0.0


def test_falcon_h2_feature_baseline_eval_scores_centroid_predictions(tmp_path) -> None:
    train_path = _write_h2_file(tmp_path, name="sub-T5-held-in-calib_ses-20230417.nwb")
    test_path = _write_h2_file(tmp_path, name="sub-T5-held-out-calib_ses-20230418.nwb")

    result = falcon_h2_feature_baseline_eval(train_path, test_path)

    assert [score.method_id for score in result.method_scores] == [
        "identity_centroid",
        "session_centered_centroid",
        "whitened_centroid",
    ]


def _write_h2_file(tmp_path, name="sub-T5-held-out-calib_ses-20230417.nwb"):
    path = tmp_path / name
    with h5py.File(path, "w") as handle:
        trials = handle.create_group("intervals/trials")
        trials.create_dataset("cue", data=[b"ab"])
        trials.create_dataset("start_time", data=[0.0])
        trials.create_dataset("stop_time", data=[2.0])
        trials.create_dataset("id", data=[1])
        handle.create_dataset("acquisition/binned_spikes/data", data=[[0, 1], [1, 0]])
        handle.create_dataset("acquisition/binned_spikes/timestamps", data=[0.25, 1.25])
        handle.create_dataset("acquisition/eval_mask/data", data=[True])
    return path


def _top_target_label(target):
    return max(target.probabilities, key=target.probabilities.get)
