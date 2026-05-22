# Protocols

Pass 1 defines result schemas for:

- held-out session
- few-shot recalibration
- communication
- authorization
- naturalistic weak-label evaluation

Each protocol produces an `EvalResult` with method scores and optional ranking
disagreement metadata. Concrete dataset ingestion and split generation are pass
2 work.

FALCON H2 now has a held-out-session path that can:

- parse trial cue windows from NWB/HDF5 files
- export declared weak targets
- score target-construction sanity baselines
- score external prediction JSONL files
