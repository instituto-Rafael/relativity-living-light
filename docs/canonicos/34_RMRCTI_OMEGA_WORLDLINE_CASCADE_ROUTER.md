# RMRCTI / Ω7 / RLL — Worldline, Cascade and Multiregime Formula Router

Date: 2026-09-12
Status: RESEARCH_ROUTER_CONTRACT
claim_allowed: false

## 0. Purpose

This document consolidates the longitudinal path from RMRCTI/gbs3_color.c and Ω7 into a cosmology-facing routing contract.

It does not assert a new cosmological law. It defines how observations, event chains, reference frames, physical regimes, formulas, uncertainties, falsifiers and receipts are connected without mixing operational metrics with physical quantities.

Core invariant:

```text
SOURCE != MODEL
MODEL != REGIME
REGIME != FORMULA
FORMULA != EXECUTION
EXECUTION != EVIDENCE
EVIDENCE != CLAIM
TOKEN_VAZIO != ZERO
ANALOGY != MECHANISM
NUMERICAL_AGREEMENT != PHYSICAL_IDENTITY
```

## 1. Canonical RMRCTI source identity

Primary source lineage:

```text
rafaelmeloreisnovo/llamaRafaelia
└── rmrCti/gbs3_color.c
```

The oral aliases `GCB_color3`, `gbs_color_3.c` and related variants are reconciled to `rmrCti/gbs3_color.c` in the canonical knowledge tree.

The code computes:

[
Delta P =
P(stable\_any=1\mid peak)
-
P(stable\_any=1\mid nonpeak).
]

The arena maps it to directional bias:

```text
deltaP > 0.20 -> bias 2
deltaP > 0.05 -> bias 1
otherwise     -> bias 0
```

Therefore `DeltaP ~= 0.18` belongs to the intermediate routing band in this demonstrator.

It is not physical pressure, cosmological density, a force, a probability of truth, an attractor proof or a universal constant.

## 2. Geometry and index reconciliation

The canonical RMRCTI records preserve the geometric defaults:

```text
R = 2.0
r = 0.7
kappa = 0.22
alpha = pi/7
beta = pi/9
lambda = 1000
```

The user-recalled index around 70 is not silently identified with `r=0.7`.

```text
r = 0.7
TOKEN_VAZIO_INDEX_AROUND_70 != r
```

## 3. Ω7 projection layer

Operational projections:

[
D_7 = \{+X,-X,+Y,-Y,+Z,-Z,Omega_{context}\}.
]

Persistence diagnostic:

[
	au_{t,d}
=
\operatorname{distance}
\left(
P_d(S_t),P_d(S_{t-1})
\right).
]

A persistent difference/tremor is a routing signal.

```text
PERSISTENCE -> EXPAND/PROBE
PERSISTENCE != TRUTH
```

No Ω7 direction is interpreted physically until a local frame and coordinate map are declared.

## 4. Event-chain worldline model

A material element, star, ejecta packet, plasma parcel or compact-object test body can undergo multiple causal events:

```text
E0 ejection/explosion
 -> propagation
E1 stellar encounter
 -> propagation
E2 gravitational slingshot
 -> propagation
E3 collision/shock
 -> propagation
E4 strong-field passage
 -> emission
OBS observation
```

The state immediately after event k is:

[
X_k^+
=
\{
x^\mu,
u^\mu,
p^\mu,
	au,
g_{\mu\nu},
F_{\mu\nu},
\rho,
T,
B,
composition,
provenance,
uncertainty
\}.
]

Continuous propagation is represented by:

[
X_{k+1}^- =
\Phi_k
\left(
X_k^+;g_{\mu\nu},F_{\mu\nu},boundary
\right).
]

A discrete event updates the state:

[
X_{k+1}^+ =
\mathcal E_{k+1}
\left(
X_{k+1}^-,
event\_parameters
\right).
]

This replaces naive Euclidean addition of several velocity vectors when relativistic speeds or strong gravitational fields matter.

## 5. Time is multi-layered

Minimum temporal state:

[
T =
\{
\tau_{proper},
t_{coordinate},
t_{emit},
t_{arrival},
t_{observer}
\}.
]

Proper time obeys:

[
d\tau^2
=
-\frac{1}{c^2}
g_{\mu\nu}dx^\mu dx^\nu.
]

Consequences:

