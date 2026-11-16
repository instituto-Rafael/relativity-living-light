# RLL source/receipt/claim boundary — falsifier successor (2026-10-09)

**Parent:** merged [PR #1087](https://github.com/instituto-Rafael/relativity-living-light/pull/1087), inheriting merged #1086. **Status:** candidate hotfix, `claim_allowed=false`. This is a *source-side provenance guard*, not a cosmological model change.

## Reproducible overlooked source-side falsifier (P0)
The old `analyze(--source X)` sent X's bytes to `source_facts` and recorded their SHA-256, but its numerical functions were imported from `data.pipelines.structure_d.joint_real_likelihood`. Two distinct synthetic source files, each passing the AST presence guard, therefore produced identical numerical diagnostics with *different* claimed source hashes. Local reproducer `/mnt/data/rll_source_identity_falsifier.py` showed this at the exact parent blob SHA `80f608897b6eecede68b40f7f55ecb1bf34f4326`; fixed isolated local repro rejects it.

**Correction:** reject any caller-supplied source file not resolving to the imported module's `__file__`, with `TOKEN_VAZIO_SOURCE_RUNTIME_BINDING`. Read bytes once for each source and archive; use those same bytes to parse/sha. This checks **file-path identity only**, not whether live in-memory Python bytecode came from the bytes currently on disk. No false bytecode attestation.

## Additional missed guards (P0/P1)
- Missing, malformed, nonfinite, duplicated or schema-incompatible historical input is typed `TOKEN_VAZIO_ARCHIVE_*` rather than fed into scientific metrics.
- Invalid source syntax/encoding and missing source are separately typed `TOKEN_VAZIO_SOURCE_*`.
- An unphysical/nonpositive E²(0) is now blocked *before* `hz_from_e2`'s numerical sqrt floor could mask it.
- **Historical execution identity remains unknown:** the observed source SHA does not attest which exact commit executed to produce the 2026-07-03 archived fit. `source_archive_execution_identity=TOKEN_VAZIO_HISTORICAL_FIT_SOURCE_NOT_ATTESTED`.
- The archival `interpretation_label=lcdm_preferred` and global BIC minimum of CPL are **not automatically contradictory**: global competition `CPL` and the pairwise `LCDM` vs `RLL` winner `LCDM` are distinct questions. The archived label's authorial intended scope is `TOKEN_VAZIO`, pending explicit definition.
- When `Os0=0`, transition parameters `zt,wt` may be unidentifiable. Historical k/BIC penalties and asymptotic likelihood inference need separately preregistered effective parameter analysis; do **not** rewrite the historical k or BIC.
- G0 `Om+OL+ORAD(+Os0)` normalization and assumption `D_M=D_C` (flat geometry) require an explicit curvature/parameter closure. G1 `r_drag` vs `r_s(z*)` proxy is **not** a Planck/CAMB recombination analysis; CMB distance priors may assume a reference model. G2's smooth-GR ΛCDM ODE omits radiation while the joint shortcut includes it; the gap is a diagnostic *under different approximation regimes*.
- No evidence that the four push failures of the book/import/dashboard/android workflows originate from #1087: they also occurred at predecessor #1086, and the observed failed runs returned **zero inspectable jobs**. Classify `WORKFLOW_LEVEL_FAILURE_CAUSE_TOKEN_VAZIO`, not `SOURCE_SIDE_FAIL` or `PROVIDER_FAIL` without logs.

## Verification and gates
1. `python -m pytest -q tests/test_rll_joint_g0_g2_adapter.py tests/test_rll_joint_g0_g4_receipt_binding.py` on **exact feature HEAD**. A successful result is **CI_SCOPED_PASS**, never independent RLL science verification.
2. `python scripts/rll_joint_g0_g2_adapter.py --output /tmp/rll_g0_g2_successor.json`. Never write over the source or archived result.
3. P0 rights/copyright review before redistributing third-party sources, official datasets, and Planck/DESI table extracts.
4. Independent CLASS/CAMB benchmarks, held-out observations, proper CMB recombination `r_s(z*)`, fσ₈ perturbations, matched fitting priors and fixed parameter/curvature conventions **before changing cosmological equations or promoting model claims**.

No private NOVOexport corpus content is copied. RafPolimata Geometry21 remains an independent formal freestanding candidate without demonstrated physical link to cosmology.

**Rollback:** revert only the source adapter change and this successor test/document pair, preserving prior PR #1087, archived 2026-07 fit and observational datasets. **SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM; TOKEN_VAZIO ≠ zero.**
