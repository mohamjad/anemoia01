from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from intentfidelity.ingest import inventory_falcon_h2
from intentfidelity.protocols import falcon_h2_baseline_eval


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the local FALCON H2 layout for pass-2 ingestion work."
    )
    parser.add_argument("data_root", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--eval-first-file", action="store_true")
    args = parser.parse_args(argv)

    inventory = inventory_falcon_h2(args.data_root)
    if args.eval_first_file:
        if not inventory.files:
            print("No FALCON H2 files available for evaluation.")
            return 2
        result = falcon_h2_baseline_eval(inventory.files[0].path)
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.json:
        print(json.dumps(inventory.to_dict(), indent=2, sort_keys=True))
    else:
        print(f"FALCON H2 inventory valid: {inventory.is_valid}")
        print(f"Files discovered: {len(inventory.files)}")
        for issue in inventory.issues:
            print(f"{issue.severity.value}: {issue.code}: {issue.message}")
    return 0 if inventory.is_valid else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