```text
SAME_IMAGE != SAME_EVENT
SAME_SKY_DIRECTION != SAME_DISTANCE
SAME_OBSERVATION_TIME != SAME_EMISSION_TIME
```

The exact observed redshift is routed through the invariant photon-frequency relation:

[
1+z =
\frac{(k_\mu u^\mu)_{emit}}
     {(k_\mu u^\mu)_{obs}}.
]

Any decomposition into cosmological, Doppler and gravitational pieces must be declared as a model decomposition rather than assumed by visual proximity.

## 6. Strong-field time boundary

Near a black-hole horizon, a distant coordinate description and the infalling object's proper time differ.

For a stationary Schwarzschild clock outside the horizon:

[
\frac{d\tau}{dt}
=
\sqrt{1-\frac{r_s}{r}}.
]

This tends to zero as `r -> r_s` for that stationary-coordinate construction.

An infalling body crosses the horizon in finite proper time.

Therefore:

```text
DISTANT_COORDINATE_SLOWING != PROPER_TIME_STOPS
HORIZON_CROSSING != PHYSICAL_FREEZE
```

## 7. Milky Way scale gate

Current public astronomical references do not support a Milky Way diameter of 150 million or 150 billion light-years.

Operational scale separation:

```text
stellar disk:
  >100,000 light-years across (order of magnitude)

dark-matter / virial halo:
  characteristic radius is model-dependent and of order hundreds of kpc
  literature examples span roughly 120-300 kpc radius
  -> about 0.8-2.0 million light-years in diameter

Local Group / larger cosmic web:
  separate dynamical scales; do not relabel as "Milky Way diameter"
```

The virial boundary is model-dependent and is not a sharp visible edge.

Scale source examples:
- NASA Science, Galaxies, updated 2026-08-12: Milky Way stellar disk spans more than 100,000 light-years.
- Jiao et al., MNRAS 2024: model-dependent r200 examples near 119 and 187 kpc.
- Fritz et al./satellite-motion literature: virial-radius estimates can extend to roughly 300 kpc depending on assumptions.

Gate:

```text
DISK_SCALE != HALO_SCALE != LOCAL_GROUP_SCALE != COSMIC_WEB_SCALE
```

## 8. Regime router

Each observation is classified before selecting equations.

### 8.1 Cosmological background

Use for large-scale expansion observables:

```text
H(z)
E(z)
distances
BAO
CMB background/compressed observables
```

Do not use a Friedmann background equation to directly explain a local shock, vortex or ejecta plume.

### 8.2 Weak/strong gravity

Weak field:

[
\epsilon_g = \frac{GM}{rc^2}.
]

If `epsilon_g << 1`, weak-field approximations may be admissible.

If not, route to full GR / Kerr / Schwarzschild / numerical relativity as required by the source.

### 8.3 Plasma / MHD / GRMHD

Candidate diagnostics include:

[
\beta_{plasma}=\frac{p_{gas}}{p_B},
\qquad
v_A=\frac{B}{\sqrt{\mu_0\rho}}.
]

Magnetic fields can alter plasma dynamics and contribute to stress-energy.

```text
MAGNETIC_DYNAMICS != MODIFIED_G
PLASMA_GRAVITY_LABEL != NEW_FUNDAMENTAL_FORCE
```

### 8.4 Shock / collision

Use conservation across a discontinuity, e.g. Rankine-Hugoniot-type relations, when a real shock regime is established.

Water-hammer/Joukowsky logic may be used only as an analogy class for impulse-propagation-reflection-relaxation unless the domain assumptions are actually satisfied.

### 8.5 Nuclear event

Mass-energy bookkeeping:

[
Q=(m_{initial}-m_{final})c^2.
]

```text
MASS_DEFECT != TOTAL_MASS_DISAPPEARANCE
TOROIDAL_PLUME_SHAPE != MATTER_ENERGY_RETURN_PROOF
```

### 8.6 Vorticity / toroidal plume

Toroidal morphology first routes to:

```text
vorticity
buoyancy
shear
entrainment
Rayleigh-Taylor
Kelvin-Helmholtz
MHD terms when magnetized
```

A toroidal shape is a geometry to explain, not a mechanism by itself.

## 9. Cascade / avalanche / linearity taxonomy

Three separate objects are preserved.

### A. Physical causal cascade

[
E_i \to E_{i+1} \to E_{i+2}
]

