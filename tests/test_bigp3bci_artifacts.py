import json
from pathlib import Path

from intentfidelity.labels import read_p300_events_jsonl, read_predictions_jsonl
from intentfidelity.protocols import load_eval_result
from intentfidelity.protocols.artifacts import EvidenceLevel, load_artifact_bundle
from intentfidelity.protocols.bigp3bci_artifacts import (
    validate_bigp3bci_artifact_bundle,
    write_bigp3bci_artifact_bundle,
)

from bigp3bci_fixtures import write_bigp3bci_event_fixture


def test_bigp3bci_bundle_writes_complete_fixture_artifacts(tmp_path: Path) -> None:
    source_file = write_bigp3bci_event_fixture(tmp_path)
    output_dir = tmp_path / "bundle"

    bundle = write_bigp3bci_artifact_bundle(
        tmp_path,
        output_dir,
        evidence_level=EvidenceLevel.FIXTURE_EVIDENCE,
        command="intentfidelity eval bigp3bci-bundle fixture bundle",
    )

    assert {path.name for path in output_dir.iterdir()} == {
        "inventory.json",
        "events.jsonl",
        "targets.jsonl",
        "predictions.jsonl",
        "result.json",
        "diagnostics.json",
        "diagnostics.md",
        "eval_card.md",
        "selection_report.md",
        "comparison.md",
        "bundle_manifest.json",
    }
    assert {artifact.kind for artifact in bundle.generated_files} == {
        "inventory_json",
        "events_jsonl",
        "targets_jsonl",
        "predictions_jsonl",
        "result_json",
        "diagnostics_json",
        "diagnostics_markdown",
        "eval_card_markdown",
        "selection_report_markdown",
        "comparison_markdown",
        "bundle_manifest_json",
    }

    events = read_p300_events_jsonl(output_dir / "events.jsonl")
    predictions = read_predictions_jsonl(output_dir / "predictions.jsonl")
    result = load_eval_result(output_dir / "result.json")
    manifest = load_artifact_bundle(output_dir / "bundle_manifest.json")
    diagnostics = json.loads((output_dir / "diagnostics.json").read_text())

    assert len(events) == 2
    assert len(predictions) == 6
    assert result.dataset_id == "bigp3bci"
    assert result.metadata["evidence_level"] == "fixture_evidence"
    assert result.metadata["command"] == (
        "intentfidelity eval bigp3bci-bundle fixture bundle"
    )
    assert result.metadata["source_files"][0]["sha256"]
    assert diagnostics["sample_count"] == 2
    assert diagnostics["method_count"] == 3
    assert manifest.metadata["event_count"] == 2
    assert manifest.metadata["source_files"][0]["size_bytes"] == source_file.size_bytes

    eval_card = (output_dir / "eval_card.md").read_text(encoding="utf-8")
    selection_report = (output_dir / "selection_report.md").read_text(
        encoding="utf-8"
    )
    comparison = (output_dir / "comparison.md").read_text(encoding="utf-8")
    assert "fixture_evidence" in eval_card
    assert "Bootstrap Ranking Stability" in (
        output_dir / "diagnostics.md"
    ).read_text(encoding="utf-8")
    assert "not downloaded bigP3BCI dataset evidence" in selection_report
    assert "not directly observed true intent" in comparison


def test_validate_bigp3bci_bundle_accepts_complete_bundle(tmp_path: Path) -> None:
    write_bigp3bci_event_fixture(tmp_path)
    output_dir = tmp_path / "bundle"
    write_bigp3bci_artifact_bundle(tmp_path, output_dir)

    report = validate_bigp3bci_artifact_bundle(output_dir)

    assert report.is_valid is True
    assert report.issues == ()


def test_validate_bigp3bci_bundle_checks_counts(tmp_path: Path) -> None:
    write_bigp3bci_event_fixture(tmp_path)
    output_dir = tmp_path / "bundle"
    write_bigp3bci_artifact_bundle(tmp_path, output_dir)
    result_path = output_dir / "result.json"
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    payload["metadata"]["event_count"] = 999
    result_path.write_text(json.dumps(payload), encoding="utf-8")

    report = validate_bigp3bci_artifact_bundle(output_dir)

    assert report.is_valid is False
    assert "result_event_count_mismatch" in {issue.code for issue in report.issues}


def test_validate_bigp3bci_bundle_checks_prediction_coverage(tmp_path: Path) -> None:
    write_bigp3bci_event_fixture(tmp_path)
    output_dir = tmp_path / "bundle"
    write_bigp3bci_artifact_bundle(tmp_path, output_dir)
    predictions_path = output_dir / "predictions.jsonl"
    rows = predictions_path.read_text(encoding="utf-8").splitlines()
    predictions_path.write_text("\n".join(rows[:-1]) + "\n", encoding="utf-8")

    report = validate_bigp3bci_artifact_bundle(output_dir)

    assert report.is_valid is False
    assert "prediction_id_mismatch" in {issue.code for issue in report.issues}
