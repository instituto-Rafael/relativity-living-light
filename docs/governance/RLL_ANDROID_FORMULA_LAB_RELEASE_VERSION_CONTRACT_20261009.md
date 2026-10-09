# RLL Android Formula Lab v0.2: source → units → calculation → falsifier → receipt

**Release candidate:** Android versionCode 2 / versionName 0.2.0 by default. **Status:** source implemented, exact-head CI pending; `claim_allowed=false`. Parent: merged PR #1090 with 4-section native JNI diagnostic UI.

## Governance and authorial boundaries
The first formula registry is a **restricted executable subset**, not a promise to execute every expression in the full RLL Papers/Matemática/Teoremas catalogue. Original references are:
- `data/pipelines/structure_d/joint_real_likelihood.py` source blob `53c8f373f878c9080148c64564654d3efe684cea`; foreground E²/H(z), growth-index proxy, drag sound horizon power-law and BAO distance conventions.
- `scripts/check_rll_background.py` source blob `c53fb475e68ffa9b960cb2a186c9df811654d18a`; transition f, density factor, documented vs conserved pressure and continuity residual, local CPL mapping.
- `rafaelmeloreisnovo/EstudioAudio` studied **as design reference only**: native DSP core, Java hosted boundary and CI-injected version/SHA provenance. **No code or audio samples copied**. Its `LICENSE_RESEARCH_COMMERCIAL.md` is NOT treated as automatic incorporation permission.
- The Android formula evaluator is `FormulaEngine.java` written as standalone hosted Java 8 source (no Android classes). `FormulaLabView.java` is separate Android UI, no extra dependencies. Native C kernel and `KernelBridge.java` unchanged.
- Each emitted receipt distinguishes SOURCE, USER_INPUT, COMPUTATION, ALGEBRAIC_CHECK, PROXY and UNMEASURED. A checked invariant is NOT a scientific proof, nor a user-entered value a trusted DESI/Planck observation.

## Supported input and source-bound formula families
`Model` = `LCDM | WCDM | CPL | RLL`. Inputs: `z, H0, Ωm, ΩΛ, Ωs0, zt, wt, w, w0, wa, Ωb h², sigma8`. Optional, linked pair `Hobs, σH`. All numeric finite and bounded, including `wt >= 0.001`, `0<=z<=10`. `ΩΛ` is FREE as in original historical fit, but UI offers a deliberate **E²(0)=1** closure calculation and reports when `E²(0)!=1`.

| IDs | Value / unit | Evidence gate |
|---|---|---|
| COS-E2-*, COS-HZ, COS-E2-ZERO | E²(z) unitless / H(z) km/s/Mpc / E²(0) | finite >0, check normalization versus H0 |
| COS-OMZ, COS-FSIGMA8-PROXY | Ωm(z), sigma8 Ωm(z)^0.55 (unitless) | proxy, **not** ODE growth D(z) |
| COS-OM-LAMBDA-CLOSURE | ΩΛ required to impose E²(0)=1 | no auto modification of inputs |
| COS-RD-PROXY | drag sound horizon Mpc | calibrated power law, **not** CMB r_s(z*) |
| COS-DM-FLAT, COS-DH, COS-DM-RD, COS-DH-RD, COS-DV-RD | distance metrics Mpc and BAO ratios unitless | flat curvature only; Simpson 128 vs 256 refinement delta |
| RLL-F-TRANSITION, RLL-RHO-FACTOR, RLL-OMEGA-S | transition, density, fraction | only RLL sector |
| RLL-W-DOC, RLL-W-CONSERVED | pressure ratios | distinguish non-conserved documented vs closure-imposed conserved form |
| RLL-CONTINUITY-DOC, RLL-CONTINUITY-CONS | dimensionless continuity residuals | algebraic identity vs hypothesis, no physics superiority claim |
| RLL-CPL-W0-LOCAL, RLL-CPL-WA-DOC, RLL-CPL-WA-CONS | first-order CPL mapping | local only, not a global equivalence |
| COS-H-RESIDUAL, COS-H-CHI2-ONE | input normalized residual and *single point* chi² | only if paired Hobs, σH supplied; **USER_INPUT** |
| COS-CMB-RS, COS-GROWTH-ODE, COS-JOINT-FIT | **typed absence**, not invented | CLASS/CAMB, ODE perturbations, official covariances and full fit not run |

Every entry has formula ID, expression, unit, source path, computed vs typed gap state, numerical result and caveat. The visible UI can show all, pick one, vary `z` on an 11-point grid, intentionally normalize ΩΛ, and copy a SHA-256 receipt. No external data is silently fetched by the engine.

## Version and safe user update
Android versionCode is bumped from 1→2 and versionName from 0.1.0→0.2.0 with optional `RLL_ANDROID_VERSION_CODE` / `RLL_ANDROID_VERSION_NAME` CI environment parameters. Android checks GitHub **only** for releases of pattern `android-rll-v<N>`, whose asset is exactly `rll-android-release.apk`, uploaded with GitHub SHA-256 digest. GitHub's other `v4.22` *scientific* release cannot trigger an Android update. The newest matching revision must have a greater number than the currently installed one.

On launch, HTTPS check runs off the UI thread (4s timeouts, 256 KiB response cap), never downloads an APK or silently installs. When a matching published release exists, a user-visible dialog offers to open the **official GitHub release page**. Android's installer then requires the user's action and a compatible installed-package signature. `org.rafaelia.rll.debug` debug builds will not update the production `org.rafaelia.rll` package; ephemeral debug keystore signatures may also be incompatible across CI runs. A stable authorized release signing key, exact source and P0 rights checks are required for a real installable release.

Current RLL GitHub releases do not contain an Android APK asset matching this protocol. **AUTOMATIC_UPDATE_INSTALLED = false** until a signed APK is published and installed by the OS with user approval. No third-party updater, unknown-source privileges, root, APK scraping or auto-approval is added. The only added permission is normal `INTERNET` for user-visible GitHub update discovery; requests disclose IP to GitHub as ordinary network traffic.

## Reproducible tests / rollback
- New deterministic `javac` harness (`sh app/verify_formula_engine.sh`) tests flat normalization, ΛCDM↔wCDM/CPL reductions, null Ωs0 equivalence, conservation identity, numerical Simpson convergence, single-point H chi², domain failures, typed gaps and absence of fabricated observations.
- Exact-head Android workflow runs JVM harness **before Gradle** plus debug/unsigned ARMv7/AArch64 APK build.
- Python source tests audit panel wiring, receipt provenance, restrictive release tags/digest, permission scope and source contracts.
- True observational cosmology proof requires independent CLASS/CAMB, official data+covariance, fit rerun and licensed provenance.
- **F_gap:** continuous scientific model benchmark, true observation source attestation, physical Android screenshots/install, stable signed release, full catalog indexing, Papers/EstudioAudio licensing crossrepo, microphone/ambisonics integration (not attempted).
- **Rollback:** revert bounded eight new/changed paths in a feature PR; original C kernel/scientific code untouched. No automatic merge or unapproved release.