where an event physically changes a downstream state.

### B. Observational cascade

A single physical cause changes several observables:

```text
event
 -> velocity
 -> temperature
 -> ionization
 -> spectrum
 -> polarization
 -> inferred parameters
```

This is not multiple independent causes.

### C. Computational sensitivity avalanche

For a transition map `X_{k+1}=F_k(X_k)`, define the local Jacobian:

[
J_k = \frac{\partial F_k}{\partial X_k}.
]

A candidate amplification diagnostic across several events is:

[
A_{i\to j}
=
\left\|
J_{j-1}J_{j-2}\cdots J_i
\right\|.
]

For numerical stability, track the logarithm:

[
\Lambda_{i\to j}
=
\sum_{k=i}^{j-1}\log\|J_k\|.
]

Interpretation:

```text
Lambda >> 0  -> perturbation amplification candidate
Lambda ~ 0   -> neutral/local-linear candidate
Lambda << 0  -> contraction/recovery candidate
```

This is a proposed diagnostic. It is not itself a physical law or proof of a cosmological avalanche.

## 10. Linear versus nonlinear regime

Define a dimensionless perturbation ratio:

[
\epsilon_X =
\frac{\|\delta X\|}{\max(\|X\|,X_{floor})}.
]

A model-specific tolerance must be declared before using labels.

```text
epsilon_X small + Jacobian stable -> linearized route candidate
epsilon_X large or state-dependent Jacobian -> nonlinear route
transition region -> run both and compare residuals
```

No universal numeric cutoff is hard-coded here.

## 11. Observation-window provenance

Every observational window must preserve:

```text
OBS_ID
instrument
timestamp
sky coordinates
distance/redshift posterior
spectral band
resolution
selection function
calibration
raw/source URL
license
SHA/hash where available
covariance/uncertainty
foreground/background classification
model assumptions
```

Material in the same image can originate from different distances and epochs.

The router must test line-of-sight superposition before combining physical states.

## 12. RMRCTI adapter

RMRCTI remains above the physical layer as a stability/routing diagnostic.

Pipeline:

```text
physical event chain
 -> observables
 -> model prediction
 -> residual vector
 -> state classification
 -> peak/nonpeak partition
 -> DeltaP
 -> Omega7 projection
 -> routing signal
```

Forbidden shortcut:

```text
DeltaP ~= 0.18
 -> cosmological constant / gravity law / physical pressure
```

Allowed bounded interpretation:

```text
DeltaP ~= 0.18
 -> STABILITY_CANDIDATE in the declared RMRCTI metric
 -> test recurrence under independent traces, seeds, parameters and nulls
```

## 13. Longitudinal / transversal / holistic / antiderivative views

### Longitudinal

Follow one object or state through ordered events and accumulated proper time.

### Transversal

At one observational epoch, compare independent objects, instruments, wavelengths, regimes or models.

### Holistic

Join only variables that share a declared causal/provenance relationship; preserve independent nuisance variables.

### Operational antiderivative/backtrace

Reconstruct the minimum upstream event chain capable of producing the observed state.

This is not automatically a calculus antiderivative.

If the continuous dynamics are invertible and boundary conditions are known, integrate the differential model backward.

Otherwise use a constrained inverse problem and preserve non-uniqueness:

```text
ONE_OBSERVATION -> MULTIPLE_CAUSAL_HISTORIES possible
```

## 14. Bounded multilevel stochastic permutation

A total Cartesian permutation is forbidden because it grows combinatorially and spends compute without proportional evidence.

Instead use seeded stochastic permutation with pruning.

Levels:

```text
L0 observation subsets
L1 event-order hypotheses
L2 physical-regime combinations
L3 frame/coordinate choices
L4 formula routes
L5 parameter perturbations
L6 null/adversarial controls
L7 provenance/evidence states
```

Sampling record:

```text
PERMUTATION_SEED
candidate_path
dependencies
pruned_by
evidence_gain
cost
novelty
falsifier_result
receipt
```

Selection score may be operationally ranked by:

[
S =
\log_2(1+information\_gain)
+
\log_2(1+uncertainty\_reduction)
-
\log_2(1+cost).
]

This score is triage only.

Stopping rule:

```text
STOP when:
- all P0 dependency branches have at least one falsifier,
AND
- marginal evidence gain falls below the next unresolved critical-path gap,
OR
- budget/compute boundary is reached,
OR
- a fail-closed gate blocks descendants.
```

