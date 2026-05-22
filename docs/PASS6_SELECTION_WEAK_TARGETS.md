# Pass 6 Selection Weak Targets

Pass 6 adds the first executable scaffold for bigP3BCI-style P300 selection
evaluations:

- P300 selection proxy events
- confidence-weighted weak target distributions over candidate symbols
- JSONL event IO
- selection proxy summaries
- explicit `selection` protocol results
- Markdown report rendering
- CLI evaluation from event and prediction JSONL files
- a synthetic bigP3BCI experiment scaffold

This is still a scaffold. Prompted symbols, observed selections, timing windows,
and session metadata are intent proxies. Event alignment and matrix timing are
dataset-specific ingestion work.
