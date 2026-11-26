# RLL Growth fσ8 — strict source validation and provenance (2026-11-18)

Review branch: work/rll-growth-input-fail-closed-20261118; base rll/lab. Code producer is scripts/check_rll_growth.py.
Scope is **input integrity only**. No change to background expansion, RK4 integration, growth equation, model settings or reported cosmological evidence. claim_allowed=false.

## Exact falsifier
Previously `read_data('missing.csv')` returned [], the same value as a deliberate no-data invocation; `evaluate_models` would calculate predictions but output chi2=None without identifying that the observation file failed to load. This is scientific input failure and cannot be treated as zero observations.

Now, explicit paths must exist, be regular CSV files, have >=1 data row, finite redshift z>=0, finite fσ8 and strictly positive finite sigma. Bad inputs fail with typed FSIGMA8_INPUT_* exceptions and line context. The deliberate prediction-only mode `read_data(None)` or `read_data('')` remains accepted with input_status=NOT_REQUESTED_PREDICTIONS_ONLY.

The JSON data_policy includes input_status, input_row_count and input_sha256 from the real bytes. This receipt is a source checksum, NOT the missing survey cross-covariance. Real source duplicate z=0.6 from different surveys remains as separate observations; no deduplication or altered values.

Data redshift beyond integrated model grid must fail, never interpolate the endpoint as if it were the observed higher z.
The comparison remains a **GR smooth-dark-sector growth approximation with diagonal measurement errors**, not an RLL perturbation completion, Boltzmann/CMB, full RSD covariance, or independent inference on S8. A row-level check is not a statistical model-selection proof.

## CI and recovery
- Existing suite + new `tests/test_rll_growth_input_fail_closed_v1.py`.
- Negative cases: missing path, empty CSV, NaN, inf, nonpositive sigma, malformed z, zero rows, path outside growth grid.
- Positive controls: explicit no-input prediction-only and duplicated z preserved with SHA-256.
- Acceptance: exact-head Python workflow, branch maturity and required governance checks, no regressions.
- Rollback: PR DRAFT/HOLD unmerged. Preserve original source and observations; append corrective successor instead of force-update or deleting history.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.
