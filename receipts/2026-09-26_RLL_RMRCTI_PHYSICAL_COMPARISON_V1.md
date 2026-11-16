# μWRITE — RMRCTI calibration × DESI physical comparison — 2026-09-26

μID: MU-RLL-RMRCTI-PHYSICAL-COMPARISON-20260926-V1  
kind: REAL_DATA_COMPARISON+NEGATIVE_BINDING_RESULT  
claim_allowed: false

## Provenance

- source data: `data/real/cosmology/desi_dr2_bao_primary_points.csv`;
- source predictions: `results/RLL_G4_DESI_GEOMETRY_LCDM_RLL_REPRODUCTION_V1.json`;
- calibration bridge: `data/governance/RLL_RMRCTI_DELTA_P_CALIBRATION_BRIDGE_V1.json`;
- executor: `tools/rll_rmrcti_physical_comparison_v1.py`.

## Observed result

- DESI observables: 13;
- anisotropic DM/DH pairs: 6;
- LCDM standardized residual RMS: 0.943563073605141;
- RLL standardized residual RMS: 0.943563074464895;
- max |single residual|: ~1.801493 sigma;
- block-summary chi2: LCDM 10.873115645602892; RLL 10.87311567736063;
- G4 full-covariance chi2: LCDM 11.770259180500712; RLL 11.77025905554635;
- cross-model max absolute prediction delta: 6.541668540194223e-9;
- RLL recorded null boundary: Omega_s0=0.
- committed joint real 64-observation recomparison: χ² LCDM=93.95354560099567, RLL=93.95983068903539, Δχ²=+0.006285088039717834, ΔAIC=+6.006285088039718, ΔBIC=+12.482934338118739;
- joint blocks: H(z), DESI DR2 BAO, fσ8, CMB shift; this is artifact recomparison, not a fresh refit.

## Negative evidence

No physically derived mapping exists from DESI observables to RMRCTI `stable_any` / `peak`.

Therefore `DeltaP` is not computed on DESI. A post-hoc residual threshold would be an invented bridge and is forbidden.

## Rollback

Revert only the additive bridge/executor/tests/result/docs. Preserve the underlying DESI/G4 artifacts and the negative binding result.
