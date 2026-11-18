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
