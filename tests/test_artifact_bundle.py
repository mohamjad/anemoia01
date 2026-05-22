from pathlib import Path

import pytest

from intentfidelity.protocols.artifacts import (
    ArtifactBundle,
    EvidenceLevel,
    GeneratedArtifact,
    load_artifact_bundle,
    save_artifact_bundle,
    validate_artifact_bundle,
)
from intentfidelity.protocols.schemas import ProtocolType


def test_artifact_bundle_roundtrips_json(tmp_path: Path) -> None:
    bundle = ArtifactBundle(
        dataset_id="falcon_h2",
        protocol=ProtocolType.HELD_OUT_SESSION,
        evidence_level=EvidenceLevel.FIXTURE_EVIDENCE,
        source_path=tmp_path / "input.nwb",
        output_dir=tmp_path / "bundle",
        generated_files=(
            GeneratedArtifact(
                kind="result_json",
                path=tmp_path / "bundle" / "result.json",
                description="EvalResult JSON.",
            ),
        ),
        metadata={"target_type": "handwriting_cue_character"},
    )
    path = tmp_path / "bundle_manifest.json"

    save_artifact_bundle(bundle, path)
    loaded = load_artifact_bundle(path)

    assert loaded == bundle


def test_validate_artifact_bundle_accepts_complete_manifest(tmp_path: Path) -> None:
    output_dir = tmp_path / "bundle"
    output_dir.mkdir()
    result_path = output_dir / "result.json"
    result_path.write_text("{}\n", encoding="utf-8")
    bundle = ArtifactBundle(
        dataset_id="falcon_h2",
        protocol=ProtocolType.HELD_OUT_SESSION,
        evidence_level=EvidenceLevel.FIXTURE_EVIDENCE,
        source_path=tmp_path / "input.nwb",
        output_dir=output_dir,
        generated_files=(
            GeneratedArtifact(
                kind="result_json",
                path=result_path,
                description="EvalResult JSON.",
            ),
        ),
    )
    save_artifact_bundle(bundle, output_dir / "bundle_manifest.json")

    report = validate_artifact_bundle(
        output_dir,
        required_kinds=("result_json",),
    )

    assert report.is_valid is True
    assert report.issues == ()
    assert report.checked_files == (result_path,)


def test_validate_artifact_bundle_reports_missing_manifest(tmp_path: Path) -> None:
    report = validate_artifact_bundle(tmp_path / "bundle")

    assert report.is_valid is False
    assert report.issues[0].code == "missing_bundle_manifest"


def test_validate_artifact_bundle_reports_missing_generated_file(tmp_path: Path) -> None:
    output_dir = tmp_path / "bundle"
    missing_path = output_dir / "result.json"
    bundle = ArtifactBundle(
        dataset_id="falcon_h2",
        protocol=ProtocolType.HELD_OUT_SESSION,
        evidence_level=EvidenceLevel.FIXTURE_EVIDENCE,
        source_path=tmp_path / "input.nwb",
        output_dir=output_dir,
        generated_files=(
            GeneratedArtifact(
                kind="result_json",
                path=missing_path,
                description="EvalResult JSON.",
            ),
        ),
    )
    save_artifact_bundle(bundle, output_dir / "bundle_manifest.json")

    report = validate_artifact_bundle(output_dir)

    assert report.is_valid is False
    assert report.issues[0].code == "missing_generated_artifact"


def test_validate_artifact_bundle_reports_missing_required_kind(tmp_path: Path) -> None:
    output_dir = tmp_path / "bundle"
    output_dir.mkdir()
    result_path = output_dir / "result.json"
    result_path.write_text("{}\n", encoding="utf-8")
    bundle = ArtifactBundle(
        dataset_id="falcon_h2",
        protocol=ProtocolType.HELD_OUT_SESSION,
        evidence_level=EvidenceLevel.FIXTURE_EVIDENCE,
        source_path=tmp_path / "input.nwb",
        output_dir=output_dir,
        generated_files=(
            GeneratedArtifact(
                kind="result_json",
                path=result_path,
                description="EvalResult JSON.",
            ),
        ),
    )
    save_artifact_bundle(bundle, output_dir / "bundle_manifest.json")

    report = validate_artifact_bundle(
        output_dir,
        required_kinds=("result_json", "eval_card_markdown"),
    )

    assert report.is_valid is False
    assert report.issues[0].code == "missing_required_artifact_kind"


def test_artifact_bundle_requires_generated_files(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="at least one generated file"):
        ArtifactBundle(
            dataset_id="falcon_h2",
            protocol=ProtocolType.HELD_OUT_SESSION,
            evidence_level=EvidenceLevel.FIXTURE_EVIDENCE,
            source_path=tmp_path / "input.nwb",
            output_dir=tmp_path / "bundle",
            generated_files=(),
        )
