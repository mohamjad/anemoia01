from pathlib import Path

import pytest

from intentfidelity.resources import ManifestValidationError, ResourceManifest
from intentfidelity.resources.schema import load_manifest


def test_resource_manifest_validates_required_fields() -> None:
    with pytest.raises(ManifestValidationError, match="missing required fields"):
        ResourceManifest.from_mapping({"dataset_id": "falcon_h2"})


def test_resource_manifest_rejects_invalid_dataset_id() -> None:
    payload = {
        "dataset_id": "FALCON-H2",
        "title": "FALCON H2",
        "domain": "motor",
        "status": "planned",
        "priority": 1,
        "access": "public",
        "modalities": ["intracortical"],
        "weak_proxy_sources": ["task prompts"],
        "known_limitations": ["manifest only"],
        "first_pass_role": "first target",
    }

    with pytest.raises(ManifestValidationError, match="dataset_id"):
        ResourceManifest.from_mapping(payload)


def test_load_manifest_from_yaml(tmp_path: Path) -> None:
    path = tmp_path / "resource.yaml"
    path.write_text(
        "\n".join(
            [
                "dataset_id: falcon_h2",
                "title: FALCON H2",
                "domain: motor",
                "status: active",
                "priority: 1",
                "access: public research release",
                "modalities:",
                "  - intracortical arrays",
                "weak_proxy_sources:",
                "  - prompted target",
                "known_limitations:",
                "  - ingestion not implemented",
                "first_pass_role: first real-data target",
            ]
        ),
        encoding="utf-8",
    )

    manifest = load_manifest(path)

    assert manifest.dataset_id == "falcon_h2"
    assert manifest.modalities == ("intracortical arrays",)

