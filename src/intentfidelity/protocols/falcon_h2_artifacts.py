from __future__ import annotations

import json
from pathlib import Path

from intentfidelity.ingest.falcon_h2 import (
    FALCON_H2_DATASET_ID,
    FALCON_H2_FILE_SUFFIXES,
    inventory_falcon_h2,
)
from intentfidelity.ingest.falcon_trials import load_falcon_h2_trials
from intentfidelity.ingest.schemas import (
    DataFile,
    DatasetInventory,
    ValidationIssue,
    ValidationSeverity,
)
from intentfidelity.labels import (
    Prediction,
    WeakTarget,
    weak_targets_from_trials,
    write_predictions_jsonl,
    write_weak_targets_jsonl,
)
from intentfidelity.protocols.artifacts import (
    ArtifactBundle,
    EvidenceLevel,
    GeneratedArtifact,
    save_artifact_bundle,
)
from intentfidelity.protocols.comparison import compare_eval_results
from intentfidelity.protocols.falcon_h2 import (
    falcon_h2_baseline_predictions,
    falcon_h2_prediction_result_from_targets,
    falcon_h2_split_from_path,
)
from intentfidelity.protocols.io import save_eval_result
from intentfidelity.protocols.schemas import ProtocolType
from intentfidelity.reports import EvalCard, render_comparison_markdown, render_markdown


def write_falcon_h2_artifact_bundle(
    source_path: str | Path,
    output_dir: str | Path,
    *,
    evidence_level: EvidenceLevel = EvidenceLevel.FIXTURE_EVIDENCE,
) -> ArtifactBundle:
    source = Path(source_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    inventory = _inventory_from_source(source)
    _raise_for_invalid_inventory(inventory)

    targets = _targets_from_inventory(inventory)
    if not targets:
        raise ValueError("cannot write FALCON H2 bundle without weak targets")

    predictions = falcon_h2_baseline_predictions(targets)
    result = falcon_h2_prediction_result_from_targets(
        targets,
        _predictions_by_method(predictions),
        metadata=_result_metadata(source, inventory, targets, predictions, evidence_level),
    )

    paths = _BundlePaths(output)
    _write_json(inventory.to_dict(), paths.inventory_json)
    write_weak_targets_jsonl(targets, paths.targets_jsonl)
    write_predictions_jsonl(predictions, paths.predictions_jsonl)
    save_eval_result(result, paths.result_json)
    paths.eval_card_md.write_text(
        render_markdown(EvalCard.from_result(result)),
        encoding="utf-8",
    )
    paths.comparison_md.write_text(
        _render_comparison_markdown(result, _evidence_scope_text(evidence_level)),
        encoding="utf-8",
    )

    generated_files = (
        GeneratedArtifact(
            "inventory_json",
            paths.inventory_json,
            "Inventory of FALCON H2 NWB/HDF5 files used by this bundle.",
        ),
        GeneratedArtifact(
            "targets_jsonl",
            paths.targets_jsonl,
            "Weak target distributions constructed from declared cue-character proxies.",
        ),
        GeneratedArtifact(
            "predictions_jsonl",
            paths.predictions_jsonl,
            "Deterministic proxy-oracle and uniform baseline predictions.",
        ),
        GeneratedArtifact(
            "result_json",
            paths.result_json,
            "EvalResult JSON for held-out-session intent-fidelity scoring.",
        ),
        GeneratedArtifact(
            "eval_card_markdown",
            paths.eval_card_md,
            "Markdown eval card with evidence scope and proxy limitations.",
        ),
        GeneratedArtifact(
            "comparison_markdown",
            paths.comparison_md,
            "Markdown method comparison report for bundle baselines.",
        ),
        GeneratedArtifact(
            "bundle_manifest_json",
            paths.bundle_manifest_json,
            "Artifact bundle manifest.",
        ),
    )
    bundle = ArtifactBundle(
        dataset_id=FALCON_H2_DATASET_ID,
        protocol=ProtocolType.HELD_OUT_SESSION,
        evidence_level=evidence_level,
        source_path=source,
        output_dir=output,
        generated_files=generated_files,
        metadata={
            "data_file_count": len(inventory.files),
            "target_count": len(targets),
            "prediction_count": len(predictions),
            "target_type": "handwriting_cue_character",
        },
    )
    save_artifact_bundle(bundle, paths.bundle_manifest_json)
    return bundle


class _BundlePaths:
    def __init__(self, output_dir: Path) -> None:
        self.inventory_json = output_dir / "inventory.json"
        self.targets_jsonl = output_dir / "targets.jsonl"
        self.predictions_jsonl = output_dir / "predictions.jsonl"
        self.result_json = output_dir / "result.json"
        self.eval_card_md = output_dir / "eval_card.md"
        self.comparison_md = output_dir / "comparison.md"
        self.bundle_manifest_json = output_dir / "bundle_manifest.json"


def _inventory_from_source(source: Path) -> DatasetInventory:
    if source.is_file():
        return _single_file_inventory(source)
    return inventory_falcon_h2(source)


def _single_file_inventory(path: Path) -> DatasetInventory:
    if path.suffix.lower() not in FALCON_H2_FILE_SUFFIXES:
        issue = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            code="unsupported_file_suffix",
            message="FALCON H2 bundle input must be an NWB/HDF5 file.",
            path=str(path),
        )
        return DatasetInventory(FALCON_H2_DATASET_ID, path.parent, (), (issue,))

    file = DataFile(
        dataset_id=FALCON_H2_DATASET_ID,
        split=falcon_h2_split_from_path(path),
        path=path,
        size_bytes=path.stat().st_size,
        metadata={"suffix": path.suffix.lower(), "source_mode": "single_file"},
    )
    return DatasetInventory(FALCON_H2_DATASET_ID, path.parent, (file,))


