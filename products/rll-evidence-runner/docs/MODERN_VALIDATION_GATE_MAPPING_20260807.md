# Evidence Runner -> modern RLL validation gate mapping (2026-08-07)

Status: `claim_allowed=false` / non-destructive / no automatic scientific promotion.

This mapping prevents duplication between the modern observational gap registry and the already implemented Pantheon+ full-covariance Evidence Runner.

## Existing executable evidence

Canonical experiment:

- `experiments/pantheon_full_covariance_lcdm_rll_fit_v1.yml`

Existing materialization/verification chain:

1. `scripts/fetch_pantheon_covariance.py` downloads the official `Pantheon+SH0ES_STAT+SYS.cov` pinned to repository commit, Git blob SHA-1, byte count and SHA-256.
2. `scripts/verify_pantheon_inputs.py --require-full-covariance` verifies catalog/covariance readiness.
3. `rll_evidence.pantheon_fit_ascii` executes the full STAT+SYS covariance likelihood without a diagonal fallback or jitter.
4. Evidence Runner emits a hash-bound receipt and keeps `claim_allowed=false`.

## Relationship to the modern gate

Modern registry gate:

- `RLL-MOD-P0-SN-CALIBRATION-COVARIANCE`

The existing Pantheon+ experiment is **partial materialized evidence** for that gate, not sufficient closure.

It can establish:

- official Pantheon+SH0ES catalog provenance;
- official STAT+SYS covariance provenance and 1701x1701 shape;
- full-covariance numerical LCDM/RLL fit under one selection/nuisance policy;
- deterministic multi-seed optimizer diagnostics;
- compact receipts without committing the 33 MB covariance to Git.

It does **not** establish:

- DES-Dovekie calibration/covariance ablation;
- CPL/w0wa result in the same full-covariance Pantheon likelihood;
- real nested-sampling evidence;
- independent cross-implementation replication;
- joint DESI/CMB/growth validation.

Therefore:

```yaml
pantheon_plus_full_covariance_baseline: EXECUTABLE_EXISTING
modern_sn_calibration_ablation: TOKEN_VAZIO
cpl_same_sn_likelihood: TOKEN_VAZIO
real_bayes: TOKEN_VAZIO
claim_allowed: false
```

## Next code delta after the fresh receipt

Extend the full-covariance model set from `{LCDM, RLL}` to `{LCDM, CPL, RLL}` without changing catalog selection, covariance, nuisance profiling, seeds or integration grid. Keep DES-Dovekie as a separate calibration variant so a sample/calibration change cannot be silently mixed with a model change.
