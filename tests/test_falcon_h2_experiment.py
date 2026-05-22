import importlib.util
import json
from pathlib import Path


def test_falcon_h2_experiment_reports_inventory(tmp_path, capsys) -> None:
    h2_root = tmp_path / "h2"
    for split in ("held_in_calib", "held_out_calib", "minival"):
        split_dir = h2_root / split
        split_dir.mkdir(parents=True)
        (split_dir / f"{split}.nwb").write_bytes(b"nwb")

    module = _load_experiment_module(
        Path("experiments/01_falcon_h2_ranking_disagreement/run.py")
    )

    assert module.main([str(tmp_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset_id"] == "falcon_h2"
    assert payload["file_count"] == 3


def _load_experiment_module(path: Path):
    spec = importlib.util.spec_from_file_location("falcon_h2_experiment", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
