# RLL — alphaXiv × NOVOexport × Structure-D: source-first preflight (2026-10-09)

**State:** IMPLEMENTED_CANDIDATE / TEST_GATE_PENDING / `claim_allowed=false`.

## Custody and boundaries

- START HERE V2.2 → CURRENT_STATE HOTSTATE V4.5 → canonical index → NOVOexport corpus navigation.
- NOVOexport longitudinal map reports 51 shards (000–050), 5,052 non-empty conversations, and 111,367 user messages through 2026-08-03. **Those numbers are from a derived index, not a new 51-shard rescan.** Original JSONs were not modified.
- User messages and assistant-generated text are distinct evidence classes. First occurrence in one shard is not first occurrence in the entire corpus. The shard-045 token genealogy is a scoped example.
- No private conversation text, document ID, message ID, or raw JSON is copied to this public repository.
- Historic internal comparisons or analogies to later external papers do not establish independent validation, causality, academic priority or authorship.

## Recent external independent research

1. DESI Collaboration, *DESI DR2 Results II: Measurements of Baryon Acoustic Oscillations and Cosmological Constraints*, arXiv:2503.14738 — BAO/covariance and combined-probe context.
2. Gu, Wang et al., *Dynamical Dark Energy in light of the DESI DR2 Baryonic Acoustic Oscillations Measurements*, arXiv:2504.06118 (2025 v3) — reconstruction and data-/model-dependence; compare multiple parameterizations and SNe compilations.
3. Roy Choudhury, extended-parameter DESI DR2 cosmology, arXiv:2504.15340 — multi-parameter degeneracies and model-dependence; check priors and mass/lensing nuisance parameters.

**Citation ≠ reproduced likelihood ≠ independent experimental confirmation.** These references are methodological inputs only; the numerical results have not been recomputed by this change.

## Source-side questions, not silent patches

- **P0 H(0)/H0:** The joint fit's `e2_*` functions sum fitted `Om`, `OL`, radiation and possibly `Os0` at z=0; the code multiplies by a fitted `H0`. Test whether this is a physical normalization error or an intentional scale parameter. Existing archived fitted values need re-evaluation under a declared cosmological convention.
- **P0 CMB acoustic horizon:** `cmb_shift_prediction` uses `rd_drag_mpc` where the usual CMB angular acoustic scale calls for `r_s(z_*)`; verify recombination-vs-drag redshifts and consistent sound-horizon theory before changing the likelihood.
- **P0 growth:** `fsigma8_prediction` currently uses `sigma8*Omega_m(z)**0.55`; explicitly investigate missing `D(z)`, comparing with a full perturbation solver and consistent normalization.
- **P0 RLL transition asymptotics:** Current `e2_rll` superposition `Os0*[f + (1-f)*(1+z)^3]` tends to **matter-like** growth at large z for logistic f→0, not `(1+z)^4` radiation. Earlier corpus-derived descriptions mentioning a relativistic high-z component may refer to another formulation; recover an exact source version before asserting equivalence.
- **P1 model selection label:** Archived `results/structure_d/joint_real_likelihood.json` says `interpretation_label=lcdm_preferred`, but the four archived rows rank CPL first by BIC and AICc. Append a successor interpretive receipt; never overwrite the original result to conceal this discrepancy.
- **P1 null boundary:** Archived RLL optimum `Os0=0` makes its transition parameters non-identifiable locally. Assess profile likelihood/priors and non-regular criteria before treating naïve AIC/BIC penalties as physical proof.

## Initial implementation and falsifier boundary

The stdlib-only `scripts/rll_joint_physics_preflight.py` reads the existing source and archived result, extracts limited Python AST facts, checks `E²(0)` algebraically on archived parameters and reports typed flags including covariance/growth candidates and archived label conflicts. It can write a new JSON receipt via `--output`, refusing to overwrite either source or archived result. A flag is **not** a validated physical counterexample: line/source-specific numerical reproductions remain a separate gate.

Run from repository root:

```sh
python scripts/rll_joint_physics_preflight.py --output /tmp/rll_joint_physics_preflight.json
python -m pytest -q tests/test_rll_joint_physics_preflight.py
```

## Follow-up execution gates

1. Verify this preflight at the **exact PR head**, record source/result hashes and tests. Do not infer CI success from commit creation.
2. Implement direct in-module physical sanity tests for `H(z=0)`, CMB angular-scale definitions and `fσ8` against an independently normalized solver. Preserve negative evidence.
3. For discriminating RLL against ΛCDM/CPL, preregister priors, seeds, redshift-truncation/BAO tracer ablations, held-out observations and a null-boundary-aware statistic.
4. Compare against indexed NOVOexport source expressions using private, role-aware, per-shard locators; avoid uploading private source text to the public repo.
5. Write an append-only μWRITE successor only for observed material transitions; preserve rollback links and previous evidence.

`F_ok` = inputs located and preflight mechanism authored; `F_gap` = physical reproductions, CI exact-head readback, full private corpus scan, independent validation; `F_next` = exact-head gate then numerical falsifier.
