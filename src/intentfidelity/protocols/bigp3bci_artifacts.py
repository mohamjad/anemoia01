from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from intentfidelity import __version__
from intentfidelity.baselines import selection_sanity_predictions
from intentfidelity.ingest.bigp3bci import (
    BIGP3BCI_DATASET_ID,
    BigP3BCIDataFile,
    BigP3BCIInventory,
    bigp3bci_event_extraction_contract,
    inventory_bigp3bci,
    load_bigp3bci_selection_events,
)
from intentfidelity.ingest.schemas import ValidationSeverity
from intentfidelity.labels import (
    Prediction,
    read_p300_events_jsonl,
    read_predictions_jsonl,
    read_weak_targets_jsonl,
    write_p300_events_jsonl,
    write_predictions_jsonl,
    write_weak_targets_jsonl,
)
from intentfidelity.labels.p300 import P300SelectionEvent, weak_target_from_p300_event
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
from intentfidelity.protocols.io import load_eval_result, save_eval_result
from intentfidelity.protocols.schemas import ProtocolType
from intentfidelity.protocols.selection import selection_eval_result
from intentfidelity.reports import (
    EvalCard,
    render_comparison_markdown,
    render_markdown,
    render_selection_markdown,
)


BIGP3BCI_BUNDLE_REQUIRED_KINDS: tuple[str, ...] = (
    "inventory_json",
    "events_jsonl",
    "targets_jsonl",
    "predictions_jsonl",
    "result_json",
    "eval_card_markdown",
    "selection_report_markdown",
    "comparison_markdown",
    "bundle_manifest_json",
)


def write_bigp3bci_artifact_bundle(
    data_root: str | Path,
    output_dir: str | Path,
    *,
    evidence_level: EvidenceLevel = EvidenceLevel.FIXTURE_EVIDENCE,
    command: str | None = None,
) -> ArtifactBundle:
    source = Path(data_root)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    inventory = inventory_bigp3bci(source)
    _raise_for_invalid_inventory(inventory)
    events = _events_from_inventory(inventory)
    if not events:
        raise ValueError("cannot write bigP3BCI bundle without selection events")

    targets = tuple(weak_target_from_p300_event(event) for event in events)
    predictions = selection_sanity_predictions(events)
    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    source_files = _source_file_provenance(inventory)
    metadata = _result_metadata(
        source,
        inventory,
        event_count=len(events),
        target_count=len(targets),
        prediction_count=len(predictions),
        evidence_level=evidence_level,
        generated_at=generated_at,
        source_files=source_files,
        command=command,
    )
    result = selection_eval_result(
        events,
        _predictions_by_method(predictions),
        dataset_id=BIGP3BCI_DATASET_ID,
        metadata=metadata,
    )

    paths = _BundlePaths(output)
    _write_json(inventory.to_dict(), paths.inventory_json)
    write_p300_events_jsonl(events, paths.events_jsonl)
    write_weak_targets_jsonl(targets, paths.targets_jsonl)
    write_predictions_jsonl(predictions, paths.predictions_jsonl)
    save_eval_result(result, paths.result_json)
    paths.eval_card_md.write_text(
        render_markdown(EvalCard.from_result(result)),
        encoding="utf-8",
    )
    paths.selection_report_md.write_text(
        _render_selection_report(result, _evidence_scope_text(evidence_level)),
        encoding="utf-8",
    )
    paths.comparison_md.write_text(
        _render_comparison_report(result, _evidence_scope_text(evidence_level)),
        encoding="utf-8",
    )

    generated_files = (
        GeneratedArtifact(
            "inventory_json",
            paths.inventory_json,
            "Inventory of bigP3BCI EDF+ files used by this bundle.",
        ),
        GeneratedArtifact(
            "events_jsonl",
            paths.events_jsonl,
            "Typed P300SelectionEvent rows extracted from numeric EDF+ records.",
        ),
        GeneratedArtifact(
            "targets_jsonl",
            paths.targets_jsonl,
            "Weak target distributions constructed from CurrentTarget records.",
        ),
        GeneratedArtifact(
            "predictions_jsonl",
            paths.predictions_jsonl,
            "Deterministic selection sanity baseline predictions.",
        ),
        GeneratedArtifact(
            "result_json",
            paths.result_json,
            "EvalResult JSON for selection intent-fidelity proxy scoring.",
        ),
        GeneratedArtifact(
            "eval_card_markdown",
            paths.eval_card_md,
            "Markdown eval card with evidence scope and proxy limitations.",
        ),
        GeneratedArtifact(
            "selection_report_markdown",
            paths.selection_report_md,
            "Markdown selection report for extracted P300 proxy events.",
        ),
        GeneratedArtifact(
            "comparison_markdown",
            paths.comparison_md,
            "Markdown method comparison report for bundle sanity baselines.",
        ),
        GeneratedArtifact(
            "bundle_manifest_json",
            paths.bundle_manifest_json,
            "Artifact bundle manifest.",
        ),
    )
    bundle = ArtifactBundle(
        dataset_id=BIGP3BCI_DATASET_ID,
        protocol=ProtocolType.SELECTION,
        evidence_level=evidence_level,
        source_path=source,
        output_dir=output,
        generated_files=generated_files,
        metadata={
            "data_file_count": len(inventory.files),
            "event_count": len(events),
            "target_count": len(targets),
            "prediction_count": len(predictions),
            "target_type": "p300_selection_proxy",
            "generated_at": generated_at,
            "generated_by": "intentfidelity",
            "intentfidelity_version": __version__,
            "command": command,
            "source_files": source_files,
            "event_extraction_contract": bigp3bci_event_extraction_contract(),
        },
    )
    save_artifact_bundle(bundle, paths.bundle_manifest_json)
    return bundle


