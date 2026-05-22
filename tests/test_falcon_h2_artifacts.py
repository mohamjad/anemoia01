import json
from pathlib import Path

import h5py
import pytest

from intentfidelity.labels import read_predictions_jsonl, read_weak_targets_jsonl
from intentfidelity.protocols import load_eval_result
from intentfidelity.protocols.artifacts import EvidenceLevel, load_artifact_bundle
from intentfidelity.protocols.falcon_h2_artifacts import (
    validate_falcon_h2_artifact_bundle,
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
        "eval_card_markdown",
        "comparison_markdown",
        "bundle_manifest_json",
    }

    targets = read_weak_targets_jsonl(output_dir / "targets.jsonl")
    predictions = read_predictions_jsonl(output_dir / "predictions.jsonl")
    result = load_eval_result(output_dir / "result.json")
    manifest = load_artifact_bundle(output_dir / "bundle_manifest.json")

    assert len(targets) == 2
    assert len(predictions) == 4
    assert result.dataset_id == "falcon_h2"
    assert result.metadata["evidence_level"] == "fixture_evidence"
    assert result.metadata["intentfidelity_version"] == "0.1.0"
    assert result.metadata["command"] == (
        "intentfidelity eval falcon-h2-bundle fixture.nwb bundle"
    )
    assert result.metadata["source_files"][0]["sha256"]
    assert manifest.metadata["target_count"] == 2
    assert manifest.metadata["source_files"][0]["size_bytes"] == source.stat().st_size

    eval_card = (output_dir / "eval_card.md").read_text(encoding="utf-8")
    comparison = (output_dir / "comparison.md").read_text(encoding="utf-8")
    assert "fixture_evidence" in eval_card
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
