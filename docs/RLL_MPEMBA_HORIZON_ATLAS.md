# RLL MPEMBA HORIZON ATLAS

Status: **implemented bounded falsification module; astrophysical Mpemba detection remains `TOKEN_VAZIO`**.

Date: 2026-08-27  
Authority: `instituto-Rafael/relativity-living-light`  
Maturity route: `work branch -> rll/lab -> rll/integration -> rll/release -> main`

## 1. Purpose and executable surface

This ATLAS decomposes the heuristic — compression/heating, black-hole thermodynamics, observer time/redshift, plasma/jets and anomalous relaxation — into claim fragments that survive or fail independently. Structural resemblance is never promoted to observation.

Artifacts:

- `data/pipelines/strong_gravity/mpemba_horizon_falsifier.py`
- `data/contracts/mpemba_horizon_falsifier.v1.json`
- `tests/strong_gravity/test_mpemba_horizon_falsifier.py`
- `FALSIFIABILITY_PROTOCOL.md` section 7

The regression tests run through the repository's **existing canonical Python-test CI**; no extra workflow is introduced solely for this hypothesis.

## 2. Three quantities and three observer classes

Never collapse:

1. matter/plasma temperature in the exterior accretion/jet environment;
2. semiclassical Hawking temperature of the black hole;
3. observer-dependent redshift/Tolman quantities in a stationary exterior spacetime.

Static exterior, freely falling and asymptotic observers are distinct.

For Schwarzschild,

\[
r_s=\frac{2GM}{c^2},\qquad
\alpha(r)=\sqrt{1-\frac{r_s}{r}},\quad r>r_s,
\]

and for static equilibrium

\[
T_{loc}=\frac{T_\infty}{\alpha(r)}.
\]

This expression is not a freely falling thermometer reading.

## 3. Direct / inverse / derivative / antiderivative

\[
T_H(M)=\frac{\hbar c^3}{8\pi Gk_BM},
\qquad
\frac{dT_H}{dM}=-\frac{T_H}{M}<0,
\]

