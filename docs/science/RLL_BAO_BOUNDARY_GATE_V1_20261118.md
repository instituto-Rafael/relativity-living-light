# RLL BAO · Boundary diagnostic gate V1 · preregistered review-only

Date: 2026-11-18. Producer: instituto-Rafael/relativity-living-light.
Authority: rll/lab. Branch: work/rll-bao-boundary-diagnostic-v1-20261118.
Scientific claim: NONE. claim_allowed=false.

## Intended consumer and explicit dependency
The BAO-only runner currently lives in unmerged PR #1235, commit d4d17923f417726b69cda0bf8c01afb283887520.
This PR introduces ONLY an independent reusable module, JSON schema, and tests against real SciPy OptimizeResult objects.
It does NOT yet modify the BAO-only runner or its RESULTS.RLL output: WIRING=NOT_RUN.
Integrate after #1235 and this PR are reviewed in a separately scoped follow-up.
Neither Pantheon+ nor LCDM/RLL physics, input arrays, priors, optimizer, chi2 or AICc/BIC are changed.

## Interpretation and falsification
- The user's historical chi2=6.4742 and two lower bounds belong to a pre-permutation covariance run.
  The current source-bound correction has chi2=7.803973727991534, Omega_m about 0.134 and w_t=0.05.
  Never transfer a historical min_grad_inf=17.054689 into a new JSON without remeasurement.
- SciPy least_squares: res.jac is the residual Jacobian, NOT the gradient.
  min_grad_inf in this schema is explicitly norm(res.grad, infinity); the
  separate optimizer_optimality is the scaled solver first-order measure.
- One active bound gives corner_solution=true as the versioned protocol alias;
  strict_corner=true requires two or more active bounds. An active bound does NOT prove
  an incorrect mathematical optimum: monitor KKT sign and solver optimality.
- Distance-to-bound is not silently rounded to exactly 0: a near-bound detection
  can have a positive raw distance. Tolerance uses distance relative to bound width
  with rtol=0, not the default np.isclose rtol.
- Nominal residual dof = 13 - 5 = 8 for BAO RLL; effective dof is NULL with
  TOKEN_VAZIO_NOT_ESTIMATED until an appropriate model-specific estimate.
- Any boundary_solution must keep claim_allowed=false and a reason containing
  'corner'. Render chi2 with an asterisk and explicit footnote, never bold a
  corner chi2 as an unconditional winner.
- Synthetic negative controls: true lower-bound optimum with positive raw gradient
  and small KKT violation; strict two-bound corner; interior solution; mutated
  claim_allowed=true must raise; inconsistent corner flag must raise.
- The current model-selection AICc/BIC results are *not altered* by this gate.
  If prior-restriction sensitivity fit changes chi2 by 1 or 4, that is descriptive
  sensitivity, NOT an automatic chi-square significance test or falsification.

## Acceptance and rollback
Reproduce local: python -m pytest -q tests/test_bao_boundary_gate_v1.py
CI required on exact head before any promotion; integration in PR #1235 is separate,
and must emit schema-bound diagnostics for each model. No overwriting historical receipts.
Rollback: leave DRAFT/HOLD unmerged, append successor corrections, preserve main/lab.
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.
