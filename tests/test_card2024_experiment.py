import importlib.util
import json
from pathlib import Path


def test_card2024_experiment_outputs_communication_result(capsys) -> None:
    module = _load_experiment_module(
        Path("experiments/02_card2024_speech_fidelity/run.py")
    )

    assert module.main() == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset_id"] == "card2024"
    assert payload["protocol"] == "communication"
    assert payload["metadata"]["evidence_stage"] == "synthetic_protocol_scaffold"


def _load_experiment_module(path: Path):
    spec = importlib.util.spec_from_file_location("card2024_experiment", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