def validate_bigp3bci_artifact_bundle(
    bundle_dir: str | Path,
) -> ArtifactValidationReport:
    report = validate_artifact_bundle(
        bundle_dir,
        required_kinds=BIGP3BCI_BUNDLE_REQUIRED_KINDS,
    )
    if not report.is_valid:
        return report

    issues = list(report.issues)
    manifest_path = Path(bundle_dir) / "bundle_manifest.json"
    bundle = load_artifact_bundle(manifest_path)
    artifacts = {artifact.kind: artifact.path for artifact in bundle.generated_files}

    events = read_p300_events_jsonl(artifacts["events_jsonl"])
    targets = read_weak_targets_jsonl(artifacts["targets_jsonl"])
    predictions = read_predictions_jsonl(artifacts["predictions_jsonl"])
    result = load_eval_result(artifacts["result_json"])
    eval_card = artifacts["eval_card_markdown"].read_text(encoding="utf-8")
    selection_report = artifacts["selection_report_markdown"].read_text(
        encoding="utf-8"
    )
    comparison = artifacts["comparison_markdown"].read_text(encoding="utf-8")

    _append_count_issue(
        issues,
        "event_count_mismatch",
        bundle.metadata.get("event_count"),
        len(events),
        manifest_path,
    )
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
        "result_event_count_mismatch",
        result.metadata.get("event_count"),
        len(events),
        artifacts["result_json"],
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
    if (
        bundle.dataset_id != BIGP3BCI_DATASET_ID
        or result.dataset_id != BIGP3BCI_DATASET_ID
    ):
        issues.append(
            _error(
                "dataset_id_mismatch",
                "bundle and result must use the bigp3bci dataset id.",
                manifest_path,
            )
        )
    if (
        bundle.protocol != ProtocolType.SELECTION
        or result.protocol != ProtocolType.SELECTION
    ):
        issues.append(
            _error(
                "protocol_mismatch",
                "bigP3BCI bundles must use the selection protocol.",
                manifest_path,
            )
        )
    if result.metadata.get("evidence_level") != bundle.evidence_level.value:
        issues.append(
            _error(
                "result_evidence_level_mismatch",
                "result metadata evidence level must match the bundle manifest.",
                artifacts["result_json"],
            )
        )
    if not _bundle_has_source_file_hashes(bundle):
        issues.append(
            _error(
                "missing_source_file_hashes",
                "bundle manifest must include SHA-256 provenance for source EDF+ files.",
                manifest_path,
            )
        )
    event_ids = {event.sample_id for event in events}
    target_ids = {target.sample_id for target in targets}
    if event_ids != target_ids:
        issues.append(
            _error(
                "event_target_id_mismatch",
                "event and target sample_id sets must match exactly.",
                artifacts["targets_jsonl"],
            )
        )
    for method_id, method_predictions in _predictions_by_method(predictions).items():
        prediction_ids = {prediction.sample_id for prediction in method_predictions}
        if prediction_ids != target_ids:
            issues.append(
                _error(
                    "prediction_id_mismatch",
                    f"prediction sample_id set is incomplete for method {method_id}.",
                    artifacts["predictions_jsonl"],
                )
            )
    if bundle.evidence_level.value not in eval_card:
        issues.append(
            _error(
                "eval_card_missing_evidence_scope",
                "eval card must include the bundle evidence level.",
                artifacts["eval_card_markdown"],
            )
        )
    selection_scope = "Scores use prompted symbols and selection outputs as intent proxies"
    if selection_scope not in selection_report:
        issues.append(
            _error(
                "selection_report_missing_proxy_scope",
                "selection report must state its proxy-scoring scope.",
                artifacts["selection_report_markdown"],
            )
        )
    if "not directly observed true intent" not in comparison:
        issues.append(
            _error(
                "comparison_missing_true_intent_limitation",
                "comparison report must state that rankings do not observe true intent.",
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
        self.events_jsonl = output_dir / "events.jsonl"
        self.targets_jsonl = output_dir / "targets.jsonl"
        self.predictions_jsonl = output_dir / "predictions.jsonl"
        self.result_json = output_dir / "result.json"
        self.eval_card_md = output_dir / "eval_card.md"
        self.selection_report_md = output_dir / "selection_report.md"
        self.comparison_md = output_dir / "comparison.md"
        self.bundle_manifest_json = output_dir / "bundle_manifest.json"


def _events_from_inventory(
    inventory: BigP3BCIInventory,
) -> tuple[P300SelectionEvent, ...]:
    events: list[P300SelectionEvent] = []
    for data_file in inventory.files:
        events.extend(load_bigp3bci_selection_events(data_file))
    return tuple(events)


def _raise_for_invalid_inventory(inventory: BigP3BCIInventory) -> None:
    errors = [
        f"{issue.code}: {issue.message}"
        for issue in inventory.issues
        if issue.severity == ValidationSeverity.ERROR
    ]
    if errors:
        raise ValueError(f"invalid bigP3BCI inventory: {'; '.join(errors)}")


def _predictions_by_method(
    predictions: tuple[Prediction, ...],
) -> dict[str, tuple[Prediction, ...]]:
    grouped: dict[str, list[Prediction]] = {}
    for prediction in predictions:
        grouped.setdefault(prediction.method_id, []).append(prediction)
    return {method_id: tuple(values) for method_id, values in grouped.items()}


def _result_metadata(
    source: Path,
    inventory: BigP3BCIInventory,
    *,
    event_count: int,
    target_count: int,
    prediction_count: int,
    evidence_level: EvidenceLevel,
    generated_at: str,
    source_files: tuple[dict[str, object], ...],
    command: str | None,
) -> dict[str, object]:
    return {
        "source_path": str(source),
        "data_file_count": len(inventory.files),
        "event_count": event_count,
        "target_count": target_count,
        "prediction_count": prediction_count,
        "target_type": "p300_selection_proxy",
        "weak_target_source": "bigP3BCI CurrentTarget EDF+ records",
        "evidence_level": evidence_level.value,
        "generated_at": generated_at,
        "generated_by": "intentfidelity",
        "intentfidelity_version": __version__,
        "command": command,
        "source_files": source_files,
        "baseline_scope": _evidence_scope_text(evidence_level),
        "proxy_limitations": (
            "Weak targets are prompted-symbol proxies from EDF+ records; this "
            "result does not claim direct access to true intent."
        ),
    }


def _evidence_scope_text(evidence_level: EvidenceLevel) -> str:
    if evidence_level == EvidenceLevel.FIXTURE_EVIDENCE:
        return (
            "fixture_evidence: synthetic EDF+ fixtures validate bigP3BCI bundle "
            "plumbing; this is not downloaded bigP3BCI dataset evidence."
        )
    if evidence_level == EvidenceLevel.DOWNLOADED_DATASET_EVIDENCE:
        return (
            "downloaded_dataset_evidence: local run against user-provided "
            "bigP3BCI EDF+ files; targets remain prompted-symbol proxies."
        )
    return f"{evidence_level.value}: scope is limited to declared proxy artifacts."


def _render_selection_report(result, evidence_scope: str) -> str:
    base = render_selection_markdown(result).rstrip()
    return (
        f"{base}\n\n"
        "## Evidence Scope\n"
        f"- {evidence_scope}\n"
        "- The observed selection feedback baseline is a sanity check from "
        "recorded feedback fields, not a neural decoder.\n"
    )


def _render_comparison_report(result, evidence_scope: str) -> str:
    base = render_comparison_markdown(compare_eval_results(result)).rstrip()
    return (
        f"{base}\n\n"
        "## Evidence Scope\n"
        f"- {evidence_scope}\n"
        "- Comparison rankings are computed against prompted-symbol weak target "
        "distributions, not directly observed true intent.\n"
    )


def _source_file_provenance(
    inventory: BigP3BCIInventory,
) -> tuple[dict[str, object], ...]:
    return tuple(
        _file_provenance(data_file)
        for data_file in sorted(inventory.files, key=lambda item: str(item.path))
    )


def _file_provenance(data_file: BigP3BCIDataFile) -> dict[str, object]:
    return {
        "path": str(data_file.path),
        "study_id": data_file.study_id,
        "subject_id": data_file.subject_id,
        "session_id": data_file.session_id,
        "phase": data_file.phase.value,
        "size_bytes": data_file.size_bytes,
        "sha256": _sha256_file(data_file.path),
    }


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


def _bundle_has_source_file_hashes(bundle: ArtifactBundle) -> bool:
    source_files = bundle.metadata.get("source_files")
    if not isinstance(source_files, (list, tuple)) or not source_files:
        return False
    for item in source_files:
        if not isinstance(item, dict):
            return False
        digest = item.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            return False
    return True


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
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
