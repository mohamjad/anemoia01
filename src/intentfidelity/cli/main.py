from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from intentfidelity.baselines import (
    list_baselines,
    list_implemented_baselines,
    read_labeled_examples_csv,
    run_centroid_baseline,
)
from intentfidelity.figures import render_comparison_table, render_ranking_reversal
from intentfidelity.ingest import inventory_falcon_h2, list_hdf5_datasets
from intentfidelity.labels import (
    read_predictions_jsonl,
    read_text_predictions_jsonl,
    read_text_targets_jsonl,
    write_weak_targets_jsonl,
)
from intentfidelity.protocols import (
    EvalResult,
    communication_eval_result,
    compare_eval_results,
    falcon_h2_baseline_eval,
    language_prior_report,
    load_eval_result,
)
from intentfidelity.protocols import falcon_h2_targets_from_file
from intentfidelity.protocols import falcon_h2_prediction_eval
from intentfidelity.reports import DatasetCard, EvalCard, render_json, render_markdown
from intentfidelity.reports import (
    render_comparison_markdown,
    render_language_prior_markdown,
)
from intentfidelity.resources import fetch_dandi_assets, get_manifest, load_manifests


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        parser.print_help()
        return 1
    args.handler(args)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intentfidelity",
        description="Intent-fidelity evaluation infrastructure CLI.",
    )
    subparsers = parser.add_subparsers(dest="command")

    resources_parser = subparsers.add_parser("resources")
    resources_subparsers = resources_parser.add_subparsers(dest="resources_command")
    _add_handler(resources_subparsers.add_parser("list"), _resources_list)
    _add_handler(resources_subparsers.add_parser("validate"), _resources_validate)
    resources_card = resources_subparsers.add_parser("card")
    resources_card.add_argument("dataset_id")
    resources_card.add_argument("--format", choices=("markdown", "json"), default="markdown")
    _add_handler(resources_card, _resources_card)
    dandi_assets = resources_subparsers.add_parser("falcon-h2-assets")
    dandi_assets.add_argument("--json", action="store_true")
    _add_handler(dandi_assets, _resources_falcon_h2_assets)

    eval_parser = subparsers.add_parser("eval")
    eval_subparsers = eval_parser.add_subparsers(dest="eval_command")
    eval_summary = eval_subparsers.add_parser("summarize")
    eval_summary.add_argument("result_json", type=Path)
    _add_handler(eval_summary, _eval_summarize)
    eval_compare = eval_subparsers.add_parser("compare")
    eval_compare.add_argument("before_json", type=Path)
    eval_compare.add_argument("after_json", type=Path, nargs="?")
    eval_compare.add_argument("--format", choices=("json", "markdown"), default="json")
    _add_handler(eval_compare, _eval_compare)
    falcon_h2_eval = eval_subparsers.add_parser("falcon-h2-baselines")
    falcon_h2_eval.add_argument("nwb_file", type=Path)
    falcon_h2_eval.add_argument("--output", type=Path)
    _add_handler(falcon_h2_eval, _eval_falcon_h2_baselines)
    falcon_h2_targets = eval_subparsers.add_parser("falcon-h2-targets")
    falcon_h2_targets.add_argument("nwb_file", type=Path)
    falcon_h2_targets.add_argument("output_jsonl", type=Path)
    _add_handler(falcon_h2_targets, _eval_falcon_h2_targets)
    falcon_h2_predictions = eval_subparsers.add_parser("falcon-h2-predictions")
    falcon_h2_predictions.add_argument("nwb_file", type=Path)
    falcon_h2_predictions.add_argument("predictions_jsonl", type=Path)
    _add_handler(falcon_h2_predictions, _eval_falcon_h2_predictions)
    falcon_h2_feature_baseline = eval_subparsers.add_parser("falcon-h2-feature-baseline")
    falcon_h2_feature_baseline.add_argument("train_nwb", type=Path)
    falcon_h2_feature_baseline.add_argument("test_nwb", type=Path)
    _add_handler(falcon_h2_feature_baseline, _eval_falcon_h2_feature_baseline)
    synthetic_eval = eval_subparsers.add_parser("synthetic-baselines")
    _add_handler(synthetic_eval, _eval_synthetic_baselines)
    communication_eval = eval_subparsers.add_parser("communication")
    communication_eval.add_argument("targets_jsonl", type=Path)
    communication_eval.add_argument("predictions_jsonl", type=Path)
    communication_eval.add_argument("--dataset-id", required=True)
    communication_eval.add_argument(
        "--metric",
        choices=("character_error_rate", "word_error_rate"),
        default="character_error_rate",
    )
    _add_handler(communication_eval, _eval_communication)
    language_prior_eval = eval_subparsers.add_parser("language-prior")
    language_prior_eval.add_argument("result_json", type=Path)
    language_prior_eval.add_argument("--lm-light-method-id", default="lm_light")
    language_prior_eval.add_argument("--lm-heavy-method-id", default="lm_heavy")
    language_prior_eval.add_argument(
        "--format", choices=("json", "markdown"), default="json"
    )
    _add_handler(language_prior_eval, _eval_language_prior)

    ingest_parser = subparsers.add_parser("ingest")
    ingest_subparsers = ingest_parser.add_subparsers(dest="ingest_command")
    falcon_h2_inventory = ingest_subparsers.add_parser("falcon-h2-inventory")
    falcon_h2_inventory.add_argument("data_root", type=Path)
    falcon_h2_inventory.add_argument("--json", action="store_true")
    _add_handler(falcon_h2_inventory, _ingest_falcon_h2_inventory)
    nwb_summary = ingest_subparsers.add_parser("nwb-summary")
    nwb_summary.add_argument("nwb_file", type=Path)
    _add_handler(nwb_summary, _ingest_nwb_summary)

    report_parser = subparsers.add_parser("report")
    report_subparsers = report_parser.add_subparsers(dest="report_command")
    dataset_card = report_subparsers.add_parser("dataset-card")
    dataset_card.add_argument("dataset_id")
    dataset_card.add_argument("--format", choices=("markdown", "json"), default="markdown")
    _add_handler(dataset_card, _report_dataset_card)
    eval_card = report_subparsers.add_parser("eval-card")
    eval_card.add_argument("result_json", type=Path)
    eval_card.add_argument("--format", choices=("markdown", "json"), default="markdown")
    _add_handler(eval_card, _report_eval_card)

    figure_parser = subparsers.add_parser("figure")
    figure_subparsers = figure_parser.add_subparsers(dest="figure_command")
    ranking = figure_subparsers.add_parser("ranking-reversal")
    ranking.add_argument("result_json", type=Path)
    _add_handler(ranking, _figure_ranking_reversal)
    comparison_table = figure_subparsers.add_parser("comparison-table")
    comparison_table.add_argument("result_json", type=Path)
    _add_handler(comparison_table, _figure_comparison_table)

    baselines_parser = subparsers.add_parser("baselines")
    baselines_subparsers = baselines_parser.add_subparsers(dest="baselines_command")
    baselines_list = baselines_subparsers.add_parser("list")
    baselines_list.add_argument("--implemented", action="store_true")
    _add_handler(baselines_list, _baselines_list)
    centroid = baselines_subparsers.add_parser("centroid")
    centroid.add_argument("train_csv", type=Path)
    centroid.add_argument("test_csv", type=Path)
    _add_handler(centroid, _baselines_centroid)

    return parser


