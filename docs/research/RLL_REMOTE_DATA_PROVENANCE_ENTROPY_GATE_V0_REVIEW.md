# RLL Ω — Remote dataset provenance × entropy-cycle falsifiers (review V0)

**Date:** 2026-11-14. **Producer/authority:** RLL `main` historical base
`e127d44c1dbe210b5fe021b64d2f877837ca45db`.
**Status:** REVIEW_ONLY / SOURCE_WRITTEN / NOT_RUN / claim_allowed=false.
No observational or cosmological model result is modified or promoted here.

## Why this study is additive rather than another entropy model
Use `001_PONTEIRO/RLL_ENTROPY_DISPERSION_STABILITY_CURRENT.md`,
`docs/science/RLL_ENTROPY_DISPERSION_STABILITY_RETRO_V1.md`,
`scripts/rll_entropy_stability_v1.py` and
`001_PONTEIRO/RLL_COSMOLOGY_COMPARISON_V1_CURRENT.md` as local authorities.
The synthetic seven-window counterexample already establishes:
equal empirical Shannon entropy across windows can conceal a drift in means.
Do not recreate that test with new words or infer cosmological stationarity.

## Precise new question
Can immutable remote object selection + bounded local cache preserve byte identity,
dataset grouping, ordering, covariance alignment and null semantics in RLL scientific
consumers when the phone cannot hold all input datasets?

This is a data-provenance/infrastructure question, not a novel cosmological mechanism.

## Source → execution → evidence matrix
- **Source**: `data/real/Hz_data_real.csv`,
  `data/real/cosmology/desi_dr2_bao_primary_points.csv`,
  `data/real/cosmology/desi_dr2_bao_covariance_summary.csv` and optional
  `data/real/cosmology/fsigma8_growth.csv` from
  `NEXT_RLL_VALIDATION_STEP.md`. Only use actual verified dataset revisions,
  not these filenames as evidence that the bytes currently match.
- **Remote identity**: provider/account + file ID + version/revision + size +
  independently computed SHA-256 of exact downloaded bytes, where permitted.
  Native Google Docs exports require export format/revision in identity.
- **Execution**: offline/local baseline and remote-range/hybrid-cache replay over
  identical pinned bytes, same code HEAD, same selection, same ordering and
  identical covariance matrix. Use read-only remote data.
- **Evidence**: raw input hashes and count, byte-comparison receipt, missing/error
  classification, stdout/stderr exit statuses, prediction outputs and exact
  `chi2`, AIC/BIC, model parameter count. Use exact-head GitHub Actions and device
  receipts separately.
- **Claim**: only compare scientific results if equivalence gate passes. If network
  data are incomplete, fail closed; never turn missing values into 0 or silently
  impute / remove rows.
- **Privacy**: raw private archives are NEVER added to a public RLL Git repository;
  Supabase may hold private scoped metadata, not copy-pasted archive contents.

## Four orthogonal falsifiers
1. **Byte equivalence**: same pinned input must reconstruct exactly; if not,
   `DATA_SOURCE_INTEGRITY_FAIL`. Provider metadata or a ZIP file listing does not
   prove equal bytes.
2. **Statistical equivalence**: repeated runs with pinned code and data must
   preserve full covariance, order, units, likelihood definition and outputs within
   declared numeric tolerance. A new cache cannot modify the likelihood.
3. **Time-varying information**: observed cache state/entropy must not be confused
   with the astrophysical quantities. Equal cache entropy cannot establish
   stability of cosmological residuals; use existing seven-window falsifier.
4. **Power/remote failure**: kill app, revoke credentials, lose connection, change
   remote version, corrupt one/two cache chunks and verify explicit fault rather
   than silent zero-fill. XOR repair is restricted to one detected erasure with
   independently trusted checksums.

## Federated boundaries (do not copy other repos' bodies)
- Termux `rafaelmeloreisnovo/termux-app-rafacodephi`
  branch `review/internetmount-hybrid-v0-20261114` owns isolated
  `native/internetmount/raf_im_ecc_v1.h`, hosted test and SAF proposal.
  Its source/readback is NOT a physical Android or cloud-mount test.
- Drive START HERE Ω V2.2 routes; latest committed checkpoint provides inventory
  state, not global content identity. BACKUP LINEAGE preserves historical copies.
- Supabase `raf_private.drive_metadata_index_v1` and
  `raf_private.drive_metadata_identity_projection_v1` hold scoped metadata
  observations. Do not infer cross-provider content equality or release data.
- This RLL branch owns only the scientific input/output equivalence gate design.

## Minimal acceptance criteria
(A) exact pinned data and model snapshot, (B) offline vs remote replay hashes,
(C) `NOT_RUN` represented distinctly from `FAIL` and `PASS`,
(D) zero unauthorized public payloads, (E) negative test: corrupt range / missing
chunk / invalid covariance must terminate before cosmological claims,
(F) no altered scientific model, no changed stored datasets or prior results.

## R3
F_ok = existing real-data validation path and synthetic entropy counterexample
read and referenced without duplication.
F_gap = remote replay, data hashes, hosted and Android tests, full covariance
alignment checks, scientific reproducibility under failure = NOT_RUN.
F_next = review with RLL scientific owner, pin one tiny public/non-sensitive
fixture and test exact byte roundtrip; only then compare full data.
Rollback = discard isolated review branch; `main` unchanged.
