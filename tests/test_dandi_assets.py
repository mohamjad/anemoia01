from intentfidelity.resources.dandi import parse_dandi_assets


def test_parse_dandi_assets_extracts_manifest_records() -> None:
    assets = parse_dandi_assets(
        {
            "results": [
                {
                    "asset_id": "abc",
                    "path": "sub-T5-held-out-calib/file.nwb",
                    "size": 123,
                }
            ]
        }
    )

    assert assets[0].asset_id == "abc"
    assert assets[0].path.endswith(".nwb")
    assert assets[0].size == 123

