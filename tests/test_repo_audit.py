from pathlib import Path

from intentfidelity.audit import audit_repository


def test_repo_audit_reports_current_evidence_posture() -> None:
    report = audit_repository(Path.cwd())

    assert report.passed is True
    checks = {check.name: check for check in report.checks}
    assert checks["required_docs"].passed is True
    assert checks["ci_workflow"].passed is True
    assert checks["resource_manifests"].details["count"] == 6
    assert checks["resource_manifests"].details["stage_mismatches"] == {}
    assert checks["evidence_boundaries"].passed is True
    assert checks["db_state_files"].details["matches"] == []


def test_repo_audit_serializes_checks() -> None:
    payload = audit_repository(Path.cwd()).to_dict()

    assert payload["passed"] is True
    assert {check["name"] for check in payload["checks"]} == {
        "required_docs",
        "ci_workflow",
        "resource_manifests",
        "evidence_boundaries",
        "db_state_files",
    }
