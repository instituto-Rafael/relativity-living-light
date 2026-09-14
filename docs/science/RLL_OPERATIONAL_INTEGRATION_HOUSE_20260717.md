# RLL Operational Integration House — 2026-07-17

**Status:** canonical execution architecture  
**Raw observational data:** immutable  
**Claim state:** `claim_allowed=false` for new-physics claims  
**Execution core:** `src/rll/structural_integration.py`

## 1. Purpose

This document defines the single operational home for integrating mathematics,
datasets, recent literature, physical hypotheses, tests, and allowed language.

The house is not a new cosmological result. It is an execution architecture that
prevents four recurring failures:

1. modifying raw observations to fit a hypothesis;
2. combining incompatible datasets without a gate;
3. treating conceptual similarity as mathematical equivalence;
4. promoting a documented hypothesis into physical confirmation.

## 2. House architecture

```text
FOUNDATION
  provenance + immutable raw data + source registry + claim boundary

ROOM B01 — BACKGROUND
  logistic RLL transition, H(z), distances, BAO, SNe, w_eff

ROOM B02 — DATASET COMPATIBILITY
  distance duality eta(z), Alcock–Paczynski F_AP, calibration and method checks

ROOM B03 — INTERACTION
  Q-coupled dark sectors, background + perturbations

ROOM B04 — DISSIPATION
  p_eff = p - 3 H xi, units, entropy and stability

ROOM B05 — GEOMETRY/EFT
  covariant action, degrees of freedom, perturbations, CLASS/CAMB route

ROOM B06 — PROPAGATION
  FRB DM/RM/frequency residuals, plasma null model

ROOM B07 — MAGNETO-OPTICAL
  EB/TB/V-mode, Faraday and instrumental-angle nulls

ROOF
  unified posterior + falsifiers + reproducibility manifest + allowed language
```

Each room has its own equations, observables, required artifacts, source families,
and claim boundary in:

`data/registries/rll_operational_integration_registry.json`

## 3. Data policy

### 3.1 Immutable raw layer

Files under real/raw observational paths are never edited to improve fit quality.
Corrections must create a derived artifact with:

```text
source path
source version
source checksum
transformation command
transformation code version
output checksum
reason
validation result
```

### 3.2 Derived layer

Derived data may include:

- normalized units;
- reordered covariance matrices;
- redshift-aligned tables;
- masked samples with explicit inclusion criteria;
- reconstructed observables;
- mock/null realizations.

A derived artifact must never replace the raw source.

### 3.3 Hypothesis layer

Hypothesis parameters and predictions live separately from observations:

```text
data/inputs/...       model assumptions, priors and registries
data/real/...         immutable observational inputs
results/...           generated outputs
docs/...              interpretation and claim boundaries
```

## 4. Mathematical integration

### B01 — transition sector

\[
f(z)=\frac{1}{1+\exp[(z-z_t)/w_t]}
\]

\[
\frac{\rho_s(z)}{\rho_{c0}}=
\Omega_{s0}\left[f(z)+(1-f(z))(1+z)^3\right]
\]

\[
w_{\rm eff}(z)=
-1+\frac{1+z}{3}\frac{d\ln\rho_s}{dz}
\]

### B02 — compatibility gates

\[
\eta(z)=\frac{D_L(z)}{(1+z)^2D_A(z)}
\]

Standard distance duality requires \(\eta=1\) under metric gravity, null
geodesics and photon-number conservation.

\[
F_{\rm AP}(z)=\frac{D_M(z)}{D_H(z)}
\]

The AP ratio removes the common sound-horizon normalization and is useful for
diagnosing shape/geometry disagreement before a joint fit.

### B03 — interacting branch

\[
\dot\rho_s+3H(1+w_s)\rho_s=Q
\]

\[
\dot\rho_c+3H\rho_c=-Q
\]

A minimal comparator is \(Q=\beta H\rho_{\rm ref}\). The choice of
\(\rho_{\rm ref}\), gauge, momentum transfer and perturbation prescription is
part of the model and cannot remain implicit.