\[
C_{BH}=\frac{d(Mc^2)}{dT_H}
=-\frac{8\pi Gk_BM^2}{\hbar c}<0,
\qquad
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

Fix before inspecting the claimed outcome

\[
D(t)=D[X(t),X_{eq}].
\]

The v1 witness requires all three:

\[
D_{far}(0)>D_{near}(0),
\]

\[
\exists t>0: D_{far}(t)<D_{near}(t),
\]

\[
\tau_{far}(\epsilon)<\tau_{near}(\epsilon),
\qquad
\tau(\epsilon)=\inf\{t:D(t)\le\epsilon\}.
\]

`mpemba_witness(...)` implements this. `epsilon`, observable, preprocessing, covariance treatment and admissible distance family must be preregistered for a real-data claim.

A slow-mode mechanism probe uses

```text
|A_slow,far| / |A_slow,near|
```

but suppression below one is only mechanistic evidence, not a detection by itself.

## 6. Recent theory provenance

- Mann, **Black-hole thermodynamics**, *Nature Reviews Physics* 8, 425–436 (2026), DOI `10.1038/s42254-026-00942-9`, published 2026-05-11.
- Summer et al., **Resource-Theoretical Unification of Mpemba Effects: Classical and Quantum**, *Physical Review X* 16, 011065 (2026), DOI `10.1103/rbt4-psfd`, published 2026-03-25. The initially more resourceful state can relax faster when it overlaps less with the slowest relevant channel.
- Vu & Hayakawa, **Thermomajorization Mpemba Effect**, *Physical Review Letters* 134, 107101 (2025), DOI `10.1103/PhysRevLett.134.107101`.
- Wang et al., **Quantum Mpemba-like effect in Unruh thermalization**, *JHEP* 2026, 183, DOI `10.1007/JHEP06(2026)183`, published 2026-06-17. Relativistic-QFT thermalization precedent only.
- Ge, Ishigaki, Lei & Tian, **Quantum Mpemba effect in holography**, arXiv:`2607.20899`, submitted 2026-07-23. Horizon-energy-flux/shifted-free-energy and quasinormal-mode precedent; retained as `preprint_theory`.

## 7. Real observational anchors

### M87* variability

EHT Collaboration, **Horizon-scale variability of M87* from 2017–2021 EHT observations**, *A&A* 704, A91 (2025), DOI `10.1051/0004-6361/202555855`.

It anchors real horizon-scale variability/plasma information. It neither measures Hawking temperature nor establishes a Mpemba trajectory without a dedicated preregistered analysis.

### M87* jet base

EHT Collaboration, **Probing jet base emission of M87* with the 2021 Event Horizon Telescope observations**, *A&A* 706, A27 (2026), DOI `10.1051/0004-6361/202557022`.

It constrains an exterior black-hole-scale jet-base component. The causal rejection of matter escaping from inside the event horizon comes from GR; the observation is an exterior jet/plasma anchor.

### Public products

The EHT portal lists `2026-D01-01 — 2018 and 2021 Calibrated polarimetric data`, last updated `2026-06-29`, referencing A&A 704 A91.

```text
EHT_2026_D01_01_IDENTIFIED = true
FILE_LEVEL_SHA256_VERIFIED_IN_RLL = false
NUMERIC_INGEST_COMPLETE = false
ASTROPHYSICAL_MPEMBA_INFERENCE = TOKEN_VAZIO
```

## 8. Falsifier cascade

A real astrophysical claim must survive, at minimum:

1. domain of the metric/formula;
2. observer-class separation;
3. causal-horizon boundary;
4. physically defensible observable/equilibrium target;
5. distance-family robustness and no post-hoc metric choice;
6. preregistered first-passage threshold;
7. covariance/calibration/noise propagation;
8. ordinary turbulence/GRMHD/radiative-transfer nulls;
9. slow-mode ablation where meaningful;
10. look-elsewhere/post-selection control;
11. hold-out data;
12. independent reproduction.

No finite list is claimed to contain every logically possible falsifier. New independent falsifiers are appended and may invalidate descendants.

## 9. ATLAS total

### `ATLAS:X`

```text
heuristic -> existing strong_gravity bridges -> claim ledger
-> source-class provenance -> analytic/negative tests
-> real-data ingest -> preregistered inference -> falsifier cascade
-> bounded claim transition
```

### `L:X`
Every claim transition is longitudinal and append-only; failed/superseded states remain citable.

### `O:X`
Independent axes: `thermodynamics | observer | plasma | jet | relaxation | observation | cosmology`.

### `T:X`
Permitted bridges include BH thermodynamics↔non-equilibrium relaxation, QFT/Unruh↔Mpemba precedent, holography↔horizon-flux distance, EHT variability↔exterior plasma, EHT jet-base↔jet constraints. Every bridge has `does_not_support` boundaries.

### `REL:X`
`DERIVES | SUPPORTS | CONSTRAINS | ANALOGY_ONLY | FALSIFIES | DOES_NOT_SUPPORT | TOKEN_VAZIO`.

### `SCALE:X`
Do not collapse `open-system -> QFT detector -> holographic bulk -> horizon-scale plasma -> astrophysical jet -> cosmology`.

### `EVID:X`
Explicit source classes: analytic identity, peer-reviewed theory/review, preprint theory, observational publication, public numerical product, checksum-verified local ingest, reproduced covariance-aware inference.

### `GAP:X`

```text
direct astrophysical Hawking thermometry = TOKEN_VAZIO
astrophysical Mpemba witness = TOKEN_VAZIO
EHT 2026-D01-01 numeric ingest + SHA256 = TOKEN_VAZIO
preregistered EHT D(t)/epsilon = TOKEN_VAZIO
covariance-aware matched fit = TOKEN_VAZIO
independent reproduction = TOKEN_VAZIO
```

### `LEARN:X`
A gap closes only through a receipt containing source identity, checksums where applicable, exact command/parameters, uncertainty/covariance treatment, falsifier outcomes and exact claim transition.

## 10. Next evidence cycle

1. materialize EHT 2018/2021 public products;
2. record DOI/source/access/license, filenames and SHA256;
3. freeze immutable input manifest;
4. choose a defensible time-resolved observable and target state;
5. preregister `D(t)`, admissible alternatives and `epsilon`;
6. define far/near ordering independently of the outcome;
7. propagate calibration/covariance uncertainty;
8. compare standard relaxation/turbulence/GRMHD-compatible nulls;
9. run witness, negative controls, ablations, hold-out and look-elsewhere controls;
10. issue append-only receipt;
11. promote `BH-MP-06` only after the complete gate and independent reproduction.

Until then:

```text
BH-MP-06 = TOKEN_VAZIO
global_scientific_claim_allowed = false
```

## 11. Cosmology boundary

A local strong-gravity/Mpemba-like anomaly does not imply a modified cosmological background, `H(z)`, BAO/CMB/growth prediction or RLL-over-ΛCDM preference. Any such bridge requires its own equation, likelihood, provenance and falsification gate.
