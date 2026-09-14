# RLL — Frontier Research Composition Orchestration

**Status:** experimental shadow pipeline  
**Claim policy:** `claim_allowed=false`  
**Publication effect:** `NONE`

## 1. Purpose

This orchestration treats every research fragment as a traceable object. It does not order ideas from small to large, large to small, old to new, or preferred to disfavored. The order is determined by evidential dependency:

```text
fragment
→ reference
→ falsifiable hypothesis
→ formal model
→ implementation
→ synthetic validation
→ observational validation
→ falsification
→ independent replication
→ bounded theory candidate
```

A fragment can be valuable without being promotable. A missing link is recorded as `TOKEN_VAZIO`, never silently replaced by zero, a default parameter, a metaphor, or an averaged confidence score.

## 2. Why this is necessary in frontier cosmology

Contemporary cosmology contains several layers that are often mixed prematurely:

1. phenomenological background descriptions such as `w0-wa`;
2. fluid or interacting-sector models;
3. modified-gravity or scalar-tensor theories;
4. nonparametric reconstructions;
5. perturbation and structure-growth predictions;
6. strong-gravity and plasma mechanisms;
7. global topology and geometry.

A good fit of `H(z)` does not establish a fundamental theory. A background model may reproduce distances while failing perturbation stability, gravitational-wave propagation, structure growth, or early-Universe consistency. The orchestration therefore prevents a background-only result from being promoted beyond its tested scope.

DESI DR2 motivates wider comparison because its official cosmology analysis reports increased evidence for evolving dark energy in combinations of BAO, CMB and supernova data, while extended analyses test both parametric and nonparametric descriptions. The pipeline uses that situation as a reason for stronger adversarial comparison, not as permission to declare a preferred ontology.

Primary anchors used by the queue:

- DESI DR2 Results II, `arXiv:2503.14738`;
- DESI extended dark-energy analysis, `arXiv:2503.14743`;
- interacting dark sectors with background and perturbations, `arXiv:2503.21652`;
- model-independent reconstruction after DESI DR2, `arXiv:2506.22953`.

These references establish active research routes. They do not validate RLL and do not authorize copying their conclusions into another model.

## 3. Ten gates

| Gate | Question | Missing state |
|---|---|---|
| `S0_FRAGMENT` | What is the smallest semantically complete fragment? | `TOKEN_VAZIO_FRAGMENT_BOUNDARY` |
| `S1_REFERENCE` | Which source supports it, and what does that source not support? | `TOKEN_VAZIO_SOURCE_BINDING` |
| `S2_HYPOTHESIS` | What observation could make the claim fail? | `TOKEN_VAZIO_FALSIFIABLE_HYPOTHESIS` |
| `S3_FORMALIZATION` | Are equations, dimensions, closure and limits explicit? | `TOKEN_VAZIO_FORMAL_CLOSURE` |
| `S4_IMPLEMENTATION` | Does code implement the declared mathematics without modifying raw data? | `TOKEN_VAZIO_IMPLEMENTATION_PARITY` |
| `S5_SYNTHETIC_VALIDATION` | Does the implementation recover limits and injected truth? | `TOKEN_VAZIO_SYNTHETIC_RECEIPT` |
| `S6_OBSERVATIONAL_VALIDATION` | Are data, covariance, objective, bounds and parameter counting fair? | `TOKEN_VAZIO_OBSERVATIONAL_PARITY` |
| `S7_FALSIFICATION` | Do adversarial baselines, ablations and residuals challenge the claim? | `TOKEN_VAZIO_FALSIFICATION_GATE` |
| `S8_REPLICATION` | Can an independent environment reproduce the receipt? | `TOKEN_VAZIO_INDEPENDENT_REPLICATION` |
| `S9_SYNTHESIS` | Is there a bounded synthesis with new predictions and unresolved contradictions exposed? | `TOKEN_VAZIO_THEORY_SYNTHESIS` |

No gate is bypassed by verbal coherence.

## 4. Prompt evolution to fixed point

The prompt is not rewritten indefinitely for rhetorical improvement. It is iterated through nine audit passes:

