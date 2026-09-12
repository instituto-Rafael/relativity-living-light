# RLL Gap Retrofeedback V2 — append-only receipt

Date: 2026-09-12  
Authority: `instituto-Rafael/relativity-living-light`  
Parent scientific head: `356f26d67908a3e60ec5ca425e7e29f0f9a34d63`  
Claim allowed: **false**

## SOURCE / OBSERVATION

Observed exact-head workflow:
- workflow: `CLASS CAMB Baseline Crosscheck`;
- run id: `34709860843`;
- run number: `49`;
- result: `SUCCESS`;
- CAMB runtime: `1.6.6`;
- CLASS runtime: `3.3.4.0`.

Observed RLL recombination benchmark state:
`VERIFIED_RLL_RS_CAMB_REFERENCE_BENCHMARK`.

Maximum relative errors across the three pinned backgrounds:
- `zstar`: `0.0018749684301173745` (~0.1875%);
- `rstar` at the RLL fitted `zstar`: `0.0012887947018273345` (~0.1289%);
- `rstar` at CAMB `zstar`: `1.9301624644691983e-05` (~0.00193%).

Interpretation:
the bounded RLL sound-horizon integration/background path is extremely close to CAMB when the same `zstar` is supplied. The larger, still small, residual is mainly associated with the approximate `zstar` prescription.

This does **not** validate RLL perturbations, growth, model preference, MCMC, or publication claims.

## NEGATIVE PERTURBATION EVIDENCE PRESERVED

The same exact-head workflow executed:
`tools/rll_perturbation_barotropic_candidate_v1.py`.

Observed:
- cases: `9`;
- passing cases: `0`;
- state: `FALSIFIED_AS_GLOBAL_DEFAULT`.

This falsifies only the minimal separately conserved, barotropic/adiabatic,
`Q_mu=0`, shear-free closure as a global default over the declared sweep.

It does **not** falsify the RLL background model.

The monolithic theory gap is therefore decomposed into:
1. rest-frame sound-speed / entropy policy;
2. gauge policy;
3. super-horizon initial conditions;
4. interaction-current `Q_mu` policy;
5. anisotropic-stress policy;
6. conservation / transition-regularity validation.

## PROJECT-CORPUS PROVENANCE

Contextual source only; not execution evidence:

- `Gravidade e magnetismo.txt`
  - sha256: `c7df8b972be9e06f0bdc9c150ad16479e1e8a0d979c33e4dc97f50860781b2c7`
- `Fenômenos magnéticos e atmosféricos.txt`
  - sha256: `173f76c62bb675cf08c4658195d986016279737eed5b9a9262740aad27895479`
- `Estrutura de Modelos Cosmológicos.txt`
  - sha256: `1ac69f2041f7652e9c0ed32bed927b30652b2e3d8aa341fde6334aba09372e2a`

These hashes identify the exact session/project corpus snapshots used to fill provenance.
They do not promote any magneto-plasma claim.

## MULTIDIMENSIONAL TRANSFORMS

For every gap, V2 records:
- **direct**: forward effect unlocked by closure;
- **antiderivative_backtrace**: upstream evidence/provenance reconstructing the state;
- **inverse_falsifier**: what rejects the candidate;
- **reverse_rollback**: smallest reversible rollback;
- **exclusive_boundary**: inference explicitly forbidden;
- **recursive_feedback**: smaller gaps created after success/failure.

“Multilevel permutation” is implemented as dependency-topological traversal.
Blind Cartesian permutation is forbidden.

## LOGARITHMIC PRIORITY

Operational triage only:

`log2(impact) + log2(uncertainty_reduction) - log2(effort)`.

Factors are restricted to powers of two `{1,2,4,8}`.
This score is **not scientific evidence**.

## URGENCY / PROVIDÊNCIA

Current P0 critical path:
1. `GROWTH-CS2-001`;
2. `GROWTH-QMU-001`;
3. `GROWTH-SIGMA-001`;
4. `GROWTH-GAUGE-001`;
5. `GROWTH-IC-001`;
6. `GROWTH-CONSERVATION-001`;
7. `GROWTH-THEORY-001`;
8. `GROWTH-D-001`;
9. `GROWTH-F-001`;
10. `GROWTH-FSIG8-001`.

Best next minimal delta:
`GROWTH-CS2-001`.

Reason:
the silent default `c_s^2=c_a^2` is already ruled out by the declared sweep; choosing a versioned rest-frame sound-speed/entropy candidate removes a high-impact ambiguity before any `D(z)` implementation.

## NON-REGRESSION

- CMB benchmark evidence remains bounded to its declared flat standard-background scope.
- Historical outputs are not rewritten.
- Negative perturbation evidence is never erased.
- Magneto-plasma corpus is provenance/context only.
- alphaXiv retrieval/reporting remains discovery, not truth.
- `claim_allowed=false` globally.

## F_ok

- CMB benchmark token reduced to bounded evidence;
- 28 gaps/tokens now carry provenance, urgency, gate, mitigation, rollback and next step;
- monolithic perturbation token decomposed into falsifiable children;
- project corpus provenance is content-hashed;
- priority is executable and reproducible.

## F_gap

- five perturbation-policy choices remain genuinely open;
- conservation/regularity validation remains blocked by those choices;
- `D(z)`, `f(z)`, `f sigma8` and growth benchmark remain open;
- inference/model selection remain downstream;
- magneto-plasma and alphaXiv source/runtime gaps remain outside the current P0 path.

## F_next

Implement only `GROWTH-CS2-001` as a versioned candidate contract with explicit falsification tests.
Do not treat that candidate as a derived or universal RLL property.

SOURCE != CONFIG != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
