import json
from pathlib import Path
import sys
from types import SimpleNamespace

import h5py
import numpy as np
import pytest

from intentfidelity.labels import read_predictions_jsonl, read_weak_targets_jsonl
from intentfidelity.protocols import load_eval_result
from intentfidelity.protocols.artifacts import EvidenceLevel, load_artifact_bundle
from intentfidelity.protocols.falcon_h2_artifacts import (
    validate_falcon_h2_artifact_bundle,
    validate_falcon_h2_feature_baseline_bundle,
    write_falcon_h2_feature_baseline_bundle,
    write_falcon_h2_artifact_bundle,
)


def test_falcon_h2_bundle_writes_complete_fixture_artifacts(tmp_path: Path) -> None:
    source = _write_h2_file(tmp_path / "sub-T5-held-out-calib_ses-20230417.nwb")
    output_dir = tmp_path / "bundle"

    bundle = write_falcon_h2_artifact_bundle(
        source,
        output_dir,
        evidence_level=EvidenceLevel.FIXTURE_EVIDENCE,
        command="intentfidelity eval falcon-h2-bundle fixture.nwb bundle",
    )

    expected_files = {
        "inventory.json",
        "targets.jsonl",
        "predictions.jsonl",
        "result.json",
        "diagnostics.json",
        "diagnostics.md",
        "eval_card.md",
        "comparison.md",
        "bundle_manifest.json",
    }
    assert {path.name for path in output_dir.iterdir()} == expected_files
    assert {artifact.kind for artifact in bundle.generated_files} == {
        "inventory_json",
        "targets_jsonl",
        "predictions_jsonl",
        "result_json",
        "diagnostics_json",
        "diagnostics_markdown",
        "eval_card_markdown",
        "comparison_markdown",
        "bundle_manifest_json",
    }

    targets = read_weak_targets_jsonl(output_dir / "targets.jsonl")
    predictions = read_predictions_jsonl(output_dir / "predictions.jsonl")
    result = load_eval_result(output_dir / "result.json")
    manifest = load_artifact_bundle(output_dir / "bundle_manifest.json")
    diagnostics = json.loads((output_dir / "diagnostics.json").read_text())

    assert len(targets) == 2
    assert len(predictions) == 4
    assert result.dataset_id == "falcon_h2"
    assert result.metadata["evidence_level"] == "fixture_evidence"
    assert result.metadata["intentfidelity_version"] == "0.1.0"
    assert result.metadata["command"] == (
        "intentfidelity eval falcon-h2-bundle fixture.nwb bundle"
    )
    assert result.metadata["source_files"][0]["sha256"]
    assert diagnostics["sample_count"] == 2
    assert diagnostics["method_count"] == 2
    assert manifest.metadata["target_count"] == 2
    assert manifest.metadata["source_files"][0]["size_bytes"] == source.stat().st_size

    eval_card = (output_dir / "eval_card.md").read_text(encoding="utf-8")
    comparison = (output_dir / "comparison.md").read_text(encoding="utf-8")
    assert "fixture_evidence" in eval_card
    assert "Bootstrap Ranking Stability" in (
        output_dir / "diagnostics.md"
    ).read_text(encoding="utf-8")
    assert "not downloaded FALCON H2 dataset evidence" in eval_card
    assert "declared weak target distributions" in comparison


def test_validate_falcon_h2_bundle_accepts_complete_bundle(tmp_path: Path) -> None:
    source = _write_h2_file(tmp_path / "sub-T5-held-out-calib_ses-20230417.nwb")
    output_dir = tmp_path / "bundle"
    write_falcon_h2_artifact_bundle(source, output_dir)

    report = validate_falcon_h2_artifact_bundle(output_dir)

    assert report.is_valid is True
    assert report.issues == ()


def test_validate_falcon_h2_bundle_requires_falcon_artifact_kinds(
    tmp_path: Path,
) -> None:
    source = _write_h2_file(tmp_path / "sub-T5-held-out-calib_ses-20230417.nwb")
    output_dir = tmp_path / "bundle"
    write_falcon_h2_artifact_bundle(source, output_dir)
    (output_dir / "comparison.md").unlink()

    report = validate_falcon_h2_artifact_bundle(output_dir)

    assert report.is_valid is False
    assert report.issues[0].code == "missing_generated_artifact"


def test_validate_falcon_h2_bundle_checks_result_counts(tmp_path: Path) -> None:
    source = _write_h2_file(tmp_path / "sub-T5-held-out-calib_ses-20230417.nwb")
    output_dir = tmp_path / "bundle"
    write_falcon_h2_artifact_bundle(source, output_dir)
    result_path = output_dir / "result.json"
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    payload["metadata"]["target_count"] = 999
    result_path.write_text(json.dumps(payload), encoding="utf-8")

    report = validate_falcon_h2_artifact_bundle(output_dir)

    assert report.is_valid is False
    assert "result_target_count_mismatch" in {
        issue.code for issue in report.issues
    }


def test_validate_falcon_h2_bundle_checks_report_scope(tmp_path: Path) -> None:
    source = _write_h2_file(tmp_path / "sub-T5-held-out-calib_ses-20230417.nwb")
    output_dir = tmp_path / "bundle"
    write_falcon_h2_artifact_bundle(source, output_dir)
    (output_dir / "eval_card.md").write_text("# Eval Card\n", encoding="utf-8")

    report = validate_falcon_h2_artifact_bundle(output_dir)

    assert report.is_valid is False
    assert "eval_card_missing_evidence_scope" in {
        issue.code for issue in report.issues
    }