Randomization is reproducible, never "random total" without seed.

## 15. Formula routing record

Every formula intended for scientific use should gain:

```text
FORMULA_ID
NAME
DOMAIN
REGIME
WHEN_USE
WHY_USE
INPUTS
OUTPUTS
UNITS
ASSUMPTIONS
BOUNDARY_CONDITIONS
DO_NOT_USE_WHEN
PRIMARY_SOURCE
IMPLEMENTATION
TEST
INVERSE_TEST
UNCERTAINTY
CONFOUNDERS
OBSERVABLE_MAP
RECEIPT
NEXT_FORMULA
CLAIM_ALLOWED
```

## 16. Existing RMRCTI assets not to duplicate

Primary source already contains:
- scalar DeltaP report;
- discrete cumulative integral whose terminal identity is `I_N = DeltaP`;
- exact conditional/hypergeometric falsifier;
- trace provenance and SHA;
- multi-run dispersion;
- arena consumer;
- RAF_FIBO fwd/rev/inv/inv+rev transforms.

The new router sits above these tools.

## 17. Current epistemic state

```text
RMRCTI metric definition              DOCUMENTED
gbs3_color identity                  RECONCILED
DeltaP ~= 0.18                       STABILITY_CANDIDATE
real independent repeated traces     TOKEN_VAZIO
dynamical attractor                  TOKEN_VAZIO
universal cosmological mapping       TOKEN_VAZIO
r = 0.7                              SOURCE_OBSERVED_GEOMETRIC_PARAMETER
index around 70                      TOKEN_VAZIO_INDEX_AROUND_70
worldline-event router               CONTRACT_CANDIDATE
cascade Jacobian diagnostic          PROPOSED_DIAGNOSTIC
cosmological causal validation       TOKEN_VAZIO
```

## 18. Provenance

Repository primary sources:
- rafaelmeloreisnovo/llamaRafaelia/rmrCti/gbs3_color.c
- rafaelmeloreisnovo/llamaRafaelia/rmrCti/INDEX.md
- rafaelmeloreisnovo/llamaRafaelia/rmrCti/RMRCTI_KNOWLEDGE_TREE_CANONICAL_RECORD.md
- instituto-Rafael/relativity-living-light/docs/canonicos/33_RMRCTI_OMEGA_DELTA_P_STABILITY.md

Project corpus context:
- CHUNK-LEARN-RMRCTI-STABILITY-STRATEGY-OMEGA7-V1-20260907
- Gravidade e magnetismo.txt
- other cosmology/project conversation material remains context until mapped to a typed source.

External scientific scale references:
- NASA Science, "Galaxies", updated 2026-08-12.
- Jiao et al., MNRAS 2024, dark-matter profile / virial radius model dependence.
- satellite-kinematic Milky-Way mass literature with virial-radius estimates of order a few hundred kpc.

Copyright/provenance:
No external code is copied. Scientific equations included here are standard relations or project-defined candidate diagnostics; external literature is referenced for scientific context, not vendored.

## 19. R3

F_ok:
- RMRCTI and gbs3_color identity preserved;
- DeltaP semantics preserved;
- r=0.7 separated from the unresolved ~70 index;
- worldline event chain distinguishes propagation from impulses;
- proper/coordinate/emission/arrival/observer times separated;
- cascade, avalanche and linear/nonlinear routes typed separately;
- Milky Way disk/halo scales separated;
- stochastic permutation is bounded, seeded and auditable;
- formula routing metadata defined.

F_gap:
- real independent RMRCTI traces are still missing for stronger DeltaP claims;
- exact semantic identity of the user-recalled ~70 index remains open;
- event-chain router is a contract, not an executed astrophysical inference engine;
- cascade Jacobian thresholds and domain-specific norms remain to be benchmarked;
- no observational dataset currently establishes an RMRCTI-to-cosmology causal bridge.

F_next:
Create one synthetic, provenance-complete event-chain fixture with:
1. ejection;
2. free/weak-field propagation;
3. gravitational slingshot;
4. shock impulse;
5. strong-field segment;
6. emission/observation timing;
then compare linearized versus nonlinear propagation, compute the cascade sensitivity diagnostic, produce residuals and route those residuals into RMRCTI without using DeltaP as a physical quantity.
