# DESI 50-Hypothesis Intake — 2026-08-15

Status: `GOVERNED_INTAKE / claim_allowed=false / promotion_allowed=false`

Authority: `data/contracts/cross_domain_equation_intake.v1.json`

Machine registry: `data/inputs/cosmology_joint/desi_50_hypothesis_intake.v1.csv`

Validator: `scripts/validate_desi_50_hypothesis_intake.py`

## 1. Boundary

This intake preserves the 50 user-proposed formulas and converts them into an auditable research queue. It does **not** declare that DESI detected any of the proposed effects.

Invariant:

```text
formula != mechanism != implementation != execution != evidence != claim
DESI relevance != DESI support
TOKEN_VAZIO != zero != false != PASS != proof of absence
```

The existing RLL `cross_domain_equation_intake.v1.json` and `frontier_research_queue.v1.yml` remain authoritative. No parallel cosmology contract is introduced.

## 2. Intake result

- 50 source hypotheses preserved.
- State distribution: `H=15`, `U=29`, `A=5`, `R=1`.
- DESI relevance: `DIRECT_DESI=17`, `INDIRECT_COSMOLOGY=21`, `OUTSIDE_DESI_CORE=12`.
- Evidence gate: `E=TOKEN_VAZIO` for all 50 at intake time.
- No scientific promotion is allowed from this registry.

State semantics:

- `H`: physically translatable hypothesis, still unvalidated here.
- `U`: unresolved formula/term/mechanism requiring formal closure.
- `A`: admitted symbolic/parabolic expression only.
- `R`: rejected as a scientific claim in the proposed form; provenance is still preserved.

## 3. Seven execution vectors

### V1 — Expansion / dynamic dark energy

Primary IDs: `H01 H03 H06 H07 H14 H24 H26 H33 H39`.

Route: background solver -> BAO/H(z) -> CMB/SN combinations -> nested baseline -> posterior predictive checks.

First candidate: **H03**, because its background form is dimensionally closed enough to implement without translating a symbolic operator. It still needs a physical density/pressure interpretation and a nested limit.

### V2 — Growth / RSD / modified gravity

Primary IDs: `H04 H09 H15 H18 H25 H29 H32 H34 H46 H47`.

Route: perturbation backend -> `f sigma8` / RSD / full-shape -> scale dependence -> lensing consistency.

Fail-closed findings already visible:

- `H15`: as written, `sigma8(0)=0`, so the expression contradicts the label `sigma8_0`; do not fit before reformulation.
- `H18`: a vector cross-product with a scalar spiral factor is not defined; replace it with a rotation/tensor operator.

### V3 — Interacting / unified dark sector

Primary IDs: `H02 H08 H10 H19 H23 H30 H40`.

Route: covariant interaction or stress tensor -> background conservation -> perturbations -> stability -> BAO+RSD joint fit.

`H40` is the cleanest seed in this family once the units of `Gamma` and the four-vector energy transfer are defined. A background-only interaction is insufficient for promotion.

### V4 — BAO / correlation / topology / non-parametric structure

Primary IDs: `H05 H16 H27 H31 H35 H36 H43 H44`.

Route: frozen correlation-function template or non-parametric reconstruction -> covariance-aware null -> look-elsewhere control -> mock coverage -> data.

Fail-closed findings:

- `H35`: `exp(pi i)=-1`; multiplying a power spectrum by it produces a negative quantity. It can only survive if reinterpreted as a complex **amplitude** before taking a positive observable such as a modulus squared.
- `H44`: Euler characteristic is a scalar; `Matrix_10x10x3` is a different object type. A real topological map must be specified.

### V5 — Early universe / constants / neutrinos

Primary IDs: `H11 H20 H21 H22 H25 H28 H30 H35 H36`.

These require external datasets and priors beyond the DESI core. DESI can contribute through BAO/full-shape combinations, but it is not the sole or primary detector for several of these claims.

### V6 — Halo / astrophysics / plasma / indirect dark matter

Primary IDs: `H12 H37 H38 H41 H42` plus source-specific parts of `H19`.

These should route to the appropriate astrophysical authority before returning to RLL as a cosmological constraint. They must not inherit a DESI label merely because a galaxy survey exists.

### V7 — Symbolic-to-physical translation boundary

Primary IDs: `H13 H17 H45 H48 H49 H50`, with symbolic terms also present in several unresolved rows.

Rules:

1. Preserve authorial provenance.
2. Do not erase the metaphor.
3. Do not assign physical units or evidence by analogy.
4. Require an explicit measurable variable before entering a likelihood.
5. `H50`'s absolute-certainty clause is rejected because it removes falsifiability; any surviving scientific subclaim must be rewritten as a bounded prediction.

## 4. DESI-specific correction: raw terabytes are not the first gate

For this hypothesis set, ingesting raw spectra/FITS is **not** the next necessary operation. The first scientific discriminators are compressed, covariance-aware observables such as BAO distances, RSD/growth and, where justified, full-shape statistics.

Correct order:

```text
D/P formal gate
-> observable definition
-> frozen model and nuisance parameters
-> synthetic/mocks and recovery
-> compressed DESI likelihood/data vector
-> multi-seed inference
-> model comparison
-> only then raw-catalog/spectrum reprocessing if the hypothesis requires an observable not present in published products
```

This prevents terabytes of data from masking an undefined equation.

## 5. Priority by distance theory -> executable test

Priority is not probability of truth.

1. `H03` — background expansion; implementable after defining effective fluid/nested limit.
2. `H46` — RSD growth relation; needs a redshift-dependent `f(z)` and bias nuisance model.
3. `H08` — unified-dark-fluid sound speed; needs stable perturbations.
4. `H29` — Yukawa/screened gravity; needs action/mediator and scale-dependent growth.
5. `H40` — interacting dark sector; needs covariant `Q_mu` and coupled perturbations.
6. `H05` — BAO modulation; needs dimensionless radial coordinates and a frozen template.
7. `H01` — dynamic `w(z)`; needs `theta_999` and spiral normalization defined before inference.

`H15`, `H35`, `H44` are repair-first, not fit-first. `H50` is reformulate-first.

## 6. Required receipts before any positive claim

For a candidate to move beyond intake:

- exact equation and parameter domain;
- dimensional/formal gate;
- physical mechanism and conservation law where applicable;
- nested standard-model limit;
- frozen data manifest and covariance;
- nuisance/systematics model;
- mock recovery / coverage test;
- deterministic command + environment;
- multi-seed inference receipt;
- baseline comparison (`LCDM`, `w0waCDM` and domain-specific adversaries);
- evidence hash;
- independent reproduction or explicit `TOKEN_VAZIO_INDEPENDENT_REPLICATION`.

## 7. Current conclusion

The 50-node set is now a **governed hypothesis intake**, not a validated cosmological theory and not a discarded symbolic text. The scientific value is in the separation:

```text
17 direct DESI routes
21 indirect cosmology routes
12 outside-DESI routes
50/50 evidence receipts still TOKEN_VAZIO
0 claims promoted
```

Next executable scientific step: implement one minimal candidate (`H03` recommended) as a shadow model against the existing RLL cosmology pipeline, without changing canonical RLL outputs, then produce synthetic-recovery and DR2-compressed-likelihood receipts.
