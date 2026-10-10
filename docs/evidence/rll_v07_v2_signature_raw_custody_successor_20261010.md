# RLL Ω V07 — sucessor: assinatura v2 e custódia privada (2026-10-10)

STATUS=PASS_SCOPED_OFFLINE_CRYPTO | PRIVATE_DRIVE_RAW_CUSTODY_READBACK | claim_allowed=false
Parent: RLL #1102 merged into rll/lab at bb21b34d66d3a68c43a6aafc9042296d9386e32a.
MU_ID=MU-20261010-RLL-V07-V2-RAW-CUSTODY-S2
Scope: documentation only. No APK, model, scientific data, CI or source code changed.

## Input identity and private custody

- Private bundle contains four untouched inputs, source of offline verifier, adversarial tests, sanitized report, SHA256 manifest; 468872 bytes.
- Bundle SHA256 4c2a64d4f831aaf12ff262c0b23d374708e9be71dcbe5bc45c7dea970e7e7aa2; ZIP 11 entries.
- Drive privately stored in 04_RLL_COSMOLOGY_EVIDENCE, account owner only; provider readback 468872 bytes and raw-download SHA256 identical to local.
- Public documentation intentionally omits private Drive IDs and raw ZIP/device logs. Exact private link in Drive canonical ledger.
- APK 109222 bytes, SHA256 586072a56852dcbde73bc3e04dca1e8fe111c5da46dffc31043271b9a90301ab.
- APK cert SHA256 571d24046744ebcdb060bfee28ea9d98a012a053f2b382a9576de8196f24fd68 (Android debug self-signed).
- ARMv7 ZIP SHA256 d17553c231f276a016fa54f210273c1e0415939d54d92559e33517d20b80cb56.
- ARM64 ZIP SHA256 45ce461450c25e6ef380de04cb9238040c34e5119d68edfbacfdafb7ba8d4df6.
- Prior historical audit ZIP SHA256 e83e0cbee7e225858d40405d32e59f3b569aa90bb830f6aeaa677dfe4b92f12d.

## Independent cryptographic verification and falsification

- APK Signing Block 42 present with scheme v2 ID 0x7109871a.
- Single RSA-2048 signer; algorithm 0x0103 RSASSA-PKCS1-v1_5 + SHA-256; certificate SPKI equals signed key.
- Direct independent digest recomputation over protected APK ZIP sections (exclude Signing Block; adjust EOCD central-directory offset): bbe5107987564a62ec058269e9c458f9423bbbe2408ff3fa74139c382f1f161d.
- RSA PKCS1 signature verification and signed v2 content digest match: PASS_SCOPED_OFFLINE, not official Android platform acceptance.
- SignedData extra trailing 4 zero bytes bound to signature; no silent stripping. Needs authoritative platform verifier to characterize acceptance.
- jarsigner reports jar verified with warnings: self-signed debug certificate, invalid CA chain, no timestamp and JarFile/JarInputStream inconsistencies.
- Offline validators in PRIVATE Drive bundle use Python standard library only; negative tests mutate protected payload, signedData, signature, signing block, truncate, and alter ZIP manifest.
- Local regression results: APK v2 positive plus six negative = 7/7; ZIP positive plus two negative = 3/3.
- Both runtime ZIPs CRC PASS, manifest 176/176 each; ATLAS 175/175; JNI arithmetic oracle 81/81 per runtime, 162/162 aggregate.
- Cross-run 166 of 176 manifest-listed paths identical, 10 different; manifests themselves also different: 166 equal and 11 different across 177 total ZIP entries.

## Evidence boundaries / gates

- PASS_SCOPED: local raw archive byte preservation and SHA readback, ZIP CRC+manifest, RSA v2 signature/content digest, jarsigner v1 with warnings, JNI numeric oracle.
- TOKEN_VAZIO: independent ADB device install witness, official apksigner v2/v3 platform compatibility, trusted release cert, physical model stability, license clearance for public raw data, CLASS/CAMB/DESI posterior, external heldout comparison.
- This is V07 historical evidence. V08 successor cannot inherit physical execution proof from V07.
- SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM; SIGNED_APK != TRUSTED_RELEASE; APP_SELF_REPORT != EXTERNAL_DEVICE_ATTESTATION.

## High-information gates / rollback

1. G0 PASS: private byte custody + provider readback + exact SHA.
2. G1 PASS_SCOPED: v2 cryptographic independent check + negative tests.
3. G2 OPEN: official apksigner verify --verbose --print-certs and ADB witness of exact APK, with identity/permissions checks. If unavailable, keep typed absence.
4. G3 OPEN: independent V08 physical ZIP, exact source artifact/CI binding and deterministic 109-obligation parity without reinterpretation of V07.
5. G4 OPEN: preregister shared-likelihood DESI DR2 13x13 LCDM/CPL/RLL comparison, CLASS/CAMB, covariance/priors and heldout falsifiers under rights gate.
Rollback: close this draft without merge; Drive updates append-only supersession. Never rewrite raw historical archives.
R3 F_ok=byte custody+v2+10 adversarial tests; F_gap=device witness, platform verifier, scientific refutation; F_next=V08 exact-head independent witness and pinned prior-registered likelihood. claim_allowed=false.
