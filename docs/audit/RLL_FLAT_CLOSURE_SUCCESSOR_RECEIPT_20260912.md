# RLL Flat-Closure Successor V1 — append-only receipt

Date: 2026-09-12  
Target authority: `instituto-Rafael/relativity-living-light` / `rll/lab`  
Change type: additive scientific successor; historical outputs preserved  
Claim allowed: **false**

## SOURCE

PR #878 established that the legacy joint optimizer fits `Om` and `OL` independently without `Ok`, so its bounds admit `E(0) != 1`. The same gate records two separate unresolved items: the growth-index `f sigma8` proxy lacks validated `D(z)`, and the compressed-CMB acoustic scale uses `r_d` where `r_s(z*)` is required.

## ARTEFACT

This successor adds a flat-closure parameterization rather than rewriting the legacy path.

- Standard backgrounds: `Omega_Lambda = 1 - Omega_r - Omega_m`.
- RLL: `Omega_Lambda = 1 - Omega_r - Omega_m - Omega_s0`.
- `OL` is therefore derived, not counted as a fitted parameter in the successor.
- Historical output stem `joint_real_likelihood` is explicitly rejected by the successor.

## EXECUTION

At authoring time: **TOKEN_VAZIO_EXECUTION** until CI observes the branch/PR.

## EVIDENCE

The focused tests sample lower/mid/upper optimizer bounds and require `E(0)^2=1` for LCDM, wCDM, CPL and RLL. This is evidence of the closure contract only.

## CLAIM

`claim_allowed=false`.

Closure readiness must not be promoted into growth, CMB, posterior or model-selection validation.

## F_ok

- flat closure is implemented additively;
- historical pipeline and historical artifacts are preserved;
- variable contract now distinguishes fitted, derived, proxy and missing quantities;
- `r_s(z*)` and `D(z)` are explicit TOKEN_VAZIO implementations rather than implicit omissions.

## F_gap

- validated recombination sound horizon `r_s(z*)`;
- validated perturbation/growth treatment `D(z)` and `f sigma8`;
- robust successor execution and posterior/model-selection comparison.

## F_next

Run CI on the exact successor head. If closure tests pass, keep the global model-selection gate closed and implement the CMB `r_s(z*)` gate next as a separately benchmarked, reversible change.

SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
