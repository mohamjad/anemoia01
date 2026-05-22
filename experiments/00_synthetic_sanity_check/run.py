from __future__ import annotations

import json

from intentfidelity.protocols import synthetic_baseline_eval


def main() -> None:
    print(json.dumps(synthetic_baseline_eval().to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
