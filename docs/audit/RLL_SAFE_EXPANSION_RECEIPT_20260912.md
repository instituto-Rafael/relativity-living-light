# RLL Safe Expansion + Gap Decomposition V1 — append-only receipt

Date: 2026-09-12  
Authority: `instituto-Rafael/relativity-living-light`  
Base: `rll/lab`  
Claim allowed: **false**

## SOURCE

Directional source: **“AlphaXiv e RLL/rLLM: arquitetura, estado interno documentado, expansão segura e governança”**.

Transferable controls adopted:
- minimal delta;
- typed invariants;
- baseline;
- capability/effectiveness validation;
- read-only preflight;
- canary;
- robustness;
- controlled scale-up;
- rollback + receipt;
- `CONFIG_ACCEPTED != CONFIG_EFFECTIVE`;
- retrieval/ranking/report != primary scientific evidence.

External rLLM training state is **not** imported as RLL internal architecture.

Additional physics provenance for the first CMB child:
- PDG astrophysical constants: `Omega_gamma h^2 = 2.473e-5 (T/2.7255 K)^4`;
- relativistic-neutrino ratio derived from `(7/8)(4/11)^(4/3)`;
- standard-model `N_eff=3.044` reference is treated as an explicit assumption/default, not a fitted RLL result.

No third-party code was copied.

## ARTEFACT

Added:
1. `RLL_SAFE_EXPANSION_CONTRACT_V1.json`;
2. `RLL_GAP_DECOMPOSITION_V1.json`;
3. safe-expansion graph validator;
4. CI gate;
5. focused tests;
6. an additive radiation-density helper for the future `r_s(z*)` successor.

The radiation helper does **not** rewire the legacy or flat-closure likelihood.

## EXECUTION

At authoring time: `TOKEN_VAZIO_EXECUTION` until CI observes the exact PR head.

## EVIDENCE

The new tests are present but do not become PASS until executed in CI.

## CLAIM

`claim_allowed=false`.

The helper does not validate:
- recombination redshift prescription;
- baryon-photon sound speed;
- `r_s(z*)`;
- CMB acoustic likelihood;
- perturbation growth;
- model selection.

## Decomposition created

CMB:
`radiation -> z_star + c_s -> r_s(z*) -> CLASS/CAMB benchmark`.

Growth:
`perturbation contract -> D(z) -> f(z) -> f sigma8 -> CLASS/CAMB benchmark`.

Inference:
`CMB benchmark + growth benchmark -> multi-seed fit -> posterior/MCMC -> model selection`.

Magneto-plasma:
C09, C10, C11, C12 and C14 are now separate fail-closed gaps rather than one blended hypothesis.

Literature:
alphaXiv runtime schema, primary-source verification and per-source license/provenance are separate gates.

## F_ok

- external direction converted into RLL-native governance;
- gap graph is explicit and dependency-aware;
- first CMB dependency has an additive implementation;
- legacy paths remain untouched;
- claim boundary stays closed.

## F_gap

- CI evidence for this exact head;
- z_star contract;
- sound-speed implementation;
- r_s(z*) integral;
- CLASS/CAMB benchmark;
- growth perturbation contract and D(z);
- downstream inference;
- magneto-plasma formalization.

## F_next

After this gate passes, the next bounded scientific delta is:
1. `CMB-ZSTAR-001` source contract;
2. `CMB-CS-001` baryon-photon sound speed;
3. `CMB-RS-001` integral;
4. `CMB-BENCH-001` external benchmark.

SOURCE != CONFIG != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.


## DELTA 2 — CMB recombination children implemented, 2026-09-12

Additional artefacts:
- `src/rll/cosmology_recombination.py`;
- `tests/test_rll_cosmology_recombination.py`.

Implemented as bounded successor helpers:
1. Hu-Sugiyama approximate `z_star(omega_b h^2, omega_m h^2)`;
2. `R_b(a)=3 rho_b/(4 rho_gamma)`;
3. `c_s(a)=c/sqrt(3(1+R_b))`;
4. generic `r_s(z_star)` integral with caller-supplied `E(a)`;
5. flat-LCDM reference sanity path only.

External reference facts used for sanity:
- Planck/PDG-like `H0=67.4 km s^-1 Mpc^-1`;
- `Omega_m=0.315`;
- `omega_b=0.02237`;
- PDG `r_s(z_star)=144.43 Mpc`.

The implementation deliberately keeps:
- `class_camb_benchmark_complete=false`;
- `claim_allowed=false`;
- historical CMB path untouched;
- `r_d(z_drag) != r_s(z_star)`.

No code was copied from CAMB or the cited literature; equations were independently implemented from published formulae.

### DELTA 2 state

- CMB-ZSTAR-001: IMPLEMENTED_AWAITING_CI
- CMB-CS-001: IMPLEMENTED_AWAITING_CI
- CMB-RS-001: IMPLEMENTED_AWAITING_CI
- CMB-BENCH-001: REFERENCE_SANITY_BENCHMARK_AWAITING_CI

Full CLASS/CAMB equivalence remains TOKEN_VAZIO_BENCHMARK.
