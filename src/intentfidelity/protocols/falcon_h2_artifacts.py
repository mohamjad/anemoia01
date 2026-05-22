from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from intentfidelity import __version__
from intentfidelity.ingest.falcon_h2 import (
    FALCON_H2_DATASET_ID,
    FALCON_H2_FILE_SUFFIXES,
    inventory_falcon_h2,
)
from intentfidelity.ingest.falcon_examples import load_falcon_h2_labeled_examples
from intentfidelity.ingest.falcon_trials import load_falcon_h2_trials
from intentfidelity.ingest.schemas import (
    DataFile,
    DatasetInventory,
    IngestSplit,
    ValidationIssue,
    ValidationSeverity,
)
from intentfidelity.baselines import (
    project_prediction_to_target_support,
    run_default_centroid_baselines,
)
from intentfidelity.labels import (
    Prediction,
    WeakTarget,
    read_predictions_jsonl,
    read_weak_targets_jsonl,
    weak_targets_from_trials,
    write_predictions_jsonl,
    write_weak_targets_jsonl,
)
from intentfidelity.protocols.artifacts import (
    ArtifactBundle,
    ArtifactValidationIssue,
    ArtifactValidationReport,
    ArtifactValidationSeverity,
    EvidenceLevel,
    GeneratedArtifact,
    load_artifact_bundle,
    save_artifact_bundle,
    validate_artifact_bundle,
)
from intentfidelity.protocols.comparison import compare_eval_results
from intentfidelity.protocols.falcon_h2 import (
    falcon_h2_baseline_predictions,
    falcon_h2_method_comparison_result_from_targets,
    falcon_h2_prediction_result_from_targets,
    falcon_h2_split_from_path,
)
from intentfidelity.protocols.io import load_eval_result, save_eval_result
from intentfidelity.protocols.schemas import ProtocolType
from intentfidelity.reports import EvalCard, render_comparison_markdown, render_markdown


FALCON_H2_BUNDLE_REQUIRED_KINDS: tuple[str, ...] = (
    "inventory_json",
    "targets_jsonl",
    "predictions_jsonl",
    "result_json",
    "eval_card_markdown",
    "comparison_markdown",
    "bundle_manifest_json",
)

FALCON_H2_FEATURE_BUNDLE_REQUIRED_KINDS: tuple[str, ...] = (
    "train_inventory_json",
    "test_inventory_json",
    "targets_jsonl",
    "predictions_jsonl",
    "baseline_runs_json",
    "result_json",
    "eval_card_markdown",
    "comparison_markdown",
    "bundle_manifest_json",
)


def write_falcon_h2_artifact_bundle(
    source_path: str | Path,
    output_dir: str | Path,
    *,
    evidence_level: EvidenceLevel = EvidenceLevel.FIXTURE_EVIDENCE,
    command: str | None = None,
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
    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    source_files = _source_file_provenance(inventory)
    result = falcon_h2_prediction_result_from_targets(
        targets,
        _predictions_by_method(predictions),
        metadata=_result_metadata(
            source,
            inventory,
            targets,
            predictions,
            evidence_level,
            generated_at=generated_at,
            source_files=source_files,
            command=command,
        ),
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
            "generated_at": generated_at,
            "generated_by": "intentfidelity",
            "intentfidelity_version": __version__,
            "command": command,
            "source_files": source_files,
        },
    )
    save_artifact_bundle(bundle, paths.bundle_manifest_json)
    return bundle