def _raise_for_invalid_inventory(inventory: DatasetInventory) -> None:
    if inventory.is_valid and inventory.files:
        return
    if not inventory.files and inventory.is_valid:
        raise ValueError("FALCON H2 inventory did not contain NWB/HDF5 files")
    errors = [issue for issue in inventory.issues if issue.severity == ValidationSeverity.ERROR]
    if not errors:
        raise ValueError("FALCON H2 inventory is not usable")
    details = "; ".join(f"{issue.code}: {issue.message}" for issue in errors)
    raise ValueError(f"invalid FALCON H2 inventory: {details}")


def _targets_from_inventory(inventory: DatasetInventory) -> tuple[WeakTarget, ...]:
    targets: list[WeakTarget] = []
    for data_file in sorted(inventory.files, key=lambda item: (item.split.value, str(item.path))):
        trials = load_falcon_h2_trials(data_file.path, data_file.split)
        targets.extend(weak_targets_from_trials(trials))
    return tuple(targets)


def _predictions_by_method(
    predictions: tuple[Prediction, ...],
) -> dict[str, tuple[Prediction, ...]]:
    grouped: dict[str, list[Prediction]] = {}
    for prediction in predictions:
        grouped.setdefault(prediction.method_id, []).append(prediction)
    return {method_id: tuple(values) for method_id, values in grouped.items()}


def _result_metadata(
    source: Path,
    inventory: DatasetInventory,
    targets: tuple[WeakTarget, ...],
    predictions: tuple[Prediction, ...],
    evidence_level: EvidenceLevel,
) -> dict[str, object]:
    return {
        "source_path": str(source),
        "data_file_count": len(inventory.files),
        "target_count": len(targets),
        "prediction_count": len(predictions),
        "target_type": "handwriting_cue_character",
        "weak_target_source": "declared FALCON H2 trial cue text",
        "evidence_level": evidence_level.value,
        "baseline_scope": _evidence_scope_text(evidence_level),
        "proxy_limitations": (
            "Weak targets are cue-character intent proxies; this result does "
            "not claim direct access to true intent."
        ),
    }


def _evidence_scope_text(evidence_level: EvidenceLevel) -> str:
    if evidence_level == EvidenceLevel.FIXTURE_EVIDENCE:
        return (
            "fixture_evidence: synthetic NWB/HDF5 fixtures validate bundle "
            "plumbing; this is not downloaded FALCON H2 dataset evidence."
        )
    if evidence_level == EvidenceLevel.DOWNLOADED_DATASET_EVIDENCE:
        return (
            "downloaded_dataset_evidence: local run against user-provided "
            "FALCON H2 NWB/HDF5 files; targets remain declared cue proxies."
        )
    return f"{evidence_level.value}: scope is limited to declared proxy artifacts."


def _render_comparison_markdown(result, evidence_scope: str) -> str:
    report = compare_eval_results(result)
    base = render_comparison_markdown(report).rstrip()
    return (
        f"{base}\n\n"
        "## Evidence Scope\n"
        f"- {evidence_scope}\n"
        "- Comparison rankings are computed against declared weak target "
        "distributions, not directly observed true intent.\n"
    )


def _write_json(payload: dict, path: Path) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
