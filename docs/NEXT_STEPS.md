# Next Steps

## Recommended Path

Start a real FALCON H2 evidence pass.

Why FALCON H2:

- it already has the strongest ingestion path
- tests cover NWB/HDF5 fixture parsing
- character weak targets and prediction scoring already exist
- method comparison and reporting are already wired

## Pass Objective

Produce a reproducible local evaluation bundle from FALCON H2 files:

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

1. Add an artifact bundle schema.
   - Suggested module: `src/intentfidelity/protocols/artifacts.py`
   - Include paths, dataset id, protocol, evidence level, and generated files.

2. Add a FALCON H2 bundle writer.
   - Suggested module: `src/intentfidelity/protocols/falcon_h2_artifacts.py`
   - Inputs: NWB path or inventory root.
   - Outputs: target JSONL, prediction JSONL, result JSON, eval card Markdown.

3. Add a CLI command.
   - Suggested command: `intentfidelity eval falcon-h2-bundle <nwb-file> <output-dir>`
   - Keep it deterministic and testable with synthetic HDF5 fixtures.

4. Add tests before touching downloaded data.
   - Extend `tests/test_cli.py`.
   - Add a focused artifact test.
   - Reuse the existing synthetic H2 fixture shape.

5. Add evidence documentation.
   - Document fixture evidence separately from downloaded dataset evidence.
   - Record exact commands used to generate artifacts.

## Acceptance Criteria

- `pytest -q` passes.
- The artifact command writes every expected file.
- The result loads through `load_eval_result`.
- The eval card states the evidence scope.
- No report implies direct access to true intent.
- Docs explain how to reproduce the run.

## Deferred Work

Only after the FALCON H2 bundle is stable:

- real Card/Willett speech-path ingestion
- Kunz authorization event extraction
- AJILE12 naturalistic event extraction
- bigP3BCI event alignment and symbol target extraction
- CI and coverage thresholds
