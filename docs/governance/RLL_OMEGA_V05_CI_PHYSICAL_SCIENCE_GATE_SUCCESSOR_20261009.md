# RLL Ω v0.5 — evidence successor and CI falsifiers (2026-10-09)

Authority: uploaded owner-scoped ZIP/APK plus independently read GitHub Actions metadata. **No private raw logs, telemetry or APK files committed.** `claim_allowed=false`.

## Exact source / provider / artifact / observed runtime chain

- Source PR #1095: merged into `rll/lab`; feature HEAD `122df6bbbf900964374e7b6093276caa062485aa`, merge commit `1adcf6020b705c2a6b5eafcdeda70a06d45d0121`.
- Provider Android Build run `37981690643`: Android job **SUCCESS**; debug APK artifact `11641520124`, registered artifact ZIP SHA-256 `51d21e1e2260c4b566aef6698f640ff17e13602ab8f07cbea962f4b28fb49f39`.
- Independently received user ZIP `rll-debug-apk (2).zip`: SHA-256 **exactly matches** provider archive digest above; `app-debug.apk` 92827 bytes, SHA-256 `a11e0125e9e773d32380645a79f30f718094484d2c0c5420b51163d36f727e8d`.
- Independently received `RLL_CANONICAL_OMEGA_ALL_EVIDENCE (1).zip`: SHA-256 `282ade40b74484baad4d8c7700636cfddf26486823b9c5ef04e23a98d19eeb43`; 73 ZIP entries including SHA manifest. Verified 72/72 SHA entries, with 71/71 ATLAS entries (ATLAS excludes its own entry, avoiding cyclic self-hash).
- The app-reported installed-package SHA-256 matches the exact uploaded APK bytes; debug certificate X.509 SHA-256 `39b7363dac2076dabc556dda43d59da0a818c11a2a695fb728e33e4d90b665e9`, obtained independently from APK signer block (JAR/v1 certificate) and matches PackageManager self-report. This **does not** attest installation independently.
- Device self-report Android SDK29 / Motorola moto e(7) power / ABI armeabi-v7a, versionCode 5 / versionName 0.5.0-debug; locally self-reported JNI 4/4 concordant vectors.
- Independent hosted Python-stdlib audit: 47 scoped integrity / matrix / consistency gates passed, 0 failed. 44 per-point formula receipts, 4 x 11; 29 enumerated formula controls (24 pass self-reports, 5 explicitly typed unrun). No independent physical or scientific validation implied.
- Independently recomputed BAO 13x13 full covariance at **fixed parameters** (with empirical sound-horizon proxy): ΛCDM 18.761209524949, wCDM 18.761209524949, CPL 82.808282486745, RLL 105.652156361133. χ² values are not a fit, posterior, evidence, Bayes factor or model preference.
- ARMv7 `ELF32 EM_ARM`, ARM64 `ELF64 EM_AARCH64`, dex header checked. JNI .so has dynamic dependencies `libc.so`, `libdl.so`, `libm.so` (Android NDK boundary), so **do not** label the entire APK freestanding/zero-libc.

## Scoped absences and restrictions

| Gate | Status | Closing evidence |
|---|---|---|
| Independent physical installation / hardware witness | `TOKEN_VAZIO_NOT_ATTESTED` | External authorized ADB pull of installed base.apk and SHA/signature |
| APK v2/v3 signing verification | `TOKEN_VAZIO_NOT_RUN` | Android build-tools `apksigner verify --verbose --print-certs` independently |
| Stable production release signer | `TOKEN_VAZIO_NOT_PROVIDED` | Approved release keystore digest and verified release APK |
| CLASS/CAMB / official DESI posterior / external independent replication | `TOKEN_VAZIO_NOT_RUN` | Predeclared scientific protocol, inputs and independent run |
| Dynamical Poincaré / RMRCTI ΔP | `TOKEN_VAZIO_NO_TRAJECTORY` | Real trajectories and source-contract peak/stable_any records |
| Distribution rights | `TOKEN_VAZIO_UNVERIFIED` | Upstream licensing/custody review before redistribution |

**CI not globally green:** exact feature commit run `37981693732` Python tests: 3 failed / 2255 passed. Failure A: hardcoded `getOrElse(2)` test against approved `getOrElse(5)` Gradle revision; Failure B/C: workflow contract expected 117, observed 119. Exact feature run `37981693653` platform assurance failed for same workflow count drift; `37981693661` Six Sigma real-data controls failed when materializing documentation inventory delta (not repaired or silently attributed). This PR contains only two **source-side falsifier-backed** test / workflow contract corrections. It does not alter APK/model equations or claim new physical execution.

## Rollback and future operation

Review branch only, no merge/promotion. Rollback the isolated two-file patch by reverting its commits, never rewrite historical evidence. For future one-button data capture, the existing v0.5 APK is already built; do not rebuild to repeat receipt capture. If CI is re-run, bind receipts to the new exact HEAD rather than reusing the old build run. Retain app-owned logs privately and never publish hardware IDs / personal content.

SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM; TOKEN_VAZIO ≠ 0; IMPLEMENTED_UNTESTED ≠ PASS.
