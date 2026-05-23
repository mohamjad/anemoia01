# Next Steps

## Recommended Path

Use the completed FALCON H2 downloaded-data runs as the local evidence handoff,
then expand to fuller method coverage, full split coverage, or a real
non-FALCON ingestion path.

Why FALCON H2:

- it already has the strongest ingestion path
- tests cover NWB/HDF5 fixture parsing
- character weak targets and prediction scoring already exist
- method comparison and reporting are already wired

## Pass Objective

The current bundle implementation produces a reproducible local evaluation
bundle from FALCON H2 files:

```text
data root
-> inventory
-> weak targets
-> baseline predictions
-> eval result
-> eval card
-> comparison report
```

## Concrete Work Items

1. Run the fixture-backed bundle command when checking the local contract:

   ```text
   intentfidelity eval falcon-h2-bundle <fixture.nwb> outputs/falcon-h2-fixture
   ```

2. For downloaded FALCON H2 files, run:

   ```text
   intentfidelity eval falcon-h2-bundle data outputs/falcon-h2-bundle --evidence-level downloaded_dataset_evidence
   ```

3. Inspect `eval_card.md`, `comparison.md`, and `bundle_manifest.json` before
   treating the output as a reported result.

4. Validate the completed bundle:

   ```text
   intentfidelity eval falcon-h2-validate-bundle outputs/falcon-h2-bundle
   ```

5. Keep fixture results scoped as fixture evidence. Do not describe them as
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

## Deferred Work

Only after the FALCON H2 bundle is stable:

- full downloaded FALCON H2 split coverage instead of the minimal one-file-per-split run
- richer FALCON H2 method families beyond centroid baselines
- real Card/Willett speech-path ingestion
- Kunz authorization event extraction
- AJILE12 naturalistic event extraction
- bigP3BCI event alignment and symbol target extraction
- CI and coverage thresholds
