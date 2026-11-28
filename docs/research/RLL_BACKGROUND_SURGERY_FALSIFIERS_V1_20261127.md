# RLL BG surgery V1 — operational successor and falsification matrix

State: REMOTE_WRITTEN / LOCAL_PASS_SCOPED / INDEPENDENT_SCAN / claim_allowed=false.
Predecessor: [initial design](RLL_BACKGROUND_REFORM_V1_20261127.md). The initial design's NOT_RUN labels describe its historical local stage, not this successor.
Receipt: [RLL_BG_SURGERY_V1](../../receipts/RLL_BG_SURGERY_V1_20261127.json).
Existing G4 (`tools/run_g4_background_tournament.py`) remains the canonical six-model combined background route. It already filters the 5 BAO-labelled H(z) rows, uses the DESI order guard, Pantheon+ STAT+SYS and profiled M_B. Its rd approximation and diagonal CC errors remain separate scientific assumptions. The new adapter is a free-rd sensitivity/holdout diagnostic, not a replacement for G4. GEDE/IDE remain mandatory comparators in G4, not represented in the four-model diagnostic.

## Mathematical cross-cut: identifiability before preference

For x=(1+z)^3, the RLL background equation without radiation is exactly
E² = 1 + [Omega_m + Omega_s0(1-f)](x-1).
At fixed Omega_s0=0, z_t and w_t are unidentifiable: their derivatives vanish identically. In the saturated f->0 regime the Omega_m and Omega_s0 derivatives coalesce; f->1 removes sensitivity to Omega_s0. These are mathematical degeneracies, not new physical claims. A nominal improvement in chi² cannot establish a new sector; the null is on a boundary and conventional Wilks assumptions are not automatic.
BAO predictions have the factor c/(H0 rd); the analytic profile eliminates this scale from the nonlinear search at a fixed arbitrary H0 pivot. For y=observations, t=unit-scale prediction and covariance C, the unconstrained profile is A=(t^T C^-1 y)/(t^T C^-1 t), projected to the declared scale bounds. No independent H0 or rd inferred.

## Predeclared falsification matrix (future executions)

| Layer | Negative control | Exit evidence / disposition |
|---|---|---|
| Algebra | Exact LambdaCDM null, saturation and derivative limits | independent formula and finite differences; reject mismatched code |
| Numerics | integration resolution doubling, independent quadrature, optimization seed and bound widening | record convergence, rank and condition number; boundary-limited solution remains provisional |
| Data | source order, SPD, wrong axis, duplicate row, cross covariance, release substitution | fail closed on invalid inputs; Ly-alpha AP replaces overlapping BAO only with joint covariance |
| Inference | synthetic LCDM null recovery and false-discovery distribution of max improvement across all prespecified alternatives | freeze search family, simulated covariance and threshold before mock runs; no naive chi-square conversion |
| Generalization | remove Ly-alpha / CC / SN / entire tracer groups, refit only on train | predictive distribution incl. parameter uncertainty; report conditional likelihood if cross covariance nonzero |
| Calibration | Pantheon+, Dovekie, Union separately, calibrated vs uncalibrated SN; CC stellar-population systematics | no post-data selection, no independent claim for shared calibrators |
| Physics | conserved C and interacting I closures, stability, gauge and initial conditions, GR null | retain F as background only; no f_sigma8/S8/Cl substitute |
| Early universe | rd computed separately from rs(z*) under consistent radiation/baryon/recombination physics | full TT/TE/EE/lensing and CLASS/CAMB comparison; compressed prior not proof |
| Software | Python/C11 equivalence, clean checkout, exact-head regression, negative tests, rollback | no merge/release without governed promotion and independent evidence |

The independent scan in the receipt used DESI DR2 Table-IV rounded means and the repository-bound native covariance. It is exploratory because the candidate parameter ranges and split were chosen after the dataset existed. CPL reaches w0=-0.3, RLL reaches wt=0.05 and scan iteration limit; both have start sensitivity. The next run must be frozen before additional data and use proper predictive distributions. No conclusion of falsification of a whole model family or superiority from the scan.

## Route
`python -m unittest discover -s tests -p 'test_background*py' -v`
`python -m data.pipelines.structure_d.background_scale_profile_v1 --output /tmp/rll_bg_profile_v1.json`
Run existing G4 with its documented command separately; never overwrite earlier result stems. No new workflow, rule, merge or release was created. Rollback is non-promotion or a reviewed successor.
