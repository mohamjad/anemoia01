from intentfidelity.resources import get_manifest, load_manifests


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
    assert manifest.first_pass_role.startswith("first real-data target")

