import importlib.util
import json
from pathlib import Path


def test_willett2023_experiment_outputs_language_prior_attribution(capsys) -> None:
    module = _load_experiment_module(
        Path("experiments/03_willett2023_lm_attribution/run.py")
    )

    assert module.main() == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["lm_light_method_id"] == "lm_light"
    assert payload["lm_heavy_method_id"] == "lm_heavy"
    assert payload["interpretation"] == "lm_heavy_worse"


def _load_experiment_module(path: Path):
    spec = importlib.util.spec_from_file_location("willett2023_experiment", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
