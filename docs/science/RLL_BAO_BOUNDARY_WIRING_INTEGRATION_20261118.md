# RAFAELIA Ω — Fonte única BAO G4 com diagnóstico de fronteira integrado (2026-11-18)

State: SOURCE_COMMITTED, PROVIDER_CI_NOT_YET_CHECKED, claim_allowed=false.

**Authority and provenance**
- RLL rll/lab base commit f83f6173cb98fc785935da35afe4b31c609f1744; consumer originates PR #1235 at d4d17923f417726b69cda0bf8c01afb283887520; diagnostics originate PR #1237 at 2c21ed2699015b499ac3614a705b55a7dd9fffe8.
- Source inputs are loaded exclusively through tools/run_g4_background_tournament.py::load_desi() with a verified Lyman-α (DH,DM to DM,DH) covariance permutation. No observed inputs were copied.
- The integration combines the seven source, schema, tests and historical documentation files into one lab-based DRAFT/HOLD candidate. The two antecedent PRs remain preserved, not merged.

**Scientific boundary**
For the corrected 13-observable BAO-only fit (χ² RLL ~7.804), `results.RLL.boundary_diagnostics` is measured fresh from that exact `scipy.optimize.least_squares` OptimizeResult. This is not the outdated unpermuted-covariance χ²=6.4742 and min_grad_inf=17.054689.

- `min_grad_inf = norm(res.grad, infinity)`: unprojected gradient norm. It is not `norm(res.jac, infinity)`.
- `optimizer_optimality=res.optimality` and `kkt_violation_inf` are separate bounded-optimum diagnostics.
- `corner_solution` means any active bound by protocol convention, `strict_corner` means two or more. A constrained optimum on one bound need not be a numerical failure.
- Bound distances preserve finite positive near-bound distances; threshold is 1e-8 of each parameter bound width.
- `n_residual_dof_nominal=13-k`. `n_effective_dof=null` with typed unknown `TOKEN_VAZIO_NOT_ESTIMATED`; nominal count is not a measured effective count.
- Each model JSON row stores diagnostics. The convenience `results` dictionary exposes `results.RLL.min_grad_inf` and `results.RLL.boundary_diagnostics`; `rendered_table` adds an asterisk to boundary χ² and mandatory footnote.
- `claim_allowed=false` always, even for an interior optimum: this is an experimental fit, not scientific confirmation.
- Raw optimizer gradients refer to 96 quadrature nodes; χ² displayed is verified at 192 nodes. Never silently treat these as identical derivatives.

**Falsifiers and rollback**
- Synthetic known-boundary cases, KKT sign and invalid-value tests in tests/test_bao_boundary_gate_v1.py.
- BAO 13×13 reference regression and source-order permutation in tests/test_bao_only_g4_v1.py. New assertions require current RLL w_t active and Ωm not active, `7.8040*` marker, typified effective dof, unchanged model χ² anchors and no positive claim.
- Re-optimizing with changed Ωm/w_t bounds is explicitly NOT_RUN; any Δχ² is sensitivity, not automatic significance. MCMC/nested/CMB/perturbations/linear growth are not implied.
- Before merge require exact-head Python tests and schema gate, reviewer check and explicit human authorization. This branch may be safely abandoned; main and lab stay unchanged, no history deletion.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM. IMPLEMENTED_UNTESTED != PASS.
