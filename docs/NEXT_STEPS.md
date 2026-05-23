# Next Steps

## Recommended Path

Use the completed full-coverage FALCON H2 downloaded-data run as the local
evidence handoff, then expand to richer method coverage or a real non-FALCON
ingestion path.

Why FALCON H2:

- it already has the strongest ingestion path
- tests cover NWB/HDF5 fixture parsing
- character weak targets and prediction scoring already exist
- method comparison and reporting are already wired

## Current Completed Flow

The current implementation produces a reproducible local evaluation bundle from
FALCON H2 files:

```text
data root
-> inventory
-> weak targets
-> baseline predictions
-> eval result
-> eval card
-> comparison report
```

The repo also has a bigP3BCI raw EDF+ inventory contract. That contract stops
at file inventory; it does not parse EDF+ annotations or produce selection
targets.

## Closeout Checks

Run these before treating a pass as ready to hand off:

1. Run the repository posture audit:

   ```text
   intentfidelity audit repo --json
   ```

2. Run the fixture-backed bundle command when checking the local FALCON H2
   contract:

   ```text
   intentfidelity eval falcon-h2-bundle <fixture.nwb> outputs/falcon-h2-fixture
   ```

3. For downloaded FALCON H2 files, run:

   ```text
   intentfidelity eval falcon-h2-bundle data outputs/falcon-h2-bundle --evidence-level downloaded_dataset_evidence
   ```

4. Inspect `eval_card.md`, `comparison.md`, and `bundle_manifest.json` before
   treating the output as a reported result.

5. Validate the completed bundle:

   ```text
   intentfidelity eval falcon-h2-validate-bundle outputs/falcon-h2-bundle
   ```

6. Keep fixture results scoped as fixture evidence. Do not describe them as
   downloaded dataset evidence.

## Acceptance Criteria

- `pytest -q` passes.
- The artifact command writes every expected file.
- The result loads through `load_eval_result`.
- The eval card states the evidence scope.
- No report implies direct access to true intent.
- Docs explain how to reproduce the run.
- A downloaded-data bundle should record the local data path and exact command
  used to generate artifacts.
- `intentfidelity eval falcon-h2-validate-bundle` passes for the generated
  bundle.

## Highest-Value Remaining Work

The repo should not expand the thesis language until one of these concrete
evidence upgrades exists:

1. Richer FALCON H2 method families beyond centroid baselines, recorded through
   the same validated artifact bundle and reported whether ranking disagreement
   appears or not.
2. bigP3BCI EDF+ annotation parsing into typed P300 selection events, followed
   by weak target construction and a validated real-data artifact path.
3. CI and coverage thresholds so the audit/test gates run outside local
   discipline.
4. Real Card/Willett speech-path ingestion, Kunz authorization extraction, or
   AJILE12 naturalistic extraction only after a raw contract is written and
   fixture-backed.
