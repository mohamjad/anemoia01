from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any

import yaml


DATASET_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")
RESOURCE_STATUSES = {"planned", "reference", "active"}


class ManifestValidationError(ValueError):
    """Raised when a resource manifest does not match the registry contract."""


@dataclass(frozen=True)
class ResourceManifest:
    dataset_id: str
    title: str
    domain: str
    status: str
    priority: int
    access: str
    modalities: tuple[str, ...]
    weak_proxy_sources: tuple[str, ...]
    known_limitations: tuple[str, ...]
    first_pass_role: str
    source_url: str | None = None
    subjects: int | None = None
    sessions: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> ResourceManifest:
        missing = [
            key
            for key in (
                "dataset_id",
                "title",
                "domain",
                "status",
                "priority",
                "access",
                "modalities",
                "weak_proxy_sources",
                "known_limitations",
                "first_pass_role",
            )
            if key not in payload
        ]
        if missing:
            raise ManifestValidationError(
                f"manifest missing required fields: {', '.join(missing)}"
            )

        dataset_id = _required_str(payload, "dataset_id")
        if not DATASET_ID_PATTERN.fullmatch(dataset_id):
            raise ManifestValidationError(
                "dataset_id must use lowercase letters, numbers, and underscores"
            )

        status = _required_str(payload, "status")
        if status not in RESOURCE_STATUSES:
            allowed = ", ".join(sorted(RESOURCE_STATUSES))
            raise ManifestValidationError(f"status must be one of: {allowed}")

        return cls(
            dataset_id=dataset_id,
            title=_required_str(payload, "title"),
            domain=_required_str(payload, "domain"),
            status=status,
            priority=_required_int(payload, "priority"),
            access=_required_str(payload, "access"),
            modalities=_required_str_tuple(payload, "modalities"),
            weak_proxy_sources=_required_str_tuple(payload, "weak_proxy_sources"),
            known_limitations=_required_str_tuple(payload, "known_limitations"),
            first_pass_role=_required_str(payload, "first_pass_role"),
            source_url=_optional_str(payload, "source_url"),
            subjects=_optional_int(payload, "subjects"),
            sessions=_optional_int(payload, "sessions"),
            metadata=dict(payload.get("metadata", {})),
        )


def load_manifest(path: str | Path) -> ResourceManifest:
    manifest_path = Path(path)
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ManifestValidationError("manifest root must be a mapping")
    return ResourceManifest.from_mapping(payload)


def _required_str(payload: dict[str, Any], key: str) -> str:
    value = payload[key]
    if not isinstance(value, str) or not value.strip():
        raise ManifestValidationError(f"{key} must be a non-empty string")
    return value


def _optional_str(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ManifestValidationError(f"{key} must be a non-empty string when set")
    return value


def _required_int(payload: dict[str, Any], key: str) -> int:
    value = payload[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise ManifestValidationError(f"{key} must be an integer")
    return value


def _optional_int(payload: dict[str, Any], key: str) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ManifestValidationError(f"{key} must be an integer when set")
    return value


def _required_str_tuple(payload: dict[str, Any], key: str) -> tuple[str, ...]:
    value = payload[key]
    if not isinstance(value, list) or not value:
        raise ManifestValidationError(f"{key} must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ManifestValidationError(f"{key} must contain only non-empty strings")
    return tuple(value)

