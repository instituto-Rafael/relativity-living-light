# RLL G4 background — conditional local CPL slope and phantom-closure preregistration

2026-11-18; DRAFT/HOLD, claim_allowed=false. Exact G4 authority:
`tools/run_g4_background_tournament.py::e2`, base `rll/lab@f83f6173cb98fc785935da35afe4b31c609f1744`.
Predecessor RLL scientific-critical source:
`docs/research/RLL_EXTERNAL_CRITICAL_METHODS_REVIEW_20261114_S1.md` (currently on main; not copied).

## Hypotheses, actual mathematical domain and falsifiers

For the G4 RLL `E²` and a **separately conserved effective dark sector**
\[
g(z)=\Omega_\Lambda+\Omega_{s0}[f(z)+(1-f(z))(1+z)^3], \quad
f(z)=1/[1+\exp((z-z_t)/w_t)],
\]
with Ωs0 >= 0, w_t>0 and ΩΛ>=0, one gets
\[
w_{\mathrm{eff}}=-1+\frac{1+z}{3g}\,\frac{dg}{dz},\quad
w_{0,\mathrm{eff}}=-1+\frac{\Omega_{s0}(1-f_0)}{G},\quad
G=\Omega_\Lambda+\Omega_{s0},
\]
\[
w_{a,\mathrm{cons}}=
 \frac{\Omega_{s0}(1-f_0)}{G^2}\left[
 \frac{2 f_0 G}{w_t}+3(\Omega_\Lambda+\Omega_{s0}f_0)\right]\ge0.
\]
This is the *z=0 tangent*, not a global CPL fit and NOT the separate documented-pressure formula (which has a factor **1** instead of **2** before \(f_0G/w_t\)). Mistaking one for the other is a sign-source mismatch.

The tests calculate local finite-difference gradients directly from actual G4 `e2`, subtracting matter/radiation using the G4 source `OMEGA_R0`. They verify the analytic tangent for representative priors, the LCDM null case, and reject malformed domains. This is a **background mathematical sign gate**, not a matched-data DESI+CMB+Pantheon posterior or a proof of physical NEC.

### Scientific observation and limitation (2026)
DESI DR2 + selected CMB/SNe combinations favor CPL \(w_0>-1,w_a<0\) at a dataset-dependent significance, but cosmological Bayes factors may be inconclusive. See DOI:10.1093/mnras/stag1607 (2026-08-26) and DOI:10.1088/1475-7516/2026/08/004.
This conditional \(w_{a,\mathrm{cons}}\ge0\) is a **structural difference** worth falsifying; it does not by itself establish an excluded physical model without joint likelihood, priors and matched observables.

The repo already has `scripts/check_rll_growth.py` with a GR smooth-dark-sector linear growth **approximation** and real fσ8 CSV, but it lacks a demonstrated perturbative completion of the RLL logistic sector. Do not claim fσ8/S8 from this preflight, or assume modified gravity. An effective \(w=-1\) crossing is not proof of a pathology without a specified perturbation closure. The separately documented pressure has a continuity-residual failure, which is not silently repaired here.

### Gates and scope
- Tests `tests/test_g4_rll_effective_wa_v1.py` must pass exact HEAD; original G4 physics/data inputs remain unchanged.
- Report tagged `BACKGROUND_ANALYTIC_ONLY`, `perturbation_closure=TOKEN_VAZIO_NOT_DERIVED`, `observational_wa_posterior=TOKEN_VAZIO_NOT_FITTED_TO_MATCHED_CMB_SN_BAO`, `claim_allowed=false`.
- Later independent falsifier: joint fit including CPL and RLL under *same* DESI+CMB+SNe selection, followed by growth (with a physically specified perturbation sector). No arbitrary S8 target substituted for a likelihood.
- Do not alter `main`/`rll/lab`, merge, license, protect rules, model bounds or pressure prescription. Corrective successor and rollback via unmerged PR.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.
