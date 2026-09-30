# 10 — Evidence and Results Route

Status: `PRESENTATION_INDEX`  
Claim gate: `claim_allowed=false`

## Primary quantitative route

- Machine-readable result: `results/structure_d/joint_real_likelihood.json`
- Tabular result: `results/structure_d/joint_real_likelihood.csv`
- Human explanation: `results/structure_d/joint_real_likelihood_readme.md`
- Current paper table: `docs/RLL_CURRENT_RESULTS_PAPER_TABLE.md`
- RLL vs CPL diagnostic: `docs/RLL_VS_CPL_DIAGNOSTIC.md`
- Robust-fit next plan: `docs/RLL_NEXT_ROBUST_FIT_PLAN.md`
- Missing-calculation ledger: `docs/RLL_MISSING_CALCULATIONS_LEDGER.md`

## What is worth presenting first

Present the comparison pipeline before the theory-wide narrative:

```text
real inputs
→ same likelihood route
→ LCDM / wCDM / CPL / RLL
→ chi2 / AIC / AICc / BIC
→ claim gate
→ gaps / next falsifier
```

That order lets a reviewer distinguish implemented computation from interpretation.

## Known boundary

The repository records an effective `N=64` comparison artifact and explicitly treats the current run as preliminary rather than final inference. Strong claims remain blocked until robust multi-seed fits, fuller covariance/likelihood treatment and independent reproduction are available.

## Presentation invariant

Do not copy a number into slides or Pages without also linking:

1. the exact result artifact;
2. the generating code/workflow;
3. the commit/receipt when available;
4. the claim boundary.
