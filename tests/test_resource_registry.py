import shutil

import pytest

from intentfidelity.resources import (
    ManifestValidationError,
    get_manifest,
    load_manifests,
)


def test_initial_resource_manifests_load_in_priority_order() -> None:
    manifests = load_manifests()

    assert [manifest.dataset_id for manifest in manifests] == [
        "falcon_h2",
        "card2024",
        "willett2023",
        "kunz2025",
        "ajile12",
        "bigp3bci",
    ]


def test_get_manifest_returns_dataset_record() -> None:
    manifest = get_manifest("falcon_h2")

    assert manifest.title == "FALCON H2"
    assert manifest.source_url == "https://dandiarchive.org/dandiset/000950"
    assert manifest.metadata["expected_local_root"] == "data/h2"
    assert manifest.first_pass_role.startswith("first real-data target")


def test_registry_rejects_duplicate_priorities(tmp_path) -> None:
    source = get_manifest("falcon_h2")
    first = tmp_path / "first.yaml"
    second = tmp_path / "second.yaml"
    manifest_text = "\n".join(
        [
            f"dataset_id: {source.dataset_id}",
            f"title: {source.title}",
            f"domain: {source.domain}",
            f"status: {source.status}",
            f"priority: {source.priority}",
            f"access: {source.access}",
            "modalities:",
            "  - intracortical neural recordings",
            "weak_proxy_sources:",
            "  - task prompts",
            "known_limitations:",
            "  - test manifest",
            f"first_pass_role: {source.first_pass_role}",
        ]
    )
    first.write_text(manifest_text, encoding="utf-8")
    shutil.copyfile(first, second)

    with pytest.raises(ManifestValidationError, match="duplicate dataset_id"):
        load_manifests(tmp_path)
