from __future__ import annotations

from dataclasses import dataclass
import json
from urllib.request import urlopen


DANDI_000950_ASSETS_URL = (
    "https://api.dandiarchive.org/api/dandisets/000950/"
    "versions/0.241029.1403/assets/"
)


@dataclass(frozen=True)
class DandiAsset:
    asset_id: str
    path: str
    size: int


def parse_dandi_assets(payload: dict) -> tuple[DandiAsset, ...]:
    return tuple(
        DandiAsset(
            asset_id=item["asset_id"],
            path=item["path"],
            size=int(item["size"]),
        )
        for item in payload.get("results", [])
    )


def fetch_dandi_assets(url: str = DANDI_000950_ASSETS_URL) -> tuple[DandiAsset, ...]:
    with urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return parse_dandi_assets(payload)

