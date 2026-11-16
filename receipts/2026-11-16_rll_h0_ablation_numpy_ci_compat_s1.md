# H0/r_d ablation Python dependency-closure hotfix S1 — 2026-11-16

- mu_id: MU-RLL-H0ABLATION-NUMPY1-S1-20261116
- source: PR #1222, failed exact-head job https://github.com/instituto-Rafael/relativity-living-light/actions/runs/43824795233/job/133155947456
- parent_lab: 5ba4120cf62e89ec0d7a7562673fd58172c055ed
- traceback: pandas 3.1.1 requires numpy>=2.0.2; workflow intentionally pins NumPy 1.x for CAMB1.6.6. Python import error before scientific test collection.
- proposed_delta: bound pandas>=2,<3, astropy>=5.3,<8 and contourpy>=1.0,<1.4 consistently with NumPy>=1.26,<2; keep exact CAMB1.6.6. Require pip check to catch remaining interpreter-level conflicts before any numerical test runs.
- files:
  - .github/workflows/h0-rd-ablation.yml: 9a24e5ea6b6189f152dc742256c3cc3b7bcdb002
  - tests/test_h0_rd_ablation_ci_compat.py: d4f8536e1a9d9a75ce2d283172e75c2b813e2bd3
- negative scope: no modifications to numerical implementation, datasets, physical claims, fitter outputs, optimizer or tests beyond static dependency regressions.
- status: IMPLEMENTED_UNTESTED; exact-head GitHub CI required; claim_allowed=false.
- rollback: reviewed successor/revert; keep parent exact.
