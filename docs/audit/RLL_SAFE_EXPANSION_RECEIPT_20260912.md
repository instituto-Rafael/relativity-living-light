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
