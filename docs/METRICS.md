# Metrics

Metrics operate on declared weak target distributions and prediction
distributions with matching support.

Implemented in pass 1:

- log loss
- Brier score
- KL divergence
- Jensen-Shannon divergence
- energy score for continuous sanity checks
- intent-fidelity log loss
- ranking disagreement
- over-adaptation detection
- expected calibration error
- ranking reversal rate
- character error rate
- word error rate
- language-prior attribution delta

For FALCON H2 pass 2, `intent_fidelity_log_loss` is computed over character
targets derived from declared handwriting prompt cues and trial timing windows.

These metrics evaluate fidelity to declared proxies. They do not claim direct
measurement of true intent.
