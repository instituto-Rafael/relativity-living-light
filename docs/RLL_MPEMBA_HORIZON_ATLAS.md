# RLL MPEMBA HORIZON ATLAS

Status: **implemented bounded falsification gate; astrophysical Mpemba detection remains `TOKEN_VAZIO`**.

Date: 2026-08-27  
Authority: `instituto-Rafael/relativity-living-light`  
Maturity route: `work branch -> rll/lab -> rll/integration -> rll/release -> main`

## 1. Purpose

This gate decomposes the session heuristic — compression/heating, black-hole thermodynamics, observer time/redshift, plasma/jets and anomalous relaxation — into independently falsifiable fragments. Structural resemblance is never promoted to observation.

Artifacts:

- `data/pipelines/strong_gravity/mpemba_horizon_falsifier.py`
- `data/contracts/mpemba_horizon_falsifier.v1.json`
- `tests/strong_gravity/test_mpemba_horizon_falsifier.py`
- `.github/workflows/rll-mpemba-horizon-gate.yml`

## 2. Three quantities that must not collapse

1. matter/plasma temperature in the exterior accretion/jet environment;
2. semiclassical Hawking temperature of the black hole;
3. observer-dependent redshift/Tolman quantities in a stationary exterior spacetime.

The gate also separates static exterior, freely falling and asymptotic observers.

For Schwarzschild,

\[
r_s=\frac{2GM}{c^2},\qquad
\alpha(r)=\sqrt{1-\frac{r_s}{r}},\quad r>r_s,
\]

and the static-equilibrium Tolman relation is represented as

\[
T_{loc}=\frac{T_\infty}{\alpha(r)}.
\]

This is not re-labelled as a freely falling thermometer reading.

## 3. Direct / inverse / derivative / antiderivative structure

\[
T_H(M)=\frac{\hbar c^3}{8\pi Gk_BM},
\qquad
\frac{dT_H}{dM}=-\frac{T_H}{M}<0,
\]

\[
C_{BH}=\frac{d(Mc^2)}{dT_H}
=-\frac{8\pi Gk_BM^2}{\hbar c}<0,
\]

\[
S_{BH}=\frac{4\pi k_BG M^2}{\hbar c}.
\]

Deterministic probes:

```text
T_H(2M)/T_H(M) = 1/2
S_BH(2M)/S_BH(M) = 4
C_BH < 0
dT_H/dM < 0
```

These are analytic/semi-classical checks, not an astrophysical Hawking-radiation measurement.

## 4. F-gap ledger

| ID | fragment | state |
|---|---|---|
| BH-MP-01 | Schwarzschild `T_H ~ M^-1`, `S ~ M^2`, negative heat capacity | `SUPPORTED_ANALYTIC_SEMICLASSICAL` |
| BH-MP-02 | static Tolman temperature = free-fall local temperature | `FALSIFIED_AS_EQUIVALENCE` |
| BH-MP-03 | past/present/future literally form one local thermodynamic reading at the horizon | `REJECT_LITERAL_CLAIM` |
| BH-MP-04 | observed jet matter escapes from inside the horizon | `FALSIFIED_BY_CAUSAL_BOUNDARY` |
| BH-MP-05 | exterior magnetized plasma + spin/flux are relevant to jet launching | `LITERATURE_OBSERVATION_SUPPORTED_BOUNDED` |
| BH-MP-06 | astrophysical black hole directly exhibits a Mpemba relaxation | `TOKEN_VAZIO` |
| BH-MP-07 | Mpemba-like relaxation has relativistic-QFT/holographic precedents | `LITERATURE_SUPPORTED_THEORY` |
| BH-MP-08 | Hawking temperature directly measured for M87* or Sgr A* | `TOKEN_VAZIO` |
| BH-MP-09 | generic curved spacetime has one universal global scalar energy conservation law | `REJECT_OVERGENERALIZATION` |

## 5. F-next: operational Mpemba witness

