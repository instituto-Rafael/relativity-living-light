# RLL Android PR #1092 — commit / CI / APK / signer / install gate (2026-10-09)

Scope: exact provenance check, **no APK rebuild, no code/model changes, no promotion of scientific or physical installation claims**. SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM; TOKEN_VAZIO ≠ 0.

## Exact producer
- PR: https://github.com/instituto-Rafael/relativity-living-light/pull/1092 (open draft at observation).
- Source commit: `1db4481fc9b884c37e8a32ed954238649760087b`.
- CI: https://github.com/instituto-Rafael/relativity-living-light/actions/runs/37974877210 — Android job SUCCESS. Signed-release build/upload SKIPPED.
- Exact-run debug GitHub artifact `11638044324`: ZIP SHA-256 `51c80bced4ba09df4532f0e98b25f38e5c2813131451ca5736201332c697e7e2`; inner APK `df91599a401af3166cce4cd12c941cb8dcc6247ea92422cf58a610dfbecb35fe`.
- Exact-run validation-unsigned artifact `11637499673`: ZIP SHA-256 `b935473ff68c16fb020ecfc9994a5801002be7a0e4310f2ad419b291eb04bd87`; inner APK `2245001b0bbe32390a74693d375ba314069c15890beaf02a2c33e76721a7c682`.

## User-uploaded bytes vs CI bytes
- Uploaded debug APK SHA-256 `f10aa018ecabb941a13fe0c1c09ac35fa266029cd4fc9c982e52874bcda4b8b5`; uploaded validation-unsigned APK `9e1eafe7ad9336bf9ca31b49203cf2b32f8b1a6843ff47b806306546cbe65d5f`.
- `classes.dex`, `classes2.dex`, `lib/arm64-v8a/librll_kernel_bridge.so`, `lib/armeabi-v7a/librll_kernel_bridge.so`, `resources.arsc`, `META-INF/com/android/build/gradle/app-metadata.properties`: six components **byte-identical in each uploaded-vs-CI debug and unsigned pair**, validated by SHA-256.
- For each comparison the binary AndroidManifest differs in precisely **two bytes**, corresponding to version `0.2.0`/code 2 vs `0.3.0`/code 3 (debug offsets 596 & 1512; unsigned offsets 596 & 1548).
- Thus `COMPILED_COMPONENTS_EQUAL=PASS_SCOPED`, but `WHOLE_APK_EQUAL=false`. The source/override operation producing the uploaded versioned APK has no independent build-execution receipt; do **not** identify it as the exact CI output.

## Signer boundary
- Uploaded APK's signer X.509 SHA-256 `8e994c45e7cb9dbb13df249bc7e7080de237d3937680cfc92830aff8f95129f8`.
- CI APK's signer X.509 SHA-256 `933d9429fe5287687aefdc21fa84a3b30399c88553e30575da2d4032f2cab074`.
- Both are **different, self-signed debug certificates**, not a stable release signing identity. `jarsigner -verify` succeeds (JAR/v1 scope) with debug-chain warnings. APK Signature Scheme v2 block exists but `apksigner` verification was **not run**.
- Do not assert continuity between these certs; no production/release-signing proof exists.

## Installed-state observation (scoped)
- User-provided archive `RLL_DESI_DR2_EVIDENCE.zip` SHA-256 `a770f48f82fd11624406109e5d71418dec36a873b1bb96327b5c2326655b8287` includes `receipts/android_install_self_report.txt`.
- App PackageManager self-report names debug package/version 2 and reports installed APK SHA-256 `f10aa018...` and signer `8e994c45...`; both match independently parsed **uploaded bytes**. This is `SELF_REPORT_MATCH=PASS_SCOPED`, **not external device attestation**.
- `INDEPENDENT_PHYSICAL_INSTALL=TOKEN_VAZIO_NOT_RUN`; `STABLE_RELEASE_SIGNER=TOKEN_VAZIO`; `SCIENTIFIC_LIKELIHOOD=TOKEN_VAZIO`. Claims remain `claim_allowed=false`.

## Closure and next gate
`COMMIT_RUN=PASS; CI_ARTIFACT_SHA=PASS; COMPILED_COMPONENT_EQUIVALENCE=PASS_SCOPED; DEBUG_SIGNER_V1=PASS_SCOPED; SELF_REPORT_MATCH=PASS_SCOPED; INDEPENDENT_INSTALL=TOKEN_VAZIO`.

An authorized **external-to-app** capture can resolve the next boundary: `adb shell pm path org.rafaelia.rll.debug` → `adb pull base.apk` → host SHA-256 and signer verification → match exact package/version/cert/hash and log/receipt. Script: `tools/android/rll_capture_install_via_adb.sh`. It is not executed by this document or a CI build. Historical evidence stays unchanged; corrections must be successor receipts.

Rollback: revert only this documentation and optional capture helper; no release/action changes.