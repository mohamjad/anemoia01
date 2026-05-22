import json
from pathlib import Path

import h5py

from intentfidelity.cli.main import main
from intentfidelity.baselines import LabeledExample, write_labeled_examples_csv
from intentfidelity.labels import (
    AuthorizationEvent,
    AuthorizationState,
    Prediction,
    TextPrediction,
    TextTarget,
    write_authorization_events_jsonl,
    write_predictions_jsonl,
    write_text_predictions_jsonl,
    write_text_targets_jsonl,
)
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

    assert main(["figure", "comparison-table", str(path)]) == 0
    assert "reversal_rate" in capsys.readouterr().out

    assert main(["eval", "compare", str(path), "--format", "markdown"]) == 0
    assert "Method Comparison Report" in capsys.readouterr().out


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


def test_falcon_h2_baseline_eval_command_outputs_json(tmp_path: Path, capsys) -> None:
    path = _write_cli_h2_file(tmp_path)

    assert main(["eval", "falcon-h2-baselines", str(path)]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset_id"] == "falcon_h2"
    assert len(payload["method_scores"]) == 2


def test_falcon_h2_feature_baseline_command_outputs_json(tmp_path: Path, capsys) -> None:
    train = _write_cli_h2_file(tmp_path, "sub-T5-held-in-calib_ses-20230417.nwb")
    test = _write_cli_h2_file(tmp_path, "sub-T5-held-out-calib_ses-20230418.nwb")

    assert main(["eval", "falcon-h2-feature-baseline", str(train), str(test)]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert [score["method_id"] for score in payload["method_scores"]] == [
        "identity_centroid",
        "session_centered_centroid",
        "whitened_centroid",
    ]


def test_falcon_h2_targets_command_writes_jsonl(tmp_path: Path, capsys) -> None:
    path = _write_cli_h2_file(tmp_path)
    output = tmp_path / "targets.jsonl"

    assert main(["eval", "falcon-h2-targets", str(path), str(output)]) == 0

    assert "Wrote 2 weak targets" in capsys.readouterr().out
    assert len(output.read_text(encoding="utf-8").splitlines()) == 2


def test_falcon_h2_predictions_command_scores_jsonl(tmp_path: Path, capsys) -> None:
    path = _write_cli_h2_file(tmp_path)
    predictions = (
        Prediction("falcon_h2:2023-04-17:trial-1:char-000", {"a": 1.0, "b": 0.0}, "decoder"),
        Prediction("falcon_h2:2023-04-17:trial-1:char-001", {"a": 0.0, "b": 1.0}, "decoder"),
    )
    prediction_path = tmp_path / "predictions.jsonl"
    write_predictions_jsonl(predictions, prediction_path)

    assert main(["eval", "falcon-h2-predictions", str(path), str(prediction_path)]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["method_scores"][0]["method_id"] == "decoder"


def test_synthetic_baselines_command_outputs_eval_result(capsys) -> None:
    assert main(["eval", "synthetic-baselines"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset_id"] == "synthetic_shift"


def test_communication_command_scores_text_jsonl(tmp_path: Path, capsys) -> None:
    targets_path = tmp_path / "targets.jsonl"
    predictions_path = tmp_path / "predictions.jsonl"
    write_text_targets_jsonl((TextTarget("s0", "open", "prompt"),), targets_path)
    write_text_predictions_jsonl(
        (TextPrediction("s0", "open", "decoder"),), predictions_path
    )

    assert (
        main(
            [
                "eval",
                "communication",
                str(targets_path),
                str(predictions_path),
                "--dataset-id",
                "card2024",
            ]
        )
        == 0
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["protocol"] == "communication"
    assert payload["method_scores"][0]["method_id"] == "decoder"


def test_language_prior_command_outputs_attribution(tmp_path: Path, capsys) -> None:
    result = EvalResult(
        dataset_id="willett2023",
        protocol=ProtocolType.COMMUNICATION,
        method_scores=(
            MethodScore("lm_light", 0.2, 0.2),
            MethodScore("lm_heavy", 0.1, 0.4),
        ),
        primary_metric="character_error_rate",
    )
    path = tmp_path / "result.json"
    path.write_text(json.dumps(result.to_dict()), encoding="utf-8")

    assert main(["eval", "language-prior", str(path), "--format", "markdown"]) == 0

    output = capsys.readouterr().out
    assert "Language Prior Attribution" in output
    assert "lm_heavy_worse" in output


def test_authorization_command_scores_event_jsonl(tmp_path: Path, capsys) -> None:
    events_path = tmp_path / "events.jsonl"
    predictions_path = tmp_path / "predictions.jsonl"
    write_authorization_events_jsonl(
        (AuthorizationEvent("s0", AuthorizationState.AUTHORIZED),), events_path
    )
    write_predictions_jsonl(
        (
            Prediction(
                "s0",
                {"authorized": 0.9, "not_authorized": 0.1},
                "decoder",
            ),
        ),
        predictions_path,
    )

    assert (
        main(
            [
                "eval",
                "authorization",
                str(events_path),
                str(predictions_path),
                "--dataset-id",
                "kunz2025",
            ]
        )
        == 0
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["protocol"] == "authorization"
    assert payload["method_scores"][0]["method_id"] == "decoder"


def test_nwb_summary_command_lists_hdf5_datasets(tmp_path: Path, capsys) -> None:
    path = tmp_path / "sample.nwb"
    with h5py.File(path, "w") as handle:
        handle.create_dataset("x/y", data=[1])

    assert main(["ingest", "nwb-summary", str(path)]) == 0

    assert "x/y" in capsys.readouterr().out


def test_baselines_centroid_command_outputs_predictions(tmp_path: Path, capsys) -> None:
    train = tmp_path / "train.csv"
    test = tmp_path / "test.csv"
    write_labeled_examples_csv(
        (
            LabeledExample("train-a", "a", [0.0], "s1"),
            LabeledExample("train-b", "b", [10.0], "s1"),
        ),
        train,
    )
    write_labeled_examples_csv((LabeledExample("test-a", "a", [1.0], "s2"),), test)

    assert main(["baselines", "centroid", str(train), str(test)]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["test_count"] == 1


def test_baselines_list_command_outputs_implemented_methods(capsys) -> None:
    assert main(["baselines", "list", "--implemented"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert [item["method_id"] for item in payload] == [
        "identity",
        "session_centering",
        "whitening_coloring",
    ]


def test_falcon_h2_assets_command_can_be_patched(monkeypatch, capsys) -> None:
    class Asset:
        asset_id = "abc"
        path = "sub-T5-held-out-calib/file.nwb"
        size = 123

    monkeypatch.setattr("intentfidelity.cli.main.fetch_dandi_assets", lambda: (Asset(),))

    assert main(["resources", "falcon-h2-assets"]) == 0

    assert "sub-T5-held-out-calib/file.nwb" in capsys.readouterr().out


def _write_cli_h2_file(
    tmp_path: Path,
    name: str = "sub-T5-held-out-calib_ses-20230417.nwb",
) -> Path:
    path = tmp_path / name
    with h5py.File(path, "w") as handle:
        trials = handle.create_group("intervals/trials")
        trials.create_dataset("cue", data=[b"ab"])
        trials.create_dataset("start_time", data=[0.0])
        trials.create_dataset("stop_time", data=[2.0])
        trials.create_dataset("id", data=[1])
        handle.create_dataset("acquisition/binned_spikes/data", data=[[0, 1], [1, 0]])
        handle.create_dataset("acquisition/binned_spikes/timestamps", data=[0.25, 1.25])
    return path
