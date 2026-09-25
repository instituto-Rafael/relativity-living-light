# μWRITE receipt — RLL Geometric Adaptive Feature Router V1 — rll/lab topology

μID: MU-RLL-GEOM-ADAPT-FEATURES-20260925-LAB  
date: 2026-09-25  
state: IMPLEMENTED_RLL_LAB_BRANCH_LOCAL_LOGIC_PASS_PROVIDER_CI_PENDING  
claim_allowed: false  
parent: MU-RLL-GEOM-ADAPT-FEATURES-20260925  
supersedes_route: PR#986 main-target route (invalid branch transition)  
authority: instituto-Rafael/relativity-living-light  
branch: research/geometric-adaptive-feature-router-v1-20260925-lab  
base: rll/lab

## Delta

Re-materialized the additive geometry feature adapter on the repository's allowed WORK -> rll/lab topology after Branch Maturity Gate V2 rejected the first PR target with INVALID_BRANCH_TRANSITION.

Files/commits:
- rx/geometric_features.py @ b669c4d4c31e81babd862b7c838c642c0b8a43ea
- data/governance/RLL_GEOMETRIC_ADAPTIVE_FEATURE_ROUTER_V1.json @ 46611452159769edff03cf7fbb9aca85fbd6a26d
- tests/test_geometric_adaptive_feature_router.py @ 087964d5f41465fedf0180ff96ca73870ce43681
- docs/science/RLL_GEOMETRIC_ADAPTIVE_FEATURE_ROUTER_V1.md @ 1c857199106317b491e63718a75850eb978164c2
- data/governance/RLL_GEOMETRIC_ADAPTIVE_FORMULA_BINDINGS_V1.json @ 2f47a942f911c23e5c168d0275b18640f7f19cd4

## Scope

Exact diagnostic families:
- concentric circles / annuli;
- spherical shells;
- circle inversion;
- orthographic circle->ellipse projection;
- regular-polygon normalized descriptors and diagonal recurrence;
- complex-plane rotation, multiply/divide/root phase operations.

Allowed adaptation:
- numerical resolution;
- synthetic fixture density;
- diagnostic router priority.

Blocked adaptation:
- H0;
- Omega_m;
- Omega_s0;
- w0/wa;
- physical constants;
- equation-of-motion parameters.

## Evidence

Local logic check before GitHub materialization:
- annulus q=1/2 -> annulus fraction 3/4 PASS
- spherical shell q=1/2 -> shell fraction 7/8 PASS
- inversion r=3,a=2 -> rr'=4 PASS
- projection i=60deg -> b/a=1/2 and identity residual ~0 PASS
- hexagon r/R=sqrt(3)/2 and lambda=sqrt(3) PASS
- diagonal recurrence -> [1,sqrt(3),2] PASS
- complex polar multiply/divide/root identities PASS
- fail-closed adaptive numerical policy PASS

Provider exact-head CI: TOKEN_VAZIO_PENDING_PR_EXECUTION.

## Boundary

adaptive_numerics != adaptive_physics  
geometry_feature != cosmological_parameter  
geometry_fit != causal_explanation  
pi/phi/root occurrence != new_physics  
post_hoc_feature_mining != confirmatory_test

F_gap: provider CI, independent replay, preregistered G6 residual mapping, any G5 physical derivation.  
F_next: open draft PR to rll/lab -> exact-head CI -> synthetic hidden-truth routing benchmark -> preregistered G6 residual feature.  
rollback: close/revert only additive lab branch/PR; preserve both receipts and invalid-transition evidence.
