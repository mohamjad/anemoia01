from intentfidelity.overview import build_repo_overview, render_repo_overview


def test_repo_overview_names_evidence_paths_and_boundaries() -> None:
    overview = build_repo_overview()

    assert overview.audit_passed is True
    assert "downloaded-data FALCON H2 evidence" in overview.current_status
    assert [path.name for path in overview.evidence_paths] == [
        "FALCON H2",
        "bigP3BCI",
        "Speech, authorization, and naturalistic paths",
    ]
    assert "not a submitted-decoder benchmark" in overview.evidence_paths[0].boundary
    assert "Fixture-backed extraction only" in overview.evidence_paths[1].boundary


def test_repo_overview_renders_navigation() -> None:
    rendered = render_repo_overview(build_repo_overview())

    assert "# Intent Fidelity Repo Overview" in rendered
    assert "docs/START_HERE.md" in rendered
    assert "Audit passed: True" in rendered