def _add_handler(
    parser: argparse.ArgumentParser, handler: object
) -> argparse.ArgumentParser:
    parser.set_defaults(handler=handler)
    return parser


def _resources_list(_: argparse.Namespace) -> None:
    for manifest in load_manifests():
        print(f"{manifest.dataset_id}\t{manifest.status}\t{manifest.title}")


def _resources_validate(_: argparse.Namespace) -> None:
    manifests = load_manifests()
    print(f"Validated {len(manifests)} resource manifests.")


def _resources_card(args: argparse.Namespace) -> None:
    card = DatasetCard.from_manifest(get_manifest(args.dataset_id))
    _print_card(card, args.format)


def _resources_falcon_h2_assets(args: argparse.Namespace) -> None:
    assets = fetch_dandi_assets()
    if args.json:
        print(json.dumps([asset.__dict__ for asset in assets], indent=2, sort_keys=True))
        return
    for asset in assets:
        print(f"{asset.path}\t{asset.size}")


def _report_dataset_card(args: argparse.Namespace) -> None:
    _resources_card(args)


def _eval_summarize(args: argparse.Namespace) -> None:
    result = _load_eval_result(args.result_json)
    print(f"Dataset: {result.dataset_id}")
    print(f"Protocol: {result.protocol.value}")
    print(f"Primary metric: {result.primary_metric}")
    print(f"Methods: {len(result.method_scores)}")
    if result.ranking_disagreement is not None:
        print(f"Ranking disagreement: {result.ranking_disagreement.has_disagreement}")


def _eval_compare(args: argparse.Namespace) -> None:
    before = load_eval_result(args.before_json)
    after = load_eval_result(args.after_json) if args.after_json else None
    report = compare_eval_results(before, after)
    if args.format == "markdown":
        print(render_comparison_markdown(report), end="")
        return
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))


