# Pass 4 Communication And Authorization

Pass 4 adds the first executable scaffold for the speech and authorization
resource path:

- text transcript targets and predictions
- character and word error rates
- communication eval results
- language-prior attribution between LM-light and LM-heavy method scores
- authorization events as weak target distributions
- authorization eval results

These are protocol scaffolds. The synthetic experiment runners validate file
shape, metric plumbing, and report rendering only. They are not real-data
evidence for Card 2024, Willett 2023, or Kunz 2025.

The intended real-data path remains:

```text
resource manifest
-> speech or authorization proxy extraction
-> weak target distribution
-> method prediction import
-> protocol result
-> report card
```
