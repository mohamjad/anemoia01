# CLI

Initial commands:

```text
intentfidelity resources list
intentfidelity resources validate
intentfidelity resources card falcon_h2
intentfidelity resources falcon-h2-assets --json
intentfidelity ingest falcon-h2-inventory data --json
intentfidelity ingest nwb-summary data/h2/sub-T5-held-out-calib/example.nwb
intentfidelity baselines list --implemented
intentfidelity baselines centroid train.csv test.csv
intentfidelity eval synthetic-baselines
intentfidelity eval falcon-h2-targets data/h2/sub-T5-held-out-calib/example.nwb outputs/targets.jsonl
intentfidelity eval falcon-h2-baselines data/h2/sub-T5-held-out-calib/example.nwb
intentfidelity eval falcon-h2-feature-baseline train.nwb test.nwb
intentfidelity eval falcon-h2-predictions data/h2/sub-T5-held-out-calib/example.nwb outputs/predictions.jsonl
intentfidelity eval communication text-targets.jsonl text-predictions.jsonl --dataset-id card2024
intentfidelity eval language-prior outputs/results.json --format markdown
intentfidelity eval authorization authorization-events.jsonl authorization-predictions.jsonl --dataset-id kunz2025
intentfidelity eval naturalistic naturalistic-events.jsonl naturalistic-predictions.jsonl --dataset-id ajile12 --format markdown
intentfidelity eval selection p300-events.jsonl p300-predictions.jsonl --dataset-id bigp3bci --format markdown
intentfidelity eval summarize outputs/results.json
intentfidelity eval compare outputs/results.json --format markdown
intentfidelity report dataset-card falcon_h2
intentfidelity report eval-card outputs/results.json
intentfidelity figure ranking-reversal outputs/results.json
intentfidelity figure comparison-table outputs/results.json
```

Commands that read `outputs/results.json` expect the `EvalResult` JSON contract
from `intentfidelity.protocols`.
