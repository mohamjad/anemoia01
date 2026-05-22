import importlib.util
import json
from pathlib import Path


def test_ajile12_experiment_outputs_naturalistic_result(capsys) -> None:
    module = _load_experiment_module(
        Path("experiments/05_ajile12_naturalistic_weak_labels/run.py")
    )

    assert module.main() == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset_id"] == "ajile12"
    assert payload["protocol"] == "naturalistic_weak_label"
    assert payload["metadata"]["evidence_stage"] == "synthetic_protocol_scaffold"
    assert payload["metadata"]["proxy_summary"]["session_count"] == 2


def _load_experiment_module(path: Path):
    spec = importlib.util.spec_from_file_location("ajile12_experiment", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
