from pathlib import Path

import pytest

from intentfidelity.protocols.artifacts import (
    ArtifactBundle,
    EvidenceLevel,
    GeneratedArtifact,
    load_artifact_bundle,
    save_artifact_bundle,
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