def _eval_falcon_h2_baselines(args: argparse.Namespace) -> None:
    result = falcon_h2_baseline_eval(args.nwb_file)
    rendered = json.dumps(result.to_dict(), indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
        return
    print(rendered)


def _eval_falcon_h2_targets(args: argparse.Namespace) -> None:
    targets = falcon_h2_targets_from_file(args.nwb_file)
    write_weak_targets_jsonl(targets, args.output_jsonl)
    print(f"Wrote {len(targets)} weak targets to {args.output_jsonl}")


def _eval_falcon_h2_predictions(args: argparse.Namespace) -> None:
    grouped = _predictions_by_method(read_predictions_jsonl(args.predictions_jsonl))
    result = falcon_h2_prediction_eval(args.nwb_file, grouped)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))


def _eval_falcon_h2_feature_baseline(args: argparse.Namespace) -> None:
    from intentfidelity.protocols import falcon_h2_feature_baseline_eval

    result = falcon_h2_feature_baseline_eval(args.train_nwb, args.test_nwb)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))


def _eval_synthetic_baselines(_: argparse.Namespace) -> None:
    from intentfidelity.protocols import synthetic_baseline_eval

    print(json.dumps(synthetic_baseline_eval().to_dict(), indent=2, sort_keys=True))


def _eval_communication(args: argparse.Namespace) -> None:
    result = communication_eval_result(
        read_text_targets_jsonl(args.targets_jsonl),
        read_text_predictions_jsonl(args.predictions_jsonl),
        dataset_id=args.dataset_id,
        metric=args.metric,
    )
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))


def _eval_language_prior(args: argparse.Namespace) -> None:
    attribution = language_prior_report(
        _load_eval_result(args.result_json),
        lm_light_method_id=args.lm_light_method_id,
        lm_heavy_method_id=args.lm_heavy_method_id,
    )
    if args.format == "markdown":
        print(render_language_prior_markdown(attribution), end="")
        return
    print(json.dumps(attribution.to_dict(), indent=2, sort_keys=True))


def _ingest_falcon_h2_inventory(args: argparse.Namespace) -> None:
    inventory = inventory_falcon_h2(args.data_root)
    if args.json:
        print(json.dumps(inventory.to_dict(), indent=2, sort_keys=True))
        return

    print(f"Dataset: {inventory.dataset_id}")
    print(f"Root: {inventory.root}")
    print(f"Valid: {inventory.is_valid}")
    print(f"Files: {len(inventory.files)}")
    for issue in inventory.issues:
        location = f" ({issue.path})" if issue.path else ""
        print(f"{issue.severity.value}: {issue.code}: {issue.message}{location}")


def _ingest_nwb_summary(args: argparse.Namespace) -> None:
    for dataset in list_hdf5_datasets(args.nwb_file):
        print(f"{dataset.path}\t{dataset.shape}\t{dataset.dtype}")


def _report_eval_card(args: argparse.Namespace) -> None:
    card = EvalCard.from_result(_load_eval_result(args.result_json))
    _print_card(card, args.format)


def _figure_ranking_reversal(args: argparse.Namespace) -> None:
    print(render_ranking_reversal(_load_eval_result(args.result_json)), end="")


def _figure_comparison_table(args: argparse.Namespace) -> None:
    print(render_comparison_table(compare_eval_results(_load_eval_result(args.result_json))), end="")


def _baselines_centroid(args: argparse.Namespace) -> None:
    run = run_centroid_baseline(
        read_labeled_examples_csv(args.train_csv),
        read_labeled_examples_csv(args.test_csv),
    )
    print(
        json.dumps(
            {
                "method_id": run.method_id,
                "train_count": run.train_count,
                "test_count": run.test_count,
                "predictions": [prediction.to_dict() for prediction in run.predictions],
            },
            indent=2,
            sort_keys=True,
        )
    )


def _baselines_list(args: argparse.Namespace) -> None:
    baselines = list_implemented_baselines() if args.implemented else list_baselines()
    print(json.dumps([baseline.to_dict() for baseline in baselines], indent=2, sort_keys=True))


def _load_eval_result(path: Path) -> EvalResult:
    return load_eval_result(path)


def _print_card(card: object, output_format: str) -> None:
    if output_format == "json":
        print(render_json(card))
        return
    print(render_markdown(card), end="")


def _predictions_by_method(predictions) -> dict[str, tuple]:
    grouped: dict[str, list] = {}
    for prediction in predictions:
        grouped.setdefault(prediction.method_id, []).append(prediction)
    return {method_id: tuple(values) for method_id, values in grouped.items()}


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