def test_falcon_h2_feature_baseline_bundle_writes_method_artifacts(
    tmp_path: Path,
) -> None:
    train = _write_h2_file(tmp_path / "sub-T5-held-in-calib_ses-20230416.nwb")
    test = _write_h2_file(tmp_path / "sub-T5-held-out-calib_ses-20230417.nwb")
    output_dir = tmp_path / "feature-bundle"

    bundle = write_falcon_h2_feature_baseline_bundle(train, test, output_dir)

    expected_files = {
        "train_inventory.json",
        "test_inventory.json",
        "targets.jsonl",
        "predictions.jsonl",
        "baseline_runs.json",
        "result.json",
        "diagnostics.json",
        "diagnostics.md",
        "latent_drift.json",
        "latent_drift.md",
        "eval_card.md",
        "comparison.md",
        "bundle_manifest.json",
    }
    result = load_eval_result(output_dir / "result.json")
    report = validate_falcon_h2_feature_baseline_bundle(output_dir)

    assert {path.name for path in output_dir.iterdir()} == expected_files
    assert bundle.metadata["train_example_count"] == 2
    assert bundle.metadata["test_example_count"] == 2
    assert bundle.metadata["prediction_count"] == 6
    assert bundle.metadata["latent_backend"] == "pca_svd"
    assert json.loads((output_dir / "diagnostics.json").read_text())[
        "method_count"
    ] == 3
    latent_drift = json.loads((output_dir / "latent_drift.json").read_text())
    assert latent_drift["config"]["method_id"] == "pca_svd_latent_probe"
    assert latent_drift["evaluated_sample_count"] == 2
    assert "direct intent readout" in (output_dir / "latent_drift.md").read_text(
        encoding="utf-8"
    )
    assert [score.method_id for score in result.method_scores] == [
        "identity_centroid",
        "session_centered_centroid",
        "whitened_centroid",
    ]
    assert result.method_scores[0].conventional_score >= 0.0
    assert report.is_valid is True


def test_falcon_h2_feature_bundle_can_use_optional_cebra_backend(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeCebraModel:
        def __init__(self, **kwargs: object) -> None:
            self.output_dimension = int(kwargs["output_dimension"])

        def fit(self, matrix: np.ndarray):
            return self

        def transform(self, matrix: np.ndarray) -> np.ndarray:
            return matrix[:, : self.output_dimension]

    monkeypatch.setitem(sys.modules, "cebra", SimpleNamespace(CEBRA=FakeCebraModel))
    train = _write_h2_file(tmp_path / "sub-T5-held-in-calib_ses-20230416.nwb")
    test = _write_h2_file(tmp_path / "sub-T5-held-out-calib_ses-20230417.nwb")
    output_dir = tmp_path / "feature-bundle"

    bundle = write_falcon_h2_feature_baseline_bundle(
        train,
        test,
        output_dir,
        latent_backend="cebra",
        latent_components=2,
        cebra_max_iterations=3,
    )

    latent_drift = json.loads((output_dir / "latent_drift.json").read_text())
    report = validate_falcon_h2_feature_baseline_bundle(output_dir)

    assert bundle.metadata["latent_backend"] == "cebra"
    assert latent_drift["config"]["method_id"] == "cebra_self_supervised_latent_probe"
    assert latent_drift["config"]["parameters"]["max_iterations"] == 3
    assert latent_drift["latent_dimension"] == 2
    assert report.is_valid is True


def test_falcon_h2_bundle_accepts_inventory_root(tmp_path: Path) -> None:
    h2_root = tmp_path / "h2"
    _write_h2_file(h2_root / "held_in_calib" / "sub-T5-held-in-calib_ses-20230417.nwb")
    _write_h2_file(
        h2_root / "held_out_calib" / "sub-T5-held-out-calib_ses-20230418.nwb"
    )
    _write_h2_file(h2_root / "minival" / "sub-T5-held-in-minival_ses-20230419.nwb")

    write_falcon_h2_artifact_bundle(tmp_path, tmp_path / "bundle")

    inventory = json.loads((tmp_path / "bundle" / "inventory.json").read_text())
    targets = read_weak_targets_jsonl(tmp_path / "bundle" / "targets.jsonl")

    assert inventory["file_count"] == 3
    assert len(targets) == 6


def test_falcon_h2_bundle_rejects_invalid_file_suffix(tmp_path: Path) -> None:
    source = tmp_path / "not-nwb.txt"
    source.write_text("not hdf5", encoding="utf-8")

    with pytest.raises(ValueError, match="unsupported_file_suffix"):
        write_falcon_h2_artifact_bundle(source, tmp_path / "bundle")


def _write_h2_file(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as handle:
        trials = handle.create_group("intervals/trials")
        trials.create_dataset("cue", data=[b"ab"])
        trials.create_dataset("start_time", data=[0.0])
        trials.create_dataset("stop_time", data=[2.0])
        trials.create_dataset("id", data=[1])
        handle.create_dataset("acquisition/binned_spikes/data", data=[[0, 1], [1, 0]])
        handle.create_dataset("acquisition/binned_spikes/timestamps", data=[0.25, 1.25])
    return path
