from intentfidelity.baselines import get_baseline, list_baselines
from intentfidelity.baselines.registry import list_implemented_baselines


def test_baseline_registry_contains_first_pass_methods() -> None:
    method_ids = [baseline.method_id for baseline in list_baselines()]

    assert method_ids == [
        "identity",
        "session_centering",
        "procrustes",
        "cca",
        "whitening_coloring",
        "supervised_fine_tune",
        "lm_heavy",
        "lm_light",
    ]


def test_get_baseline_returns_method_metadata() -> None:
    baseline = get_baseline("lm_heavy")

    assert baseline.category == "language_prior"
    assert baseline.status == "placeholder"


def test_implemented_baselines_are_marked_active() -> None:
    assert get_baseline("identity").status == "implemented"
    assert get_baseline("session_centering").status == "implemented"
    assert get_baseline("whitening_coloring").status == "implemented"


def test_baseline_specs_serialize_and_filter_by_status() -> None:
    assert get_baseline("identity").to_dict()["status"] == "implemented"
    assert [baseline.method_id for baseline in list_implemented_baselines()] == [
        "identity",
        "session_centering",
        "whitening_coloring",
    ]
