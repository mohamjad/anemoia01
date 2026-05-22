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

