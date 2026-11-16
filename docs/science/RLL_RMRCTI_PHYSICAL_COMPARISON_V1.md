# RLL — RMRCTI ΔP Calibration × Real DESI DR2 Physical Comparison V1

**Date:** 2026-09-26  
**State:** `REAL_DATA_COMPARISON / DIRECT_DELTA_P_BINDING_BLOCKED`  
**claim_allowed:** `false`

## Sources

- DESI DR2 BAO primary 13-vector in `data/real/cosmology/desi_dr2_bao_primary_points.csv`;
- G4 source-preserving LCDM/RLL predictions in `results/RLL_G4_DESI_GEOMETRY_LCDM_RLL_REPRODUCTION_V1.json`;
- synthetic CI calibration pointer in `RLL_RMRCTI_DELTA_P_CALIBRATION_BRIDGE_V1.json`.

## Real-data result

For the 13 committed DESI DR2 BAO observables, the per-observable standardized residual RMS is:

[
RMS_z(Lambda CDM)=0.9435630736,
qquad
RMS_z(RLL)=0.9435630745.
]

The largest single absolute standardized residual is about (1.8015sigma).

Using only the six published within-pair correlations plus BGS gives:

[
chi^2_{block}(Lambda CDM)=10.87311565,
]

[
chi^2_{block}(RLL)=10.87311568.
]

The already-recorded G4 full-covariance recomputation is:

[
chi^2_{full}(Lambda CDM)=11.77025918,
]

[
chi^2_{full}(RLL)=11.77025906.
]

Therefore the block-summary approximation is deliberately **not** relabeled as full covariance. The missing cross-block contribution is about (0.89714) in this comparison.

## Geometry coordinates

For each of the six anisotropic DESI pairs the executable derives only the invertible coordinates

[
s=	frac12ln[(D_M/r_d)(D_H/r_d)],
qquad
a=ln[(D_M/r_d)/(D_H/r_d)].
]

They are diagnostics/reparameterizations, not new physics.

## Cross-model finding

At the recorded G4 best fit:

[
Omega_{s0}=0.
]

The maximum absolute RLL-minus-LCDM prediction difference over the DESI vector is

[
6.54	imes10^{-9},
]

with maximum relative difference

[
3.10	imes10^{-10}.
]

So this particular physical-data state supplies a **negative discrimination result**: the recorded RLL point lies on its LCDM null submanifold.


## Joint real 64-observation cross-check

The same executor now also re-compares the committed joint real-likelihood artifact
`results/structure_d/joint_real_likelihood.json`, which contains 64 observations
across H(z), DESI DR2 BAO, fσ8 and the compressed CMB-shift block.

The committed totals are:

\[
\chi^2_{\Lambda CDM}=93.95354560099567,
\qquad
\chi^2_{RLL}=93.95983068903539,
\]

so

\[
\Delta\chi^2_{RLL-\Lambda CDM}=+0.006285088039717834.
\]

The information-criterion differences recorded by that same artifact are

\[
\Delta AIC=+6.006285088039718,
\qquad
\Delta BIC=+12.482934338118739.
\]

The per-block χ² deltas are:

- H(z): +0.01743377936652113;
- DESI DR2 BAO: +0.12780720215373687;
- fσ8: -0.007981146950073458;
- CMB shift: -0.13097474653047256.

These nearly cancel in χ², while RLL still pays the extra-parameter penalty in
AIC/BIC. The RLL row again has `Omega_s0=0.0`.

This is a recomparison of a committed real-data artifact, not a fresh refit.

## Why ΔP is not computed on DESI

DESI rows do not define the RMRCTI fields `stable_any` and `peak`. Creating those labels from residual sign, threshold or geometry after seeing the data would be a post-hoc mapping.

Therefore:

[
oxed{DIRECT_DELTA P_ON_DESI=BLOCKED}
]

until an independently derived physical mapping exists.

## R3

**F_ok:** real DESI comparison executed from committed data; 13 observables and six anisotropic geometry pairs bound; block-vs-full covariance distinction measured; RLL/LCDM null-submanifold equivalence reproduced.

**F_gap:** a physical derivation of RMRCTI stable/peak semantics; independent real RMRCTI traces; serial-dependence-aware threshold calibration.

**F_next:** if a physical stable/peak mapping is ever derived before looking at outcomes, preregister it and run it as a separate falsifier. Otherwise keep ΔP as an engineering/statistical diagnostic.
