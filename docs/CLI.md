# CLI

Initial commands:

```text
intentfidelity resources list
intentfidelity resources validate
intentfidelity resources card falcon_h2
intentfidelity eval summarize outputs/results.json
intentfidelity report dataset-card falcon_h2
intentfidelity report eval-card outputs/results.json
intentfidelity figure ranking-reversal outputs/results.json
```

Commands that read `outputs/results.json` expect the `EvalResult` JSON contract
from `intentfidelity.protocols`.

