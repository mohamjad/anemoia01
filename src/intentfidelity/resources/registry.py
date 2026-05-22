from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Iterable

from intentfidelity.resources.schema import (
    ManifestValidationError,
    ResourceManifest,
    load_manifest,
)


MANIFEST_PACKAGE = "intentfidelity.resources.manifests"


def iter_manifest_paths(directory: Path | None = None) -> Iterable[Path]:
    if directory is not None:
        yield from sorted(directory.glob("*.yaml"))
        return

    manifest_root = resources.files(MANIFEST_PACKAGE)
    for item in sorted(manifest_root.iterdir(), key=lambda path: path.name):
        if item.name.endswith(".yaml"):
            with resources.as_file(item) as path:
                yield path


def load_manifests(directory: Path | None = None) -> list[ResourceManifest]:
    manifests = [load_manifest(path) for path in iter_manifest_paths(directory)]
    _validate_unique_registry(manifests)
    return sorted(manifests, key=lambda manifest: manifest.priority)


def get_manifest(dataset_id: str, directory: Path | None = None) -> ResourceManifest:
    for manifest in load_manifests(directory):
        if manifest.dataset_id == dataset_id:
            return manifest
    raise KeyError(f"unknown dataset_id: {dataset_id}")


def _validate_unique_registry(manifests: list[ResourceManifest]) -> None:
    dataset_ids = [manifest.dataset_id for manifest in manifests]
    duplicate_ids = sorted(
        {dataset_id for dataset_id in dataset_ids if dataset_ids.count(dataset_id) > 1}
    )
    if duplicate_ids:
        raise ManifestValidationError(
            f"duplicate dataset_id values: {', '.join(duplicate_ids)}"
        )

    priorities = [manifest.priority for manifest in manifests]
    duplicate_priorities = sorted(
        {priority for priority in priorities if priorities.count(priority) > 1}
    )
    if duplicate_priorities:
        formatted = ", ".join(str(priority) for priority in duplicate_priorities)
        raise ManifestValidationError(f"duplicate priority values: {formatted}")
