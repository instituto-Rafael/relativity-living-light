# G4 — nested-null optimizer hotfix (review-only, 2026-11-18)

## Finding / SOURCE
The immutable artifact [Python tests run 44251877786](https://github.com/instituto-Rafael/relativity-living-light/actions/runs/44251877786) shows a G4 joint 1698-observable result: ΛCDM χ²=1492.574832908293, GEDE χ²=1522.7948344813904. The same receipt verifies GEDE Δ=0 exactly recovers ΛCDM in E². Hence the reported GEDE best is inconsistent with the nested model's available parameter set. In the five-start GEDE fit, seed 11 stopped at the canonical point after one iteration; several other seeds also stopped after one iteration. This is an **optimizer/local-minimum problem**, not a physical penalty and not evidence that GEDE is inferior by +30.22 in χ².

## Fix / regression boundary
This branch changes ONLY the G4 optimizer's starting set and guard:
- The original five seed starts remain preserved.
- For each extended model, append a sixth, explicit LCDM-best-fit start at its exact declared null limit (w=-1; CPL w0=-1,wa=0; GEDE Δ=0; IDE β=0; RLL Ωs0=0,zt=1,wt=0.3).
- Record the direct null-likelihood evaluation separately from optimizer output. A purported optimized best worse than the known nested null is BLOCKED, not PASS.
- No data, covariance, H(z) formula, model prior or sound-horizon policy is modified.
- `claim_allowed=false`; scientific model comparison remains limited to background. Follow-on G5/G6 receipts must be recomputed and cannot reuse an old G4 SHA.

## Falsifiers
1. Mathematical null E² matches ΛCDM for all extensions to ≤1e-12.
2. Large positive χ² difference of an alleged nested optimum fails the guard; best fit ≤ anchor within roundoff.
3. All five original seeded fits remain in the receipt; the extra start is identified as `best_LCDM_embedded_exact_null`, seed=-1.
4. No scientific claim from a green CI: G6 prior/sampling stability remains independently BLOCKED.
5. Validate exact G4 HEAD in CI using 1657 Pantheon+, 28 CC, 13 DESI observations. A missing verified STAT+SYS covariance is `TOKEN_VAZIO` and must fail closed.

## Provenance
Review branch from `rll/lab@f83f6173cb98fc785935da35afe4b31c609f1744`, source `tools/run_g4_background_tournament.py`, tests `tests/test_g4_nested_null_optimization_v1.py`. This is a scientific numerical improvement candidate, not yet an accepted optimum or merge authorization. Rollback: leave review PR unmerged and preserve original source and receipt.


## Post-merge lab reassessment (2026-11-18) — source-level regression

Live lab advanced from `f83f6173cb98fc785935da35afe4b31c609f1744` to
`a84cb8a00425da97915d8f64d1c6704ebf4f8397` after PRs #1234/#1235/
#1237/#1238/#1239/#1240 were merged. This PR remains a distinct DRAFT/HOLD
candidate, initially 17 commits behind lab and mergeable in the GitHub API.
The G4 source blob on lab remains `cb4c449e05e520b73135facd4074d4bb236a3f9b`,
and this PR's corrected source differs only by its audited nested-null logic.

A new `test_g4_nested_full_background_profiles_are_equal_across_all_blocks`
uses **synthetic** correlated Pantheon-like, chronometer and DESI-like data
and checks exact equality of every forward observable, the profiled M_B,
each χ² component, and total χ² at the true nested LCDM embedding for all
five extended models. This falsifies a narrower but critical failure missed by
the original test: equal E² while distances, sound horizon, covariances, or
nuisance profiling disagree. These synthetic values are not measured survey
data and cannot supply a cosmological claim.

The exact-HEAD provider CI, including G4 integration and G6 scientific
BLOCKED receipts, must still pass after this successor commit. A green
workflow never means perturbative closure or physical confirmation.
No merge is authorized by this review; `rll/lab` and `main` stay untouched.
