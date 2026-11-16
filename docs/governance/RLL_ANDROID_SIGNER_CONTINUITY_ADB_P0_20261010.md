# RLL Android — P0 signing continuity and non-destructive external witness

Date: 2026-10-10
Parent: GitHub issue #1104; prior evidence receipts MU-20261010-RLL-V07-V08-SIGNER-CONTINUITY-P0-S3.
Scope: hosted Android SDK/ADB **tools and tests only**; no APK, signing keys, applicationId, release workflow, model, data, or scientific equations changed.
Status: SOURCE_HOTFIX_LOCALLY_TESTED / CI_EXACT_HEAD_PENDING / claim_allowed=false.

## Source-side falsifiers and observed evidence

The predecessor file tools/android/rll_capture_install_via_adb.sh at Git blob 313f3c3241297fc1dab11670aa9f5034848f3fdf had an unterminated shell quote/grep expression inside REMOTE=... and duplicate orphaned collection statements. POSIX sh -n fails on the predecessor; an independent external installation witness could not safely rely on it.

Current source app/build.gradle (Git blob 8a99282563c7748180ab373c9fe90cc856100662) declares release signingConfigs from externally-provisioned RLL_RELEASE_* credentials. It does **not** configure a persistent debug signing identity. The Android Build workflow (blob c2914d4fdbd3ff08123a76c0c51798c8e412241d) runs :app:assembleDebug on ubuntu-latest, and only decodes the externally-provisioned release keystore if the release-secrets presence gate is satisfied. Existing source docs already warn that ephemeral debug certificates may be incompatible across CI runs. **We did not observe the runners' keystore bytes**, so this is a reproducible source capability explaining an observed mismatch, not a proven historical key-creation cause.

Observed historical input certificates:
- V07 APK SHA256 586072a56852dcbde73bc3e04dca1e8fe111c5da46dffc31043271b9a90301ab, package org.rafaelia.rll.debug, versionCode 7, signing X509 SHA256 571d24046744ebcdb060bfee28ea9d98a012a053f2b382a9576de8196f24fd68;
- V08 APK SHA256 ec368202ade86ac8e9a7f7ec18281d0846b2ce15a7b41bdf370a1ca499c48f11, same package, versionCode 8, signer SHA256 e4b505bc03026b00883461bf6865e18468ac479407a975557ab770d647ca9c85.
Private user bytes and host-side standalone cryptographic verification are retained in Google Drive controlled evidence custody; **never commit the APKs, certificates' private keys or device dumps**.

## Source-side repair

1. Replace broken ADB capture helper by a POSIX-sh -n-clean read-only collector with restrictive umask (077), output-clobber refusal, 1-device guard, package/base.apk path checks, explicit SHA-256 expected identity and typed no-hash/mismatch outcomes. It has no install, uninstall, cleanup or default dumpsys commands. It only captures from a device whose ADB access the user has authorized. ADB host observation is *not* hardware attestation.
2. Add tools/android/rll_android_upgrade_preflight.py: read-only use of **official** Android SDK Build Tools apksigner verify --verbose --print-certs and aapt dump badging for BOTH exact APK paths. It compares package, monotonically increasing versionCode and observed certificate SHA256. Mismatched signers, different package or nonincreasing version **fail closed** (exit 3). SDK unavailable, unsigned/tampered/unsupported outputs **fail closed** (exit 2). Even a scoped pass **does not authorize install**.
3. Add fast pytest source-level positive/negative contracts with simulated ADB and SDK outputs. No private raw APKs embedded and no physical install attempted.

## Use — explicit, non-destructive human authorization

From repo root, on a trusted host with Android SDK Build Tools in PATH:

    python3 tools/android/rll_android_upgrade_preflight.py v07-exact.apk v08-exact.apk

Exit 3 means BLOCKED; investigate certificate/key authority and rotation with actual Android SDK output. For the examined historical APKs, an in-place upgrade is *not approved* by the signing continuity evidence; do not force an uninstall to conceal this block.

To capture ONLY an existing installation from one authorized device, after observing its package and consent:

    sh tools/android/rll_capture_install_via_adb.sh ./unique_private_receipt_dir <EXPECTED_INSTALLED_APK_SHA256>

The collector refuses preexisting output directories, requires expected digest for an identity PASS and retains pulled APK in the private directory. Avoid publishing any collected device data. A trusted operator separately reviews the output and the official apksigner result. On-device validation is pending.

## Tests and gates

Local hosted/source tests (no ADB device, no Android SDK accepted as proof): 8 ADB script tests + 8 signing preflight tests = 16/16 PASS, shell -n PASS.
Separate private byte-bound verifier regression (historical V07/V08): 3/3 PASS; expected BLOCKED_IN_PLACE_UPGRADE_DIFFERENT_SIGNER, and other 10 historical archive/v2 negative/positive tests preserved by prior receipts. Neither private results nor local source tests are GitHub CI validation until the exact-head provider run is observed.
No stable debug/release keystore has been created, restored, accessed or installed.
No scientific model modifications; claim_allowed=false.

## Next execution decision, reverse path

- Root cause P0: identify which authorized CI configuration controls debug/release signer continuity, including exact run and artifact ID. If authorized, fix producer identity via controlled signer, or deliberately use distinct applicationId for disposable parallel test; do not secretly migrate user data.
- Execute official apksigner preflight and bounded external ADB witness only when hardware is authorized and no data-destruction path is required.
- Preserve SHA256 and provider exact-head test run before merge; if global gates fail, distinguish new source failure from unrelated baseline/provider defects.
- Separate V08 physical evidence from DESI/CLASS/CAMB scientific falsifiability; never promote SOFTWARE_PASS to COSMOLOGY_PASS.

Rollback: close the draft PR without merge, or revert only this helper/preflight/test/doc delta if later merged. Keep original evidence and historical receipts append-only.

R3 F_ok=source-side shell parser defect reproduced and repaired + falsifiers; F_gap=CI readback, SDK real invocation, independent ADB witness, signer policy/keystore ownership; F_next=exact-head checks and authorized signer strategy.
