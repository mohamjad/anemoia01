# Implementation Plan

## Pass 1

Build architecture, docs, schemas, metrics, CLI, and tests.

Do not attempt full real dataset ingestion in this pass.

### 1. Package Skeleton

```text
src/intentfidelity/
  resources/
  ingest/
  labels/
  metrics/
  protocols/
  baselines/
  reports/
  figures/
  cli/
```

### 2. Resource Registry

Add YAML manifests for:

- `falcon_h2`
- `card2024`
- `willett2023`
- `kunz2025`
- `ajile12`
- `bigp3bci`

Implement manifest validation and dataset-card generation.

### 3. Weak Targets

Implement:

- `WeakTarget`
- `Prediction`
- support validation
- probability normalization
- metadata and source typing

### 4. Metrics

Implement:

- log loss
- Brier score
- Jensen-Shannon divergence
- KL divergence where appropriate
- optional energy score for continuous targets
- intent-fidelity loss
- ranking disagreement
- over-adaptation detection
- calibration utilities

### 5. Protocols

Implement result schemas for:

- held-out session
- few-shot recalibration
- communication evaluation
- authorization evaluation
- naturalistic weak-label evaluation

Each protocol should produce an `EvalResult`.

### 6. Baselines

Start with registry entries:

- identity
- session centering
- Procrustes
- CCA
- whitening-coloring
- supervised fine-tune placeholder
- LM-heavy placeholder
- LM-light placeholder

Do not overbuild ML models before ingestion works.

### 7. Reports

Implement:

- `DatasetCard`
- `ClaimCard`
- `EvalCard`
- JSON and Markdown rendering

### 8. CLI

Initial commands:

```text
intentfidelity resources list
intentfidelity resources validate
intentfidelity resources card <dataset_id>
intentfidelity eval summarize outputs/results.json
intentfidelity report dataset-card <dataset_id>
intentfidelity report eval-card outputs/results.json
intentfidelity figure ranking-reversal outputs/results.json
```

Commands may be stubbed where data ingestion is incomplete, but architecture
must be clear and testable.

### 9. Experiments

Create:

```text
experiments/00_synthetic_sanity_check/
experiments/01_falcon_h2_ranking_disagreement/
experiments/02_card2024_speech_fidelity/
experiments/03_willett2023_lm_attribution/
experiments/04_kunz2025_authorized_intent/
experiments/05_ajile12_naturalistic_weak_labels/
```

Each folder gets:

- `README.md`
- `config.yaml`
- `run.py`
- `expected_outputs.md`
- `notes.md`

## Pass 2

Integrate the first serious dataset path.

Recommended order:

1. FALCON H2
2. Card 2024

Goal:

```text
real data → weak target construction → held-out-session protocol → eval card
```

## Acceptance Criteria

- README explains the repo in 60 seconds.
- No plasticity/meaning overclaiming.
- Resource registry exists.
- Weak target metric exists.
- Protocol result schema exists.
- Ranking disagreement and over-adaptation are tested.
- Synthetic experiment is labeled as a sanity check.
- FALCON H2 and Card2024 are clear first targets.
- Tests pass.
