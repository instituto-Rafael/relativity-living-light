# μWRITE receipt — RLL Geometric Adaptive Feature Router V1

μID: MU-RLL-GEOM-ADAPT-FEATURES-20260925  
date: 2026-09-25  
state: IMPLEMENTED_BRANCH_LOCAL_LOGIC_PASS_PROVIDER_CI_PENDING  
claim_allowed: false  
parent: RLL_DYNAMIC_STRUCTURAL_GEOMETRY_CONTEXT_V1

## Delta

Implemented an exact, standard-library geometry feature layer for:
- inner/outer circles and annuli;
- spherical shell ratios;
- circle inversion;
- orthographic projection;
- regular-polygon compactness/radius/diagonal descriptors;
- complex-plane rotation, multiplication, division and roots;
- fail-closed adaptive numerical policy.

Allowed adaptation:
- numerical resolution;
- synthetic fixture density;
- diagnostic-router priority.

Blocked adaptation:
- H0;
- Omega_m;
- Omega_s0;
- w0/wa;
- physical constants;
- equation-of-motion parameters.

## Evidence

Branch: `research/geometric-adaptive-feature-router-v1-20260925`

Commits:
- geometric feature implementation: `3c70ef573c4e7b82b4a91df628e7f1e782e6baad`
- governance contract: `1b7e43681e201c9f0d77398469642610778ccccc`
- tests: `3e42ef6f4067911dcfc4076d46debf2d0ba3832e`

Local logic checks before repository materialization:
- annulus q=1/2 -> area fraction 3/4: PASS
- spherical shell q=1/2 -> volume fraction 7/8: PASS
- inversion r=3,a=2 -> rr'=4: PASS
- projection i=60deg -> b/a=1/2 and unit identity residual ~0: PASS
- hexagon -> r/R=sqrt(3)/2, lambda=sqrt(3): PASS
- hexagon diagonal recurrence -> [1,sqrt(3),2]: PASS
- complex polar multiply/divide/root identities: PASS
- numerical-adaptation policy keeps claim_allowed=false and blocks physical parameters: PASS

Provider CI: TOKEN_VAZIO_PENDING_PR_EXECUTION.

## Scientific boundary

This adapter does not modify the Friedmann background, RLL likelihood, cosmological parameter values or physical claims. It supplies typed geometry descriptors and bounded numerical-routing suggestions only.

F_gap: provider CI; independent rerun; predeclared G6 observable mapping; any G5 physical bridge.  
F_next: open draft PR -> observe exact-head CI -> synthetic hidden-truth benchmark -> predeclared G6 residual test.  
rollback: remove this additive adapter branch/files; preserve receipt/history.
