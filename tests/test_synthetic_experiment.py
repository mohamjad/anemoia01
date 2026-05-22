import importlib.util
import json
from pathlib import Path


def test_synthetic_experiment_outputs_eval_result(capsys) -> None:
    module = _load_experiment_module(Path("experiments/00_synthetic_sanity_check/run.py"))

    module.main()

    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset_id"] == "synthetic_shift"


def _load_experiment_module(path: Path):
    spec = importlib.util.spec_from_file_location("synthetic_experiment", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

