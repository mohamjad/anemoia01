# Source Of Truth

## Identity

`anemoia01` is the private implementation engine for:

```text
Intent Fidelity Evaluation Infrastructure for Adaptive Neural Interfaces
```

Core sentence:

```text
Intent fidelity is the metric object. Nonstationarity is the condition. Evaluation infrastructure is the product.
```

## Primary Claim

Decoder accuracy is necessary but can be insufficient for long-term neural
interfaces when supervision is weak, delayed, self-paced, behaviorally
confounded, or mediated by adaptive decoders/language models.

The repo evaluates when conventional decoder metrics and intent-fidelity metrics
select different methods.

## What This Is

- resource registry for open neural-interface datasets
- benchmark-construction engine for multi-session and weak-label data
- metric library for explicit weak target distributions
- protocol suite for held-out-session, recalibration, communication,
  authorization, and naturalistic evaluations
- baseline comparison engine
- reporting layer for dataset cards, claim cards, eval cards, and figures

## What This Is Not

- not a BCI decoder company
- not a general neuroscience theory
- not a claim that true intent is directly observed
- not a claim that plasticity explains all drift
- not a manifesto
- not a public proof before real-data evidence exists

## Language

Use:

- intent fidelity
- weak target distribution
- task-relevant intended state
- intent proxy
- fidelity to declared weak target
- neural nonstationarity
- ranking disagreement
- over-adaptation
- held-out-session reliability
- evaluation layer
- monitoring layer
- adaptive neural-interface ops

Avoid:

- meaning gap as headline
- plasticity signal as central object
- noise, drift, and ambiguity are the same problem
- the brain intended
- we model what the brain means
- this solves neuroplasticity
- no one has built this

## Measurement Contract

We do not observe intent directly.

We construct uncertainty-aware target distributions from available proxies:

- task prompts
- timing windows
- behavioral outputs
- endorsement signals
- language priors
- authorization states
- session metadata

The metric evaluates fidelity to the declared proxy, not metaphysical intent.

## Core Flow

Every dataset should eventually become:

```text
resource manifest
-> dataset-specific raw contract
-> weak target construction
-> protocol split
-> method comparison
-> ranking disagreement report
-> claim card
```

## First Resources

Priority resources:

1. FALCON H2
2. Card 2024 speech neuroprosthesis
3. Willett 2023 speech neuroprosthesis
4. Kunz 2025 inner / attempted speech
5. AJILE12
6. bigP3BCI

FALCON H2 is the first infrastructure path.

Card/Willett/Kunz are the conceptual speech path.

AJILE12 is a scaffold path for naturalistic weak labels. bigP3BCI is the first
non-FALCON fixture-backed artifact bundle path for P300-style selection weak
targets, but it is not downloaded-data evidence yet.

## Old Repo Relationship

`neurodrift-lab` remains the exploratory thesis prototype.

This repo is the infrastructure conversion.

Port only the useful pieces:

- weak target patterns
- proper scoring ideas
- ranking disagreement
- over-adaptation detection
- synthetic sanity check
- report and CLI discipline

Do not port the old public framing.