Let `X(t)` be an observable state and `X_eq` a declared target. Fix, before inspecting the outcome,

\[
D(t)=D[X(t),X_{eq}].
\]

A v1 witness requires simultaneously

\[
D_{far}(0)>D_{near}(0),
\]

\[
\exists t>0: D_{far}(t)<D_{near}(t),
\]

and with preregistered `epsilon`,

\[
\tau_{far}(\epsilon)<\tau_{near}(\epsilon),
\qquad
\tau(\epsilon)=\inf\{t:D(t)\le\epsilon\}.
\]

The code implements this as `mpemba_witness(...)`.

### Slow-mode mechanism probe

A diagnostic

```text
|A_slow,far| / |A_slow,near|
```

checks whether the initially farther state has reduced overlap with the slowest relaxation channel. A ratio below one is a mechanism probe, never sufficient by itself for a detection.

## 6. Recent theory provenance

- Robert B. Mann, **Black-hole thermodynamics**, *Nature Reviews Physics* 8, 425–436 (2026), DOI `10.1038/s42254-026-00942-9`, published 2026-05-11. Current review of established thermodynamics and open non-equilibrium questions.
- Summer et al., **Resource-Theoretical Unification of Mpemba Effects: Classical and Quantum**, *Physical Review X* 16, 011065 (2026), DOI `10.1103/rbt4-psfd`, published 2026-03-25. Supports slow-mode-overlap organization of anomalous relaxation.
- Vu & Hayakawa, **Thermomajorization Mpemba Effect**, *Physical Review Letters* 134, 107101 (2025), DOI `10.1103/PhysRevLett.134.107101`. Supports distance-robust formulations in Markovian relaxation.
- Wang et al., **Quantum Mpemba-like effect in Unruh thermalization**, *JHEP* 2026, 183, DOI `10.1007/JHEP06(2026)183`, published 2026-06-17. Relativistic-QFT thermalization precedent only.
- Ge, Ishigaki, Lei & Tian, **Quantum Mpemba effect in holography**, arXiv:`2607.20899`, submitted 2026-07-23. Uses shifted free energy built from energy flux into a black-hole horizon and quasinormal-mode competition; retained as `preprint_theory`.

## 7. Real observational anchors

### M87* horizon-scale variability

EHT Collaboration, **Horizon-scale variability of M87* from 2017–2021 EHT observations**, *A&A* 704, A91 (2025), DOI `10.1051/0004-6361/202555855`.

It supplies real horizon-scale time variability and polarimetric/plasma constraints. It does **not** measure Hawking temperature and is not, without a dedicated preregistered relaxation analysis, a Mpemba detection.

### M87* jet-base localization

EHT Collaboration, **Probing jet base emission of M87* with the 2021 Event Horizon Telescope observations**, *A&A* 706, A27 (2026), DOI `10.1051/0004-6361/202557022`.

The observations/model comparison constrain a likely exterior jet-base component on black-hole-scale angular scales. The causal-horizon rejection of matter escaping from the interior comes from GR; the observation is an exterior jet-plasma anchor, not a direct horizon-crossing movie.

### Public numerical products

The EHT data portal lists `2026-D01-01 — 2018 and 2021 Calibrated polarimetric data`, last updated `2026-06-29`, referencing A&A 704 A91.

Current RLL state:

```text
EHT_2026_D01_01_IDENTIFIED = true
FILE_LEVEL_SHA256_VERIFIED_IN_RLL = false
NUMERIC_INGEST_COMPLETE = false
ASTROPHYSICAL_MPEMBA_INFERENCE = TOKEN_VAZIO
```

## 8. Falsifier cascade

A real astrophysical Mpemba claim must survive at least:

