from pathlib import Path

import pytest

from intentfidelity.ingest.falcon_session import FalconSessionKey, session_date_from_path
from intentfidelity.ingest import IngestSplit


def test_session_date_from_path_extracts_dandiset_name() -> None:
    assert (
        session_date_from_path("sub-T5-held-out-calib_ses-20230417.nwb")
        == "2023-04-17"
    )


def test_session_date_from_path_accepts_download_alias() -> None:
    assert session_date_from_path("held_out_20230417.nwb") == "2023-04-17"


def test_session_date_from_path_rejects_unknown_names() -> None:
    with pytest.raises(ValueError, match="cannot infer"):
        session_date_from_path("session.nwb")


def test_falcon_session_key_normalizes_path() -> None:
    key = FalconSessionKey(
        dataset_id="falcon_h2",
        split=IngestSplit.HELD_OUT_CALIB,
        session_date="2023-04-17",
        source_path=Path("x.nwb"),
    )

    assert key.source_path == Path("x.nwb")
