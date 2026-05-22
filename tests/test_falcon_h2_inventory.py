from intentfidelity.ingest import (
    FALCON_H2_EXPECTED_SPLITS,
    IngestSplit,
    inventory_falcon_h2,
    resolve_falcon_h2_root,
)


def test_resolve_falcon_h2_root_accepts_parent_or_dataset_root(tmp_path) -> None:
    assert resolve_falcon_h2_root(tmp_path) == tmp_path / "h2"
    assert resolve_falcon_h2_root(tmp_path / "h2") == tmp_path / "h2"


def test_inventory_reports_missing_dataset_root(tmp_path) -> None:
    inventory = inventory_falcon_h2(tmp_path)

    assert inventory.is_valid is False
    assert inventory.issues[0].code == "missing_dataset_root"


def test_inventory_finds_nwb_files_by_split(tmp_path) -> None:
    h2_root = tmp_path / "h2"
    split_dirs = {
        "sub-T5-held-in-calib": IngestSplit.HELD_IN_CALIB,
        "sub-T5-held-out-calib": IngestSplit.HELD_OUT_CALIB,
        "sub-T5-held-in-minival": IngestSplit.MINIVAL,
    }
    for directory_name in split_dirs:
        split_dir = h2_root / directory_name
        split_dir.mkdir(parents=True)
        (split_dir / f"{directory_name}.nwb").write_bytes(b"nwb")

    inventory = inventory_falcon_h2(tmp_path)

    assert inventory.is_valid is True
    assert len(inventory.files) == 3
    assert len(inventory.files_for_split(IngestSplit.HELD_IN_CALIB)) == 1


def test_inventory_accepts_normalized_split_aliases(tmp_path) -> None:
    h2_root = tmp_path / "h2"
    for split in FALCON_H2_EXPECTED_SPLITS:
        split_dir = h2_root / split.value
        split_dir.mkdir(parents=True)
        (split_dir / f"{split.value}.nwb").write_bytes(b"nwb")

    inventory = inventory_falcon_h2(tmp_path)

    assert inventory.is_valid is True
    assert len(inventory.files) == 3
