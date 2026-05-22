import json
from pathlib import Path

from intentfidelity.cli.main import main
from intentfidelity.metrics import MethodScore, ranking_disagreement
from intentfidelity.protocols import EvalResult, ProtocolType


def test_resources_list_command(capsys) -> None:
    assert main(["resources", "list"]) == 0

    output = capsys.readouterr().out

    assert "falcon_h2" in output
    assert "FALCON H2" in output


def test_resources_validate_command(capsys) -> None:
    assert main(["resources", "validate"]) == 0

    assert "Validated 6 resource manifests." in capsys.readouterr().out


def test_report_dataset_card_command(capsys) -> None:
    assert main(["report", "dataset-card", "falcon_h2", "--format", "json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset_id"] == "falcon_h2"


def test_resources_card_command(capsys) -> None:
    assert main(["resources", "card", "falcon_h2"]) == 0

    output = capsys.readouterr().out
    assert "# FALCON H2" in output
    assert "Weak Proxy Sources" in output


def test_eval_summary_and_figure_commands(tmp_path: Path, capsys) -> None:
    scores = (
        MethodScore("accuracy_first", 0.1, 0.4),
        MethodScore("proxy_faithful", 0.2, 0.1),
    )
    result = EvalResult(
        dataset_id="falcon_h2",
        protocol=ProtocolType.HELD_OUT_SESSION,
        method_scores=scores,
        primary_metric="held_out_session_intent_fidelity_loss",
        ranking_disagreement=ranking_disagreement(scores),
    )
    path = tmp_path / "result.json"
    path.write_text(json.dumps(result.to_dict()), encoding="utf-8")

    assert main(["eval", "summarize", str(path)]) == 0
    assert "Ranking disagreement: True" in capsys.readouterr().out

    assert main(["figure", "ranking-reversal", str(path)]) == 0
    assert "accuracy_first -> proxy_faithful" in capsys.readouterr().out


def test_falcon_h2_inventory_command_reports_layout(tmp_path: Path, capsys) -> None:
    h2_root = tmp_path / "h2"
    for split in ("held_in_calib", "held_out_calib", "minival"):
        split_dir = h2_root / split
        split_dir.mkdir(parents=True)
        (split_dir / f"{split}.nwb").write_bytes(b"nwb")

    assert main(["ingest", "falcon-h2-inventory", str(tmp_path), "--json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset_id"] == "falcon_h2"
    assert payload["is_valid"] is True
    assert payload["file_count"] == 3
