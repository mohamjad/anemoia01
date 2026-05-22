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
- run centroid feature baselines over character-window neural summaries

Method comparison reports can summarize ranking disagreement for one result and
over-adaptation events between two results.

Pass 4 adds executable communication and authorization scaffolds:

- communication scores text predictions against declared transcript proxies
- language-prior attribution compares LM-light and LM-heavy method scores
- authorization scores predictions against authorization-state weak targets

These scaffolds expose the protocol contracts before real speech-path ingestion.

Pass 5 adds a naturalistic weak-label evaluator for AJILE12-style behavior
proxies. It scores predictions against confidence-weighted weak targets and
records proxy confidence and ambiguity metadata on the `EvalResult`.