```text
atomize
→ source
→ formalize
→ test limits
→ compare implementation
→ audit statistics
→ attempt falsification
→ demand replication
→ synthesize
```

The orchestrator runs until a second iteration produces the same epistemic map. That is the fixed point. Remaining gaps are emitted as `TOKEN_VAZIO` with an exit condition. This prevents “another prompt” from being mistaken for new evidence.

## 5. Composition rule

Two fragments can be composed only when all of the following hold:

- they represent distinguishable physical sectors;
- their background conventions are compatible;
- no energy density, likelihood term or nuisance parameter is counted twice;
- dimensions are compatible;
- parameters are identifiable under the available data;
- each component has an off-switch that recovers a nested baseline;
- competitors use a common likelihood and frozen pre-execution contract.

Therefore:

```text
RLL + independently defined dynamic dark-energy sector
```

can be explored as a shadow composition, while:

```text
CPL + JBP + BA
```

is blocked unless a scientific reason establishes that these are separate physical sectors rather than competing parameterizations of the same function.

## 6. Frontier tracks and current boundaries

### Background phenomenology

Implemented in the shadow benchmark using `H(z)+DESI DR2 BAO`. This is a background-expansion diagnostic only.

### Einstein-equation extensions / modified gravity

`TOKEN_VAZIO_PERTURBATION_AND_STABILITY_BACKEND` until the project selects explicit field equations or an action and provides:

- a background solver;
- perturbation equations;
- ghost and gradient stability conditions;
- gravitational-wave propagation constraints;
- model-specific observables.

The phrase “Einstein extension” alone is not a model.

### Interacting dark sector

`TOKEN_VAZIO_COUPLED_BACKGROUND_PERTURBATIONS` until a covariant interaction term, conservation equations, perturbations, stability tests and coupling priors are implemented. Recent DESI DR2 studies show that interaction conclusions depend on datasets and on whether perturbations are included; this track must therefore not be approximated by a free background curve alone.

### Nonparametric reconstruction

`TOKEN_VAZIO_REGULARIZATION_AND_COVERAGE` until kernel or basis choices, hyperparameters, cross-validation and mock recovery are frozen. A flexible reconstruction is an adversarial lens, not automatically a physical theory.

### Early Universe and neutrinos

`TOKEN_VAZIO_BOLTZMANN_BACKEND` until recombination, neutrino hierarchy, sound horizons and CMB spectra are model-consistent.

### Strong gravity and plasma

Routed to a separate authority. It can enter cosmological synthesis only through an explicit stress-energy or effective-action bridge and observables that distinguish it from ordinary astrophysical systematics.

## 7. GitHub Actions behavior

The workflow is deliberately asymmetric:

### Automatic on pull request

- validate the YML contract;
- validate the fragment queue;
- iterate the prompt to fixed point;
- run adversarial unit tests;
- dry-load the model registry;
- upload receipts.

### Manual only

- numerical shadow smoke run;
- robust multi-seed analysis;
- external replication.

The automatic workflow does not spend compute on a full cosmological ranking and does not modify canonical result artifacts.

## 8. Current queue

The initial queue contains five first-class fragments:

1. RLL logistic background transition;
2. Einstein-equation extensions / modified gravity;
3. interacting dark sector;
4. nonparametric reconstruction;
5. strong-gravity plasma mechanisms.

Each has references, a current stage, evidence paths and explicit gaps. The queue is not a ranking of importance. It is a dependency-aware map of what can currently be tested.

## 9. Operational invariant

```text
concept ≠ implementation ≠ compilation ≠ execution ≠ evidence ≠ claim
```

This mirrors the Drive ↔ GitHub memory contract and keeps sources, operators, mathematics, tests and claims separated.

## 10. R3

```text
F_ok   = ten-stage composition pipeline, fixed-point prompt evolution, queue and CI receipts.
F_gap  = robust multi-seed receipt, perturbation/Boltzmann backends, independent replication.
F_next = run the PR structural workflow; only then schedule numerical smoke and robust analyses.
```
