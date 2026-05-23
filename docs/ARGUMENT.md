# Argument

## Thesis

Adaptive neural-interface systems need evaluation artifacts that make weak
supervision explicit.

Decoder accuracy is necessary. It is not always sufficient when labels are
delayed, self-paced, behaviorally confounded, or mediated by adaptive decoders
and language models.

The missing artifact is not a claim about true intent. The missing artifact is a
reproducible evaluation record that states:

- what proxy was used
- how weak targets were constructed
- what predictions were scored
- which protocol was applied
- whether method rankings changed under the proxy-fidelity metric
- what evidence level the result supports

## Measurement Contract

This repo does not observe true intent directly.

It builds weak target distributions from declared proxies:

- task prompts
- timing windows
- behavioral outputs
- endorsement signals
- language priors
- authorization states
- session metadata

The metric evaluates fidelity to those declared weak targets. This makes the
claim narrower, but also more testable.

## Why Conventional Accuracy Can Be Insufficient

Conventional decoder metrics are usually anchored to observed outputs or labels.
That is appropriate when the target is stable, immediate, and unambiguous.

Long-running adaptive neural interfaces can violate those assumptions:

- sessions differ
- neural recordings shift
- task timing is uncertain
- behavior is an imperfect proxy
- labels may arrive late or indirectly
- language models can improve surface output while changing attribution
- adaptive updates can improve one score while degrading another

In those cases, method selection should not depend on a single point target or a
single conventional metric. It should preserve an auditable relationship between
the method and the declared proxy distribution.

## What The Infrastructure Tests

The repo asks whether methods remain faithful to declared weak target
distributions under explicit protocols.

It supports:

- proper scoring of probability distributions
- held-out-session evaluation
- communication and language-prior scaffolds
- authorization-state scaffolds
- naturalistic weak-label scaffolds
- P300-style selection scaffolds
- ranking disagreement reports
- over-adaptation checks
- reproducible artifact bundles

The central diagnostic is ranking disagreement:

```text
Do conventional metrics and intent-fidelity metrics rank methods differently?
```

The operational diagnostic is over-adaptation:

```text
Did a method improve a conventional score while worsening fidelity to the
declared proxy?
```

## Current Evidence

The strongest current path is FALCON H2.

Implemented and tested:

- DANDI asset discovery for FALCON H2
- local NWB/HDF5 inventory
- FALCON H2 trial cue parsing
- declared cue-character weak target construction
- deterministic baseline prediction export
- held-out-session `EvalResult` scoring
- eval-card rendering
- comparison report rendering
- artifact-bundle manifest
- bundle validation
- source-file hashing and provenance

Completed local downloaded-data runs:

- a sanity artifact bundle using one NWB file per required FALCON H2 split
- a feature-baseline method bundle using five held-in train sessions and all
  five held-out calibration sessions
- three feature baselines: `identity_centroid`,
  `session_centered_centroid`, and `whitened_centroid`
- validated bundles with no issues

This supports a narrow claim:

```text
The repository can produce and validate a reproducible FALCON H2 local evidence
bundle from downloaded NWB files, including simple feature-baseline method
comparisons against declared cue-character weak target proxies.
```

It does not yet support these claims:

- full FALCON H2 benchmark coverage
- superiority of a neural decoder
- real ranking disagreement among the tested FALCON H2 feature baselines
- direct measurement of true intent

The current feature-baseline result is a null ranking-disagreement result:
proxy top-1 error and intent-fidelity log loss ranked the three tested centroid
baselines the same way. That is a useful empirical boundary, not a failed
artifact.

## Why The Current Result Is Still Useful

The sanity result is not compelling because the proxy-oracle baseline wins. That
is expected and not the scientific point.

The feature-baseline result is more informative: it tests plausible methods and
finds no ranking disagreement in the current FALCON H2 subset. That means the
repo should not claim that accuracy fails here. It should claim that the
evidence object can now reveal agreement or disagreement explicitly.

That is compelling as infrastructure because it shows that the repo now
produces the evidence object the rest of the work depends on:

```text
data provenance
-> declared weak targets
-> baseline predictions
-> protocol result
-> report cards
-> comparison artifact
-> validation report
```

That artifact is reproducible, typed, scope-limited, and explicit about proxy
assumptions. This is the foundation needed before stronger method comparisons
or broader dataset claims are credible.

## Next Stronger Claim

The next substantive step is not more framing. It is stronger method evidence.

Recommended next implementation:

```text
FALCON H2 train/test NWB files
-> feature-window examples
-> centroid or session-normalized baselines
-> prediction JSONL
-> EvalResult JSON
-> ranking disagreement report
-> validated artifact bundle
```

That would move the repo from artifact plumbing evidence toward method
comparison evidence while staying within the same measurement contract.