def validate_falcon_h2_artifact_bundle(
    bundle_dir: str | Path,
) -> ArtifactValidationReport:
    report = validate_artifact_bundle(
        bundle_dir,
        required_kinds=FALCON_H2_BUNDLE_REQUIRED_KINDS,
    )
    if not report.is_valid:
        return report

    issues = list(report.issues)
    root = Path(bundle_dir)
    manifest_path = root / "bundle_manifest.json"
    bundle = load_artifact_bundle(manifest_path)
    artifacts = {artifact.kind: artifact.path for artifact in bundle.generated_files}

    targets = read_weak_targets_jsonl(artifacts["targets_jsonl"])
    predictions = read_predictions_jsonl(artifacts["predictions_jsonl"])
    result = load_eval_result(artifacts["result_json"])
    eval_card = artifacts["eval_card_markdown"].read_text(encoding="utf-8")
    comparison = artifacts["comparison_markdown"].read_text(encoding="utf-8")

    _append_count_issue(
        issues,
        "target_count_mismatch",
        bundle.metadata.get("target_count"),
        len(targets),
        manifest_path,
    )
    _append_count_issue(
        issues,
        "prediction_count_mismatch",
        bundle.metadata.get("prediction_count"),
        len(predictions),
        manifest_path,
    )
    _append_count_issue(
        issues,
        "result_target_count_mismatch",
        result.metadata.get("target_count"),
        len(targets),
        artifacts["result_json"],
    )
    _append_count_issue(
        issues,
        "result_prediction_count_mismatch",
        result.metadata.get("prediction_count"),
        len(predictions),
        artifacts["result_json"],
    )

    if result.dataset_id != FALCON_H2_DATASET_ID:
        issues.append(
            _error(
                "unexpected_result_dataset_id",
                "result.json must be for dataset_id falcon_h2.",
                artifacts["result_json"],
            )
        )
    if result.metadata.get("evidence_level") != bundle.evidence_level.value:
        issues.append(
            _error(
                "evidence_level_mismatch",
                "result.json evidence_level must match bundle_manifest.json.",
                artifacts["result_json"],
            )
        )
    if not _has_valid_source_file_hashes(bundle.metadata.get("source_files")):
        issues.append(
            _error(
                "missing_source_file_hashes",
                "bundle_manifest.json must include SHA-256 hashes for source files.",
                manifest_path,
            )
        )
    if bundle.evidence_level.value not in eval_card:
        issues.append(
            _error(
                "eval_card_missing_evidence_scope",
                "eval_card.md must include the bundle evidence level.",
                artifacts["eval_card_markdown"],
            )
        )
    if "declared weak target distributions" not in eval_card:
        issues.append(
            _error(
                "eval_card_missing_proxy_scope",
                "eval_card.md must state that scoring uses declared weak targets.",
                artifacts["eval_card_markdown"],
            )
        )
    if "not directly observed true intent" not in comparison:
        issues.append(
            _error(
                "comparison_missing_intent_limitation",
                "comparison.md must state that true intent is not directly observed.",
                artifacts["comparison_markdown"],
            )
        )

    return ArtifactValidationReport(
        bundle_dir=report.bundle_dir,
        manifest_path=report.manifest_path,
        checked_files=report.checked_files,
        issues=tuple(issues),
    )


