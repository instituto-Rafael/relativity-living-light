# RLL CMB r_s(z*) ↔ CAMB Benchmark V1 — append-only receipt

Date: 2026-09-12
Authority: `instituto-Rafael/relativity-living-light`
Base: `rll/lab`
Claim allowed: **false**

## SOURCE

Repository-local predecessors:
- `src/rll/cosmology_radiation.py`;
- `src/rll/cosmology_recombination.py`;
- `scripts/crosscheck_class_camb_baselines.py`;
- `.github/workflows/class-camb-baseline-crosscheck.yml`;
- `data/governance/RLL_GAP_DECOMPOSITION_V1.json`.

External computational authority:
- CAMB runtime installed by the existing CLASS/CAMB baseline workflow.
- CAMB `get_derived_params()` is used for `zstar` and `rstar`.
- No CAMB source code is copied into RLL.

## PURPOSE

Close the highest-value bounded gap:
`CMB-BENCH-001`.

The benchmark separates:
1. `z_star` fit error;
2. `r_s` error evaluated at the RLL fitted `z_star`;
3. `r_s` error evaluated at CAMB `zstar`.

This decomposition prevents one residual from being misattributed to another layer.

## CASES

Three pinned flat-LCDM background cases:
- baseline;
- lower_background;
- upper_background.

Massive neutrinos are disabled in this bounded reference comparison.
`T_CMB=2.7255 K` and `N_eff=3.044` follow the existing RLL radiation contract.

## GATES

Predeclared relative tolerances:
- `zstar`: 1%;
- `rstar` using RLL fitted `zstar`: 1%;
- `rstar` using CAMB `zstar`: 0.5%.

## EXECUTION

At authoring time:
`TOKEN_VAZIO_EXECUTION_EXACT_HEAD`.

No status becomes PASS before CI observes the exact PR head.

## NON-REGRESSION

- no historical likelihood is modified;
- no `r_d` output is renamed as `r_s`;
- no growth or perturbation implementation is added here;
- no claim is promoted;
- the existing CLASS/CAMB workflow is reused instead of adding another workflow.

## PROVENANCE / COPYRIGHT

No third-party code copied.
CAMB is an external runtime dependency used as a numerical authority by the existing workflow.
The RLL comparison code is independently implemented.

## F_ok

- benchmark design is layer-separated;
- three cases prevent single-point accidental agreement;
- receipt and checksum path are defined;
- existing workflow infrastructure is reused.

## F_gap

- exact-head CI evidence;
- if passed: RLL-specific perturbation closure and growth remain open;
- if failed: mismatch localization remains before any downstream likelihood change.

## F_next

If the benchmark passes:
`GROWTH-THEORY-001` becomes the next P0 scientific gap.

If it fails:
use the two r_s evaluations to distinguish `zstar` approximation error from integration/background error.

SOURCE != CONFIG != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
