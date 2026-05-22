import importlib.util
import json
from pathlib import Path


def test_bigp3bci_experiment_outputs_selection_result(capsys) -> None:
    module = _load_experiment_module(
        Path("experiments/06_bigp3bci_selection_weak_targets/run.py")
    )

    assert module.main() == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset_id"] == "bigp3bci"
    assert payload["protocol"] == "selection"
    assert payload["metadata"]["evidence_stage"] == "synthetic_protocol_scaffold"
    assert payload["metadata"]["proxy_summary"]["event_count"] == 2


def _load_experiment_module(path: Path):
    spec = importlib.util.spec_from_file_location("bigp3bci_experiment", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