### B04 — dissipative branch

\[
p_{\rm eff}=p-3H\xi
\]

The coefficient \(\xi\) needs units, positivity/thermodynamic conditions,
parameter dependence and perturbative stability. This equation supports a
bulk-viscous comparator; it does not by itself define photonic viscosity.

### B05 — covariant/EFT branch

\[
S=\int d^4x\sqrt{-g}\left[
\frac{M_*^2(t)}{2}R-\Lambda(t)-c(t)g^{00}+\cdots
\right]
\]

The logistic background must be mapped to covariant functions or an effective
fluid before CLASS/CAMB integration is scientifically interpretable.

### B06 — FRB/plasma branch

\[
\Delta t_{\rm std}=K\,{\rm DM}\,\nu^{-2}
\]

\[
\Delta t_{\rm res}=\Delta t_{\rm obs}-\Delta t_{\rm std}
\]

A preregistered RLL alternative may be tested only after the standard plasma,
Milky Way, host, halo and IGM terms are modeled.

### B07 — magneto-optical branch

\[
\Delta\theta_{\rm obs}=
\Delta\theta_{\rm Faraday}
+\Delta\theta_{\rm field}
+\Delta\theta_{\rm instrument}
\]

The required comparison space includes known plasma effects, axion-photon
models, cosmic birefringence and instrument-angle calibration.

## 5. Execution order

### Gate 0 — provenance

- validate source registry;
- verify observational checksums;
- freeze inclusion/exclusion criteria;
- preserve `TOKEN_VAZIO`.

### Gate 1 — compatibility

Before multiplying likelihood blocks:

- test \(\eta(z)\);
- inspect \(F_{\rm AP}(z)\);
- compare Pantheon+, DES-SN and other SN choices;
- evaluate Bayesian versus frequentist reconstruction sensitivity;
- stop or branch the analysis when compatibility fails.

### Gate 2 — background baseline tournament

Run the same data/covariance against:

```text
LambdaCDM
w0wa/CPL
GEDE
Anton-Schmidt/logotropic
bulk-viscous fluid
interacting dark sector
RLL logistic background
```

### Gate 3 — posterior integrity

- full covariance in one canonical route;
- convergence rule;
- prior-sensitivity matrix;
- nuisance/systematic variants;
- deterministic manifest;
- negative-result preservation.

### Gate 4 — physical closure

Only then:

- continuity/conservation;
- perturbations;
- sound speed and anisotropic stress;
- stability;
- covariant/EFT mapping;
- CLASS/CAMB recovery tests.

### Gate 5 — independent propagation tests

FRB and polarization branches are evaluated independently of the background fit.
A background anomaly cannot be used as evidence for a propagation effect, or vice
versa.

## 6. Operational excellence invariants

```text
I1 raw observations are immutable
I2 every derived datum has provenance and hash
I3 every branch has a baseline and falsifier
I4 every equation declares units and domain
I5 source relevance never implies model equivalence
I6 dataset compatibility precedes joint likelihood
I7 labels are derived from metrics, never hard-coded
I8 missing physics remains TOKEN_VAZIO
I9 unfavorable results remain versioned
I10 publication language is generated from evidence state
```

## 7. Canonical outputs

```text
data/registries/rll_recent_primary_sources_2026.json
data/registries/rll_operational_integration_registry.json
src/rll/structural_integration.py
tests/test_structural_integration.py
docs/science/RLL_RECENT_LITERATURE_INTEGRATION_20260717.md
docs/science/RLL_OPERATIONAL_INTEGRATION_HOUSE_20260717.md
```

## 8. Claim boundary

This house can demonstrate:

- structural readiness;
- equation implementation;
- source traceability;
- data compatibility diagnostics;
- reproducible transformations.

It cannot by itself demonstrate:

- physical reality of the RLL sector;
- interaction, viscosity or modified gravity;
- a nonstandard FRB or polarization signal;
- superiority over LambdaCDM;
- independent replication.