1. **domain** — no static-observer formula outside its domain;
2. **observer** — no static/free-fall equivalence by notation;
3. **causal** — no information/material propagation from inside an event horizon to infinity;
4. **observable** — equilibrium target and measured state are physically defensible;
5. **distance** — result is not an artifact of a post-hoc metric;
6. **threshold** — `epsilon` is not outcome-selected;
7. **covariance** — calibration/noise covariance and uncertainty are propagated;
8. **null model** — ordinary turbulence/GRMHD/radiative-transfer relaxation is compared;
9. **slow-mode** — mode suppression is ablated/tested where meaningful;
10. **look-elsewhere** — source/campaign/window selection is controlled;
11. **hold-out** — candidate rules survive data not used to choose them;
12. **replication** — independent rerun recovers the result within declared tolerance.

No finite list is claimed to be “all logically possible falsifiers”; this registry is append-only and expands when a new independent falsifier is identified.

## 9. ATLAS total

### `ATLAS:X`

```text
heuristic
 -> existing strong_gravity bridges
 -> decomposed BH-MP claim ledger
 -> source-class provenance
 -> analytic + negative tests
 -> public-data ingest
 -> preregistered relaxation inference
 -> falsifier cascade
 -> bounded claim transition
```

### `L:X`

Every claim-state transition is longitudinal and append-only. Superseded/failed states remain citable.

### `O:X`

Independent axes:

```text
thermodynamics | observer/coordinates | plasma | jet | relaxation | observation | cosmology
```

A pass on one axis never promotes another.

### `T:X`

Permitted bridges:

```text
black-hole thermodynamics <-> non-equilibrium relaxation
QFT/Unruh <-> Mpemba precedent
holography <-> horizon-flux distance
EHT variability/polarimetry <-> exterior plasma dynamics
EHT jet-base data <-> jet-launching constraints
```

Each bridge carries `does_not_support` boundaries.

### `REL:X`

```text
DERIVES | SUPPORTS | CONSTRAINS | ANALOGY_ONLY | FALSIFIES | DOES_NOT_SUPPORT | TOKEN_VAZIO
```

### `SCALE:X`

Do not collapse

```text
open quantum system -> QFT detector -> holographic bulk -> horizon-scale plasma -> astrophysical jet -> cosmology
```

### `EVID:X`

Source class is explicit: analytic identity, peer-reviewed theory/review, preprint theory, observational publication, public numerical product, checksum-verified local ingest, reproduced covariance-aware inference.

### `GAP:X`

Protected gaps:

```text
direct astrophysical Hawking thermometry = TOKEN_VAZIO
astrophysical Mpemba witness = TOKEN_VAZIO
EHT 2026-D01-01 numeric ingest + SHA256 = TOKEN_VAZIO
preregistered EHT D(t)/epsilon = TOKEN_VAZIO
covariance-aware matched fit = TOKEN_VAZIO
independent reproduction = TOKEN_VAZIO
```

### `LEARN:X`

A gap closes only with a receipt containing source identity, file checksums where applicable, exact command, parameters, uncertainty/covariance treatment, falsifier outcomes and exact claim transition.

## 10. Next evidence cycle

1. materialize the public EHT 2018/2021 products;
2. record URLs/DOIs, filenames, access/license context and SHA256;
3. freeze an immutable input manifest;
4. choose one time-resolved observable and equilibrium/target with physical justification;
5. preregister admissible `D(t)` and `epsilon`;
6. define far/near ordering independently of any later crossing;
7. propagate covariance/calibration uncertainty;
8. compare standard relaxation/turbulence/GRMHD-compatible nulls;
9. run witness, negative controls, ablations and look-elsewhere correction;
10. issue append-only execution receipt;
11. promote `BH-MP-06` only if the complete gate passes and is independently reproduced.

Until then:

```text
BH-MP-06 = TOKEN_VAZIO
global_scientific_claim_allowed = false
```

## 11. Cosmology boundary

A local strong-gravity/Mpemba-like anomaly does not imply a modified cosmological background, `H(z)` effect, BAO/CMB/growth prediction or an RLL-over-ΛCDM preference. Any such bridge requires its own model equation, likelihood, provenance and falsification gate.
