# RLL — Ancient Worlds Cosmocronology Session Packet — 2026-08-16

**State:** `HYPOTHESIS_PROGRAM / claim_allowed=false`  
**Cross-index:** `rafaelmeloreisnovo/Mapa:data/session-ledgers/RAFAELIA_SESSION_FAMILY_OBSERVATIONS_20260816.v1.jsonl`

## Purpose

Use old planetary systems as cosmological clocks without promoting age tension into evidence for a prior Big Bang/cycle.

## 1. Competing model clock

For any background model `M`:

```math
t_0(M)=\int_0^\infty \frac{dz}{(1+z)H_M(z)}
```

The session proposes comparing at least:

```text
LCDM
CPL / w0-wa
RLL tested background sector
specified bounce/cyclic model j
```

No model has default privilege in the likelihood.

## 2. Object residual

For object/system `i`:

```math
R_{chrono,i}(M)=t_0(M)-t_{star,i}-t_{enrichment,min,i}-t_{formation,min,i}
```

A standardized tension must include cosmological-age, stellar-clock, enrichment, formation and systematic terms. A nominal negative central value is insufficient.

Interpretation:

```text
R >= 0                         accommodated
R < 0 but systematics overlap  tension only
robust R << 0 in independent clocks  anomaly candidate
```

## 3. Ancient-world anchors from the session

- Kepler-444: old compact system used as an anchor for early small-planet formation; session source was Campante et al. 2015, arXiv:1501.06227.
- K2-111 and the 2025 rocky-planet composition/age sample were used as examples of why extreme nominal ages require clock/systematic caution.
- Early JWST enrichment results and the Whalen et al. 2025 primordial-supernova water simulations were used as countermodels showing that the current hot-Big-Bang history can produce useful chemistry very early.

These anchors are inputs to a clock test, not claims of pre-Big-Bang objects.

## 4. Null and alternative

```text
H0: all observed planetary/stellar systems formed after the current hot phase.
H1_j: a specified prior contraction/bounce exists and a specified information class survives the transition.
```

A generic statement “there were previous Big Bangs” is too flexible to be a falsifiable H1. Each `H1_j` must define:

```text
pre-bounce dynamics
matching/transfer rule
entropy treatment
perturbation transfer
what baryonic/field/information structure can survive
exclusive observable
```

Unspecified elements are `TOKEN_VAZIO`.

## 5. Discriminants

### Age excess

Require independent chronometers and a predeclared significance rule.

### Chemical impossibility

Compare abundance vector against post-Big-Bang enrichment/yield envelope, including model uncertainty and covariance.

### Formation-time floor

Do not hardcode first-planet formation time. It must come from enrichment + dust/disk + assembly models and their uncertainty.

### Primordial/bounce signature

A model-specific gravitational-wave/CMB/compact-object or other relic can become discriminating only if the same signature is not reproduced by the null family.

## 6. Important negative boundary

```text
local galaxy/structure collapse != global cosmological contraction
```

A global bounce requires the scale factor dynamics:

```math
H=\dot a/a
```

with contraction `H<0`, bounce `H=0`, expansion `H>0`.

## 7. RLL historical evidence boundary

This packet does not alter existing RLL negative/limited results. The tested additional sector remains subject to the repository's existing likelihood/Bayes evidence and claim gates.

The session program asks a new question — whether old-system chronology can provide an additional falsification axis — without converting it into evidence already obtained.

## 8. Dependency graph

```text
UniverseAgeModel
 -> StellarClocks
 -> EnrichmentFloor
 -> PlanetFormationFloor
 -> ObjectResiduals
 -> ChemicalEnvelope
 -> ModelSpecificBounceTransfer
 -> ExclusiveObservable
 -> BayesianComparison
 -> IndependentReplication
```

## 9. Open tokens

```text
PRE_BIG_BANG_RELIC = TOKEN_VAZIO
BOUNCE_TRANSFER_RULE = TOKEN_VAZIO_PER_MODEL
FORMATION_FLOOR_POSTERIOR = TOKEN_VAZIO_PENDING_DATASET
CHEMICAL_ENVELOPE_COVARIANCE = TOKEN_VAZIO
INDEPENDENT_REPLICATION = TOKEN_VAZIO
```

## 10. Claim boundary

```text
ancient planets exist                 != prior cycle detected
early chemical enrichment             != life detected
age tension                           != cosmological crisis
cosmological crisis                   != cyclic universe proven
bounce model exists mathematically    != bounce observed
```
