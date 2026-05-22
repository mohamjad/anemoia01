import importlib.util
import json
from pathlib import Path


def test_kunz2025_experiment_outputs_authorization_result(capsys) -> None:
    module = _load_experiment_module(
        Path("experiments/04_kunz2025_authorized_intent/run.py")
    )

    assert module.main() == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset_id"] == "kunz2025"
    assert payload["protocol"] == "authorization"
    assert payload["metadata"]["evidence_stage"] == "synthetic_protocol_scaffold"


def _load_experiment_module(path: Path):
    spec = importlib.util.spec_from_file_location("kunz2025_experiment", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
