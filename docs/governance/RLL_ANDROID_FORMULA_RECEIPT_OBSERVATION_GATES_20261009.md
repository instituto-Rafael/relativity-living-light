# RLL Android Formula Lab: observation and receipt integrity successor (2026-10-09)

**P0:** source/observation mismatches have direct impact on valid scientific model comparison. Parent: RLL merged PR #1091 (`rll/lab` exact code). New changes only to formula receipt, hosted UI, tests and this note; no cosmology models, parameters or source datasets changed.

## Input evidence received from the device, confidential receipt remains in conversation
A user-provided transcript marked `arch=32`, `android_abi=armeabi-v7a` and 4 of 4 independent Java/JNI/C score vectors PASS. This is **user-submitted on-device execution evidence**, not independent device identity or attested installation. A separate native receipt and formula receipt must NOT be merged into one SHA-256 claim.

The transcript included RLL/wCDM H(z) and normalized residuals plus single-point χ². Algebraic reconstruction confirms the output χ² equals residual². However, if the same observational pair `Hobs` and positive `sigmaH` were supplied to both models, then
```
  residual_A = (Hobs - H_A) / sigmaH
  residual_B = (Hobs - H_B) / sigmaH
  (residual_A - residual_B) * sigmaH = H_B - H_A .
```
The user-supplied numbers violate this invariant *if interpreted as matched observations*: the implied uncertainty is negative. The input pair was not included in either v1 receipt, so this is a **missing-evidence gate, not proof of a model or code physics defect**. The user may simply have changed the manual observation between runs. No raw private receipt pasted into public GitHub.

## Reproducible defects and corrections
1. **Missing observational inputs P0:** `FormulaEngine.Result.receipt(Input)` previously documented parameters but skipped `Hobs`/`Hsigma` while using them for residual and χ². New `rll.android.formula-lab.v2` receipt records both with round-trippable Java `Double.toString`, or explicit `TOKEN_VAZIO_NOT_PROVIDED` / `TOKEN_VAZIO_INVALID_PAIR`. Values remain `USER_ENTERED_UNVERIFIED`, never attributed to official data without dataset provenance.
2. **Rounded parameter precision P1:** prior v1 `%.12g` truncated inputs. New v2 prints binary64 round-trippable decimal representations of all key parameters, preserving the calculation input state (not physical precision).
3. **Duplicate sweep receipts P1:** prior `lastReceipt += evidence` appended multiple sweeps to a single result; now each sweep sets `lastReceipt=lastBaseReceipt+newSweep`, preventing accidental mixing of different runs.
4. **Literal text "\\n" P1:** old Java UI used doubly escaped newline strings in selected-formula and sweep outputs. Now use proper Java `"\n"` strings for human-readable and parseable line separation.
5. **Stale input P0:** old UI allowed copying a last calculation after changing model or parameters without recalculating. New gate recompares an exact current `FormulaEngine.compute(...).receipt(...) + version_gate` baseline. If mismatched, preview/copy FAIL CLOSED to `TOKEN_VAZIO_STALE_INPUT` and request recalculation.
6. **Receipt hash scope P1:** SHA-256 now clearly covers only UTF-8 bytes of `FORMULA_LAB_PAYLOAD_UTF8_ONLY` through the `receipt_hash_scope` line, not separate pasted native diagnostics or text added after the digest.

## Tests / evidence and limitations
- Independent standalone JVM gate cross-checks two distinct model H(z) residuals using identical manually supplied Hobs/sigma and confirms the exact invariant, plus v2 presence or absence of observational pair.
- Python static falsifiers assert bounded source impact, actual newlines, no sweep accumulation, stale-state guard and hash scope.
- Android CI requires Java gate and ARM32/AArch64 APK builds on the exact HEAD; until that terminal run, state is `IMPLEMENTED_UNTESTED_EXACT_HEAD`.
- Existing RLL `rll/lab` merged PR #1091 and earlier results untouched. The model remains `claim_allowed=false`; DESI, Planck, CLASS/CAMB, covariance, physical scientific measurement, stable signing and signed update validation are separately `TOKEN_VAZIO_NOT_RUN`.
- A hash is an integrity check of one defined byte payload, not cryptographic proof that the device, observation or physical cosmology is authentic.
- Rollback: revert only the v2 schema/observation patch, FormulaLabView UI changes, revised Java selftest, added static test and this document. Preserve historical v1 user receipts as immutable evidence; add successor rather than rewriting old SHA.
