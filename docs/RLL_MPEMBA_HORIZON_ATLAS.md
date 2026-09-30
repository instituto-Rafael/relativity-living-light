# RLL MPEMBA HORIZON ATLAS

Status: **implemented bounded falsification gate; astrophysical Mpemba detection remains `TOKEN_VAZIO`**.

Date: 2026-08-27

## 1. Purpose

This module converts the session heuristic — compression/heating, black-hole thermodynamics, redshift, jets and anomalous relaxation — into independent claims that can survive or fail separately.

It deliberately does **not** define “gravitational Mpemba” by analogy alone. A real-data Mpemba claim requires an operational relaxation observable and a reproducible crossing/first-passage witness.

Canonical implementation:

```text
data/pipelines/strong_gravity/mpemba_horizon_falsifier.py
```

Evidence/falsifier contract:

```text
data/contracts/mpemba_horizon_falsifier.v1.json
```

Tests:

```text
tests/strong_gravity/test_mpemba_horizon_falsifier.py
```

## 2. Scientific separation: three temperatures and three observers

The original intuition mixes quantities that must be kept apart:

1. **plasma/matter temperature** in the accretion/jet environment;
2. **Hawking temperature** of the black hole in semiclassical thermodynamics;
3. **observer-dependent redshift/Tolman quantities** in a stationary exterior geometry.

The gate prohibits silently identifying these quantities.

Likewise it separates:

- a static exterior observer;
- a freely falling observer;
- a distant observer at infinity.

The static Schwarzschild redshift factor used here is

\[
\alpha(r)=\sqrt{1-\frac{r_s}{r}},\qquad r_s=\frac{2GM}{c^2},\qquad r>r_s.
\]

The static-equilibrium Tolman relation is represented as

\[
T_{\rm loc}=\frac{T_\infty}{\alpha(r)}.
\]

This expression is **not** promoted to a freely falling thermometer reading and the implementation rejects `r <= r_s` for the static-observer formula.

## 3. Direct, inverse, derivative and antiderivative structure

For a Schwarzschild black hole,

\[
T_H(M)=\frac{\hbar c^3}{8\pi Gk_BM},
\]

so

\[
\frac{dT_H}{dM}=-\frac{T_H}{M}<0.
\]

With `E=Mc^2`,

\[
C_{BH}=\frac{dE}{dT_H}
=-\frac{8\pi G k_B M^2}{\hbar c}<0.
\]

Thus, in the Schwarzschild semiclassical domain,

```text
M up -> T_H down
M down -> T_H up
```

while the Bekenstein-Hawking entropy is

\[
S_{BH}=\frac{4\pi k_BG M^2}{\hbar c}.
\]

The implementation checks the exact scaling probes

```text
T_H(2M)/T_H(M) = 1/2
S_BH(2M)/S_BH(M) = 4
C_BH < 0
dT_H/dM < 0
```

within the stated model domain.

These analytic identities are not observational measurements of Hawking radiation.

## 4. F-gap materialized

| ID | claim fragment | state | reason |
|---|---|---|---|
| BH-MP-01 | Schwarzschild `T_H ~ M^-1`, `S ~ M^2`, negative heat capacity | `SUPPORTED_ANALYTIC_SEMICLASSICAL` | analytic black-hole thermodynamics |
| BH-MP-02 | static Tolman temperature = freely falling local temperature | `FALSIFIED_AS_EQUIVALENCE` | observer classes differ |
| BH-MP-03 | past/present/future literally form one measured thermodynamic state at the horizon | `REJECT_LITERAL_CLAIM` | not an operational GR thermodynamic observable |
| BH-MP-04 | observed jet matter escapes from inside the horizon | `FALSIFIED_BY_CAUSAL_BOUNDARY` | event horizon is causal boundary |
| BH-MP-05 | exterior magnetized plasma + spin/flux can participate in jet launching | `LITERATURE_OBSERVATION_SUPPORTED_BOUNDED` | BZ/MAD class mechanisms + EHT constraints |
| BH-MP-06 | astrophysical black hole directly exhibits a Mpemba relaxation | `TOKEN_VAZIO` | no matched trajectory analysis ingested |
| BH-MP-07 | Mpemba-like relaxation has relativistic/holographic precedents | `LITERATURE_SUPPORTED_THEORY` | Unruh and holographic work exists |
| BH-MP-08 | Hawking temperature directly measured for M87* or Sgr A* | `TOKEN_VAZIO` | no direct astrophysical Hawking thermometry registered |
| BH-MP-09 | generic curved spacetime guarantees one global scalar energy conservation law | `REJECT_OVERGENERALIZATION` | local covariant conservation and symmetry-specific charges are the safe formulation |