def write_falcon_h2_feature_baseline_bundle(
    train_source_path: str | Path,
    test_source_path: str | Path,
    output_dir: str | Path,
    *,
    evidence_level: EvidenceLevel = EvidenceLevel.DOWNLOADED_DATASET_EVIDENCE,
    command: str | None = None,
    support_floor_mass: float = 1e-6,
) -> ArtifactBundle:
    train_source = Path(train_source_path)
    test_source = Path(test_source_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    train_inventory = _inventory_from_source(
        train_source,
        expected_split=IngestSplit.HELD_IN_CALIB,
    )
    test_inventory = _inventory_from_source(
        test_source,
        expected_split=IngestSplit.HELD_OUT_CALIB,
    )
    _raise_for_invalid_inventory(train_inventory)
    _raise_for_invalid_inventory(test_inventory)

    train_examples = _examples_from_inventory(train_inventory)
    test_examples = _examples_from_inventory(test_inventory)
    if not train_examples or not test_examples:
        raise ValueError("feature bundle requires train and test labeled examples")

    all_test_targets = _targets_from_inventory(test_inventory)
    targets_by_sample = {target.sample_id: target for target in all_test_targets}
    scored_targets = tuple(
        targets_by_sample[example.sample_id]
        for example in test_examples
        if example.sample_id in targets_by_sample
    )
    if len(scored_targets) != len(test_examples):
        raise ValueError("test examples and weak targets must share sample ids")

    runs = run_default_centroid_baselines(train_examples, test_examples)
    projected_predictions = tuple(
        project_prediction_to_target_support(
            prediction,
            targets_by_sample[prediction.sample_id],
            floor_mass=support_floor_mass,
        )
        for run in runs
        for prediction in run.predictions
    )
    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    train_source_files = _source_file_provenance(train_inventory)
    test_source_files = _source_file_provenance(test_inventory)
    result = falcon_h2_method_comparison_result_from_targets(
        scored_targets,
        _predictions_by_method(projected_predictions),
        metadata={
            "source_path": str(test_source),
            "train_source_path": str(train_source),
            "data_file_count": len(train_inventory.files) + len(test_inventory.files),
            "train_file_count": len(train_inventory.files),
            "test_file_count": len(test_inventory.files),
            "train_example_count": len(train_examples),
            "test_example_count": len(test_examples),
            "target_count": len(scored_targets),
            "prediction_count": len(projected_predictions),
            "target_type": "handwriting_cue_character",
            "weak_target_source": "declared FALCON H2 trial cue text",
            "evidence_level": evidence_level.value,
            "generated_at": generated_at,
            "generated_by": "intentfidelity",
            "intentfidelity_version": __version__,
            "command": command,
            "support_projection": "declared_target_support",
            "support_floor_mass": support_floor_mass,
            "train_source_files": train_source_files,
            "test_source_files": test_source_files,
            "baseline_scope": _feature_evidence_scope_text(evidence_level),
            "proxy_limitations": (
                "Feature baselines are scored against declared cue-character "
                "intent proxies; this result does not claim direct access to "
                "true intent."
            ),
        },
    )

    paths = _FeatureBundlePaths(output)
    _write_json(train_inventory.to_dict(), paths.train_inventory_json)
    _write_json(test_inventory.to_dict(), paths.test_inventory_json)
    write_weak_targets_jsonl(scored_targets, paths.targets_jsonl)
    write_predictions_jsonl(projected_predictions, paths.predictions_jsonl)
    _write_json(_baseline_runs_payload(runs), paths.baseline_runs_json)
    save_eval_result(result, paths.result_json)
    paths.eval_card_md.write_text(
        render_markdown(EvalCard.from_result(result)),
        encoding="utf-8",
    )
    paths.comparison_md.write_text(
        _render_comparison_markdown(result, _feature_evidence_scope_text(evidence_level)),
        encoding="utf-8",
    )

    generated_files = (
        GeneratedArtifact(
            "train_inventory_json",
            paths.train_inventory_json,
            "Inventory of train FALCON H2 NWB/HDF5 files.",
        ),
        GeneratedArtifact(
            "test_inventory_json",
            paths.test_inventory_json,
            "Inventory of test FALCON H2 NWB/HDF5 files.",
        ),
        GeneratedArtifact(
            "targets_jsonl",
            paths.targets_jsonl,
            "Scored weak target distributions from declared cue-character proxies.",
        ),
        GeneratedArtifact(
            "predictions_jsonl",
            paths.predictions_jsonl,
            "Centroid feature-baseline predictions projected to target support.",
        ),
        GeneratedArtifact(
            "baseline_runs_json",
            paths.baseline_runs_json,
            "Train/test counts for each feature baseline method.",
        ),
        GeneratedArtifact(
            "result_json",
            paths.result_json,
            "EvalResult JSON with proxy top-1 error and intent-fidelity log loss.",
        ),
        GeneratedArtifact(
            "eval_card_markdown",
            paths.eval_card_md,
            "Markdown eval card with evidence scope and proxy limitations.",
        ),
        GeneratedArtifact(
            "comparison_markdown",
            paths.comparison_md,
            "Markdown method comparison report for feature baselines.",
        ),
        GeneratedArtifact(
            "bundle_manifest_json",
            paths.bundle_manifest_json,
            "Feature-baseline artifact bundle manifest.",
        ),
    )
    bundle = ArtifactBundle(
        dataset_id=FALCON_H2_DATASET_ID,
        protocol=ProtocolType.HELD_OUT_SESSION,
        evidence_level=evidence_level,
        source_path=test_source,
        output_dir=output,
        generated_files=generated_files,
        metadata={
            "train_source_path": str(train_source),
            "test_source_path": str(test_source),
            "train_file_count": len(train_inventory.files),
            "test_file_count": len(test_inventory.files),
            "train_example_count": len(train_examples),
            "test_example_count": len(test_examples),
            "target_count": len(scored_targets),
            "prediction_count": len(projected_predictions),
            "target_type": "handwriting_cue_character",
            "generated_at": generated_at,
            "generated_by": "intentfidelity",
            "intentfidelity_version": __version__,
            "command": command,
            "support_projection": "declared_target_support",
            "support_floor_mass": support_floor_mass,
            "train_source_files": train_source_files,
            "test_source_files": test_source_files,
        },
    )
    save_artifact_bundle(bundle, paths.bundle_manifest_json)
    return bundle


def validate_falcon_h2_feature_baseline_bundle(
    bundle_dir: str | Path,
) -> ArtifactValidationReport:
    report = validate_artifact_bundle(
        bundle_dir,
        required_kinds=FALCON_H2_FEATURE_BUNDLE_REQUIRED_KINDS,
    )
    if not report.is_valid:
        return report
    return _validate_falcon_bundle_semantics(report)


def _validate_falcon_bundle_semantics(
    report: ArtifactValidationReport,
) -> ArtifactValidationReport:
    issues = list(report.issues)
    bundle = load_artifact_bundle(report.manifest_path)
    artifacts = {artifact.kind: artifact.path for artifact in bundle.generated_files}

    targets = read_weak_targets_jsonl(artifacts["targets_jsonl"])
    predictions = read_predictions_jsonl(artifacts["predictions_jsonl"])
    result = load_eval_result(artifacts["result_json"])
    eval_card = artifacts["eval_card_markdown"].read_text(encoding="utf-8")
    comparison = artifacts["comparison_markdown"].read_text(encoding="utf-8")

    _append_count_issue(
        issues,
        "target_count_mismatch",
        bundle.metadata.get("target_count"),
        len(targets),
        report.manifest_path,
    )
    _append_count_issue(
        issues,
        "prediction_count_mismatch",
        bundle.metadata.get("prediction_count"),
        len(predictions),
        report.manifest_path,
    )
    _append_count_issue(
        issues,
        "result_target_count_mismatch",
        result.metadata.get("target_count"),
        len(targets),
        artifacts["result_json"],
    )
    _append_count_issue(
        issues,
        "result_prediction_count_mismatch",
        result.metadata.get("prediction_count"),
        len(predictions),
        artifacts["result_json"],
    )

    if result.dataset_id != FALCON_H2_DATASET_ID:
        issues.append(
            _error(
                "unexpected_result_dataset_id",
                "result.json must be for dataset_id falcon_h2.",
                artifacts["result_json"],
            )
        )
    if result.metadata.get("evidence_level") != bundle.evidence_level.value:
        issues.append(
            _error(
                "evidence_level_mismatch",
                "result.json evidence_level must match bundle_manifest.json.",
                artifacts["result_json"],
            )
        )
    if not _bundle_has_source_file_hashes(bundle):
        issues.append(
            _error(
                "missing_source_file_hashes",
                "bundle manifest must include SHA-256 hashes for source files.",
                report.manifest_path,
            )
        )
    if bundle.evidence_level.value not in eval_card:
        issues.append(
            _error(
                "eval_card_missing_evidence_scope",
                "eval_card.md must include the bundle evidence level.",
                artifacts["eval_card_markdown"],
            )
        )
    if "declared weak target distributions" not in eval_card:
        issues.append(
            _error(
                "eval_card_missing_proxy_scope",
                "eval_card.md must state that scoring uses declared weak targets.",
                artifacts["eval_card_markdown"],
            )
        )
    if "not directly observed true intent" not in comparison:
        issues.append(
            _error(
                "comparison_missing_intent_limitation",
                "comparison.md must state that true intent is not directly observed.",
                artifacts["comparison_markdown"],
            )
        )

    return ArtifactValidationReport(
        bundle_dir=report.bundle_dir,
        manifest_path=report.manifest_path,
        checked_files=report.checked_files,
        issues=tuple(issues),
    )


class _BundlePaths:
    def __init__(self, output_dir: Path) -> None:
        self.inventory_json = output_dir / "inventory.json"
        self.targets_jsonl = output_dir / "targets.jsonl"
        self.predictions_jsonl = output_dir / "predictions.jsonl"
        self.result_json = output_dir / "result.json"
        self.eval_card_md = output_dir / "eval_card.md"
        self.comparison_md = output_dir / "comparison.md"
        self.bundle_manifest_json = output_dir / "bundle_manifest.json"


class _FeatureBundlePaths:
    def __init__(self, output_dir: Path) -> None:
        self.train_inventory_json = output_dir / "train_inventory.json"
        self.test_inventory_json = output_dir / "test_inventory.json"
        self.targets_jsonl = output_dir / "targets.jsonl"
        self.predictions_jsonl = output_dir / "predictions.jsonl"
        self.baseline_runs_json = output_dir / "baseline_runs.json"
        self.result_json = output_dir / "result.json"
        self.eval_card_md = output_dir / "eval_card.md"
        self.comparison_md = output_dir / "comparison.md"
        self.bundle_manifest_json = output_dir / "bundle_manifest.json"


def _inventory_from_source(
    source: Path,
    *,
    expected_split: IngestSplit | None = None,
) -> DatasetInventory:
    if source.is_file():
        return _single_file_inventory(source)
    inventory = inventory_falcon_h2(source)
    if inventory.files or not source.is_dir():
        if expected_split is None:
            return inventory
        return DatasetInventory(
            dataset_id=inventory.dataset_id,
            root=inventory.root,
            files=inventory.files_for_split(expected_split),
            issues=inventory.issues,
        )

    direct_files = _find_direct_data_files(source)
    if not direct_files:
        return inventory
    return _direct_directory_inventory(source, direct_files, expected_split)


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


def _direct_directory_inventory(
    root: Path,
    files: tuple[Path, ...],
    expected_split: IngestSplit | None,
) -> DatasetInventory:
    data_files = tuple(
        DataFile(
            dataset_id=FALCON_H2_DATASET_ID,
            split=expected_split or falcon_h2_split_from_path(path),
            path=path,
            size_bytes=path.stat().st_size,
            metadata={"suffix": path.suffix.lower(), "source_mode": "direct_directory"},
        )
        for path in files
    )
    return DatasetInventory(FALCON_H2_DATASET_ID, root, data_files)


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


def _examples_from_inventory(inventory: DatasetInventory):
    examples = []
    for data_file in sorted(inventory.files, key=lambda item: (item.split.value, str(item.path))):
        examples.extend(load_falcon_h2_labeled_examples(data_file.path, data_file.split))
    return tuple(examples)


def _predictions_by_method(
    predictions: tuple[Prediction, ...],
) -> dict[str, tuple[Prediction, ...]]:
    grouped: dict[str, list[Prediction]] = {}
    for prediction in predictions:
        grouped.setdefault(prediction.method_id, []).append(prediction)
    return {method_id: tuple(values) for method_id, values in grouped.items()}


def _baseline_runs_payload(runs) -> dict[str, object]:
    return {
        "runs": [
            {
                "method_id": run.method_id,
                "train_count": run.train_count,
                "test_count": run.test_count,
                "prediction_count": len(run.predictions),
            }
            for run in runs
        ]
    }


def _result_metadata(
    source: Path,
    inventory: DatasetInventory,
    targets: tuple[WeakTarget, ...],
    predictions: tuple[Prediction, ...],
    evidence_level: EvidenceLevel,
    *,
    generated_at: str,
    source_files: tuple[dict[str, object], ...],
    command: str | None,
) -> dict[str, object]:
    return {
        "source_path": str(source),
        "data_file_count": len(inventory.files),
        "target_count": len(targets),
        "prediction_count": len(predictions),
        "target_type": "handwriting_cue_character",
        "weak_target_source": "declared FALCON H2 trial cue text",
        "evidence_level": evidence_level.value,
        "generated_at": generated_at,
        "generated_by": "intentfidelity",
        "intentfidelity_version": __version__,
        "command": command,
        "source_files": source_files,
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


def _feature_evidence_scope_text(evidence_level: EvidenceLevel) -> str:
    if evidence_level == EvidenceLevel.DOWNLOADED_DATASET_EVIDENCE:
        return (
            "downloaded_dataset_evidence: local feature-baseline comparison "
            "against user-provided FALCON H2 NWB/HDF5 files; targets remain "
            "declared cue proxies."
        )
    return f"{evidence_level.value}: feature baseline scope is proxy-limited."


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


def _find_direct_data_files(source: Path) -> tuple[Path, ...]:
    if not source.is_dir():
        return ()
    return tuple(
        sorted(
            (
                path
                for path in source.rglob("*")
                if path.is_file() and path.suffix.lower() in FALCON_H2_FILE_SUFFIXES
            ),
            key=lambda path: str(path),
        )
    )


def _source_file_provenance(
    inventory: DatasetInventory,
) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "path": str(data_file.path),
            "split": data_file.split.value,
            "size_bytes": data_file.size_bytes,
            "sha256": _sha256_file(data_file.path),
        }
        for data_file in sorted(
            inventory.files,
            key=lambda item: (item.split.value, str(item.path)),
        )
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _append_count_issue(
    issues: list[ArtifactValidationIssue],
    code: str,
    observed: object,
    expected: int,
    path: Path,
) -> None:
    if observed == expected:
        return
    issues.append(
        _error(
            code,
            f"metadata count {observed!r} does not match artifact count {expected}.",
            path,
        )
    )


def _has_valid_source_file_hashes(source_files: object) -> bool:
    if not isinstance(source_files, (list, tuple)) or not source_files:
        return False
    for item in source_files:
        if not isinstance(item, dict):
            return False
        digest = item.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            return False
    return True


def _bundle_has_source_file_hashes(bundle: ArtifactBundle) -> bool:
    source_files = bundle.metadata.get("source_files")
    if source_files is not None:
        return _has_valid_source_file_hashes(source_files)
    train_files = bundle.metadata.get("train_source_files")
    test_files = bundle.metadata.get("test_source_files")
    return (
        _has_valid_source_file_hashes(train_files)
        and _has_valid_source_file_hashes(test_files)
    )


def _error(
    code: str,
    message: str,
    path: Path,
) -> ArtifactValidationIssue:
    return ArtifactValidationIssue(
        ArtifactValidationSeverity.ERROR,
        code,
        message,
        path,
    )


def _write_json(payload: dict, path: Path) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
