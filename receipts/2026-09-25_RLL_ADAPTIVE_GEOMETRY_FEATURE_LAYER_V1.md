# μWRITE receipt — RLL Adaptive Geometry Feature Layer V1 — 2026-09-25

μID: MU-RLL-ADAPTIVE-GEOMETRY-20260925  
kind: SCIENTIFIC_BRIDGE / DIAGNOSTIC_FEATURE_LAYER / LOCAL_REPRODUCED  
source/ref:
- current geometry session 2026-09-25
- docs/science/RLL_DYNAMIC_STRUCTURAL_GEOMETRY_CONTEXT_V1.md
- results/RLL_DESI_SYNTHETIC_GEOMETRY_EMBEDDING_V1.json
parent: RLL_DYNAMIC_STRUCTURAL_GEOMETRY_CONTEXT_V1

Δsummary:
- geometry imported into RLL only as fail-closed diagnostic/reparameterization features;
- existing DESI geometry proxies reduced to two independent coordinates: log-scale and log-anisotropy;
- covariance ellipse + Mahalanobis diagnostics added;
- G0/G1 local curve curvature/torsion diagnostics added;
- G2/G3 metric adapter remains blocked/TOKEN_VAZIO;
- no cosmological equation, likelihood, or physical parameter changed.

implementation commits:
- rx/adaptive_geometry.py: 9de20225474410bb2b9b85b0030cc0630e9ec4f7
- tests/test_adaptive_geometry.py: 1db5bf8b93a7752ed4d7404c1a4455fedb2f1276
- data/governance/RLL_ADAPTIVE_GEOMETRY_FEATURE_LAYER_V1.json: 7b413ff3cc4c5350b5d58e5ad9fa15d076109c4a
- docs/science/RLL_ADAPTIVE_GEOMETRY_FEATURE_LAYER_V1.md: 6b477244b736969696eb07c3b983b881c37868de
- results/RLL_ADAPTIVE_GEOMETRY_FEATURE_LAYER_V1.json: 32000d6afd76e4265af4f43ef59ac377ab9ee7b5

readback blobs:
- rx/adaptive_geometry.py: 3a1ebc1b7ac723be2cab26daa16185d2013d6f62
- tests/test_adaptive_geometry.py: daa9bd1d3c76fbe95d35e0352f36faf0ba6d0097
- contract: a4bc8cc18f7ea3f9e668db41dfa8bbc756c408cf
- docs: c23630034b7167b5f78d11e1b3c358d6ddd856b3
- result: f7e6526c8e471f3c9ea3c0b0b2f43de52a959c53

local_precommit_evidence:
- status: PASS
- module_sha256: dc2f86247c2a329f21fe61f15ee61157f5d1dd20c6d74fbfa632c91516fdf1cc
- test_sha256: 069d9ab22ea796e6063f38a7d4880642fbd9b1024487bb5c709309b8549d4f1b
- third_party_python_dependencies: 0

observed derived identities:
- phi = atan(F_AP) for positive DM/rd,DH/rd
- q = min(F_AP,1/F_AP)
- A_ellipse = 2*pi*A_triangle
- rho^2 = (x*y)(F_AP+1/F_AP)

null control:
- recorded RLL G4 boundary: Omega_s0=0
- max_abs_delta_log_scale_RLL_minus_LCDM = 2.3896840062320734e-10
- max_abs_delta_anisotropy_RLL_minus_LCDM = 1.4148571203520532e-10
- interpretation: consistency/null parity only; not evidence favoring RLL

Papers:
- rafaelmeloreisnovo/papers/papers/rll_adaptive_geometry_observable_space_v1/paper.md
  commit 98665b3abe94142d5821c32f1bd50b25c339ea70
  blob 03de342547e9fa6d227fa2f701605dd4de58392c
- provenance.md commit 751ae369ff605b536f63f263f430b39fbfb2d37c
- claims.jsonl commit f3783ccdb8ca4eb6535f9ba97b76cf4e2f35d68f

boundary:
- geometry feature != physical mechanism
- reparameterization != independent evidence
- adaptive sampling != adaptive scientific truth
- prior/likelihood density changes require explicit contract/Jacobian accounting
- G2/G3 raw Euclidean curvature forbidden without metric/tetrad adapter
- claim_allowed=false

gap:
- provider CI / independent reproduction
- full DESI covariance binding for the 2D observable pairs
- old-vs-adaptive same-likelihood benchmark
- metric-specific G2/G3 curve invariants

next:
- benchmark scale/anisotropy coordinates against the current likelihood with identical target density;
- compare conditioning, ESS/runtime and posterior parity;
- use curvature/torsion only in the synthetic hidden-truth body-Y event-chain experiment before any real-data event claim.

rollback: append-only successor receipt; no destructive rewrite