The key epistemic transition is therefore:

```text
analogy -> decomposed claims -> independent falsifiers -> bounded survivors
```

not

```text
analogy -> global confirmation
```

## 5. F-next: operational Mpemba witness

Let `X(t)` be an observable state vector and `X_eq` its target equilibrium. Define **before inspecting the result** a distance

\[
D(t)=D[X(t),X_{eq}].
\]

For two initial states, `far` and `near`, the v1 witness requires all three:

\[
D_{far}(0)>D_{near}(0),
\]

\[
\exists t>0:\;D_{far}(t)<D_{near}(t),
\]

and for a preregistered threshold `epsilon`,

\[
\tau_{far}(\epsilon)<\tau_{near}(\epsilon),
\]

where

\[
\tau(\epsilon)=\inf\{t:D(t)\le\epsilon\}.
\]

The code implements this as `mpemba_witness(...)`.

### Slow-mode mechanism probe

Recent Mpemba literature emphasizes suppression/overlap of the slowest relaxation mode. The bridge therefore also exposes

```text
slow_mode_suppression_ratio = |A_slow,far| / |A_slow,near|
```

as a diagnostic. A ratio below one is **not** by itself a Mpemba detection; it is a mechanism probe to be combined with the trajectory witness.

## 6. Synthetic fixture vs nature

The runtime `baseline()` contains a deterministic synthetic pair of relaxation curves that intentionally satisfies the witness. Its only purpose is to test the gate.

It always emits:

```json
{
  "evidence_grade": "SYNTHETIC_GATE_FIXTURE_PLUS_ANALYTIC_IDENTITIES",
  "global_scientific_claim_allowed": false
}
```

Therefore a passing unit test cannot be cited as an astrophysical result.

## 7. Recent literature bridge

### Black-hole thermodynamics

- Mann, R. B. (2026), **Black-hole thermodynamics**, *Nature Reviews Physics* 8, 425-436, DOI `10.1038/s42254-026-00942-9`. Used as a current review of the established thermodynamic framework and open non-equilibrium problems.

### Mpemba definitions and mechanism

- Vu & Hayakawa (2025), **Thermomajorization Mpemba Effect**, *Physical Review Letters* 134, 107101, DOI `10.1103/PhysRevLett.134.107101`. Used to guard against dependence on an arbitrary single distance measure.
- **Resource-Theoretical Unification of Mpemba Effects: Classical and Quantum** (2026), *Physical Review X* 16, 011065, DOI `10.1103/rbt4-psfd`. Used for the slow-mode/relaxation organization.
- Wang et al. (2026), **Quantum Mpemba-like effect in Unruh thermalization**, *JHEP* 2026, 183, DOI `10.1007/JHEP06(2026)183`, arXiv:2509.05756. This is a relativistic-QFT thermalization precedent, not an astrophysical black-hole observation.
- Ge, Ishigaki, Lei & Tian (2026), **Quantum Mpemba effect in holography**, arXiv:2607.20899. This preprint uses a shifted free energy built from energy flux into a black-hole horizon as a monotonic distance and relates the anomalous relaxation to quasinormal-mode competition. It is retained as `preprint_theory` until publication status changes.

## 8. Real observational anchors

### M87* polarimetry

The EHT 2017/2018/2021 analysis published in 2025 reports a stable ring scale but changing polarization structure and improved constraints on 230 GHz emission near the jet base:

```text
DOI 10.1051/0004-6361/202555855
```

These data constrain **magnetized plasma dynamics**. They do not measure Hawking temperature.

### M87* jet-base localization

A 2026 EHT analysis uses radio intensity across baseline scales plus modeling to localize a likely compact jet-base region:

```text
DOI 10.1051/0004-6361/202557022
```

This is an exterior accretion/jet anchor and directly blocks the narrative that observed jet material must emerge from inside the event horizon.

### Public products identified for the next numerical cycle

The EHT data portal lists:

```text
2026-D01-01 — 2018 and 2021 calibrated polarimetric data
released 2026-06-29
```

The source has been identified but **not numerically ingested or SHA256-verified in this RLL gate yet**, therefore:

```text
EHT_TIME_DOMAIN_NUMERIC_INGEST = TOKEN_VAZIO
```

## 9. Falsifier cascade

A real astrophysical Mpemba claim must survive, at minimum:

1. **Domain falsifier** — no static-horizon formula outside its domain.
2. **Observer falsifier** — no static/free-fall equivalence by notation.
3. **Causal falsifier** — no material propagation from inside horizon to infinity.
4. **Distance falsifier** — effect must not be an artifact of one post-hoc distance choice.
5. **Threshold falsifier** — `epsilon` cannot be selected after inspecting crossings.
6. **Covariance falsifier** — calibration/noise covariance must be propagated.
7. **Null-model falsifier** — ordinary turbulent/GRMHD/radiative-transfer relaxation must be compared.
8. **Slow-mode falsifier** — candidate mode suppression must be tested/ablated where a mode decomposition is meaningful.
9. **Look-elsewhere falsifier** — campaign/source/time-window selection cannot be outcome-driven.
10. **Replication falsifier** — independent rerun must recover the result within declared tolerance.

Failure of an ancestor produces:

```text
QUARANTINE_FROM_DESCENDANTS
```

while the historical receipt remains append-only.

## 10. ATLAS total routing

### `ATLAS:X`

Canonical route for this subject:

```text
session heuristic
 -> strong_gravity existing bridges
 -> mpemba_horizon_falsifier
 -> evidence contract
 -> public-data ingest
 -> matched relaxation analysis
 -> falsifier cascade
 -> bounded claim ledger
```

### `L:X` — longitudinal

Preserve every transition of each `BH-MP-*` claim. A failed or superseded state is not deleted.

### `O:X` — orthogonal

Keep independent axes for:

```text
thermodynamics | observer/coordinates | plasma | jet | relaxation | observation | cosmological relevance
```

A pass on one axis cannot automatically promote another.

### `T:X` — transversal

Permitted bridges include:

```text
black-hole thermodynamics <-> non-equilibrium relaxation
QFT/Unruh <-> Mpemba precedent
holography <-> horizon-flux distance
EHT polarimetry <-> exterior plasma dynamics
EHT jet base <-> jet-launching constraints
```

Every bridge carries a `does_not_support` boundary.

### `REL:X`

Relations are typed as:

```text
DERIVES | SUPPORTS | CONSTRAINS | ANALOGY_ONLY | FALSIFIES | DOES_NOT_SUPPORT | TOKEN_VAZIO
```

### `SCALE:X`

Never collapse scales:

```text
quantum/open-system -> QFT detector -> holographic bulk -> horizon-scale plasma -> astrophysical jet
```

A structural resemblance is not a scale-transfer proof.

### `EVID:X`

Evidence ordering:

```text
analytic identity
peer-reviewed theory
preprint theory
public observational metadata
checksum-verified numerical observational data
covariance-aware reproduced inference
```

The labels describe source class, not a universal ranking of truth.

### `GAP:X`

Current protected gaps:

```text
direct Hawking thermometry = TOKEN_VAZIO
astrophysical Mpemba witness = TOKEN_VAZIO
EHT time-domain numeric ingest + SHA256 = TOKEN_VAZIO
preregistered D(t) for EHT = TOKEN_VAZIO
covariance-aware fit = TOKEN_VAZIO
independent reproduction = TOKEN_VAZIO
```

### `LEARN:X`

A gap closes only by a receipt carrying source identity, checksum where applicable, command, parameters, result, uncertainty, falsifier outcomes and exact claim transition.

## 11. Next executable evidence cycle

The strongest next cycle is not another synthetic formula. It is:

1. materialize the public EHT 2018/2021 calibrated polarimetric products;
2. record source URLs/DOIs, local filenames, license/access context and SHA256;
3. freeze an immutable input manifest;
4. select one time-resolved observable that has a physically defensible target state;
5. preregister the admissible `D(t)` family and `epsilon` rule;
6. define far/near initial ordering without using the later crossing;
7. propagate calibration/covariance uncertainty;
8. compare ordinary relaxation/turbulence/GRMHD-compatible nulls before any Mpemba interpretation;
9. run the witness and all negative controls;
10. write an append-only receipt;
11. promote `BH-MP-06` only if the complete gate passes.

Until step 11:

```text
BH-MP-06 = TOKEN_VAZIO
```

## 12. Boundary with RLL cosmology

This strong-gravity module does **not** connect a local Mpemba-like relaxation to an RLL cosmological-background modification. Any path to `H(z)`, BAO, CMB, growth or an RLL-vs-LambdaCDM preference requires an explicit independent bridge and its own likelihood/falsification gate.

```text
local strong-gravity anomaly != cosmological model validation
```
