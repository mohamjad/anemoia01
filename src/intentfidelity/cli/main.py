from __future__ import annotations

import argparse
from pathlib import Path
import sys

from intentfidelity.figures import render_ranking_reversal
from intentfidelity.protocols import EvalResult, load_eval_result
from intentfidelity.reports import DatasetCard, EvalCard, render_json, render_markdown
from intentfidelity.resources import get_manifest, load_manifests


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

    eval_parser = subparsers.add_parser("eval")
    eval_subparsers = eval_parser.add_subparsers(dest="eval_command")
    eval_summary = eval_subparsers.add_parser("summarize")
    eval_summary.add_argument("result_json", type=Path)
    _add_handler(eval_summary, _eval_summarize)

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


def _report_eval_card(args: argparse.Namespace) -> None:
    card = EvalCard.from_result(_load_eval_result(args.result_json))
    _print_card(card, args.format)


def _figure_ranking_reversal(args: argparse.Namespace) -> None:
    print(render_ranking_reversal(_load_eval_result(args.result_json)), end="")


def _load_eval_result(path: Path) -> EvalResult:
    return load_eval_result(path)


def _print_card(card: object, output_format: str) -> None:
    if output_format == "json":
        print(render_json(card))
        return
    print(render_markdown(card), end="")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
