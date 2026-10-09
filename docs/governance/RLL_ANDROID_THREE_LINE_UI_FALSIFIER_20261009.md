# RLL Android: from three-line JNI smoke view to interactive diagnostic

**Date:** 2026-10-09. **Scope:** hosted Android interface only; `claim_allowed=false`.

## User-observed source falsifier
The original `app/src/main/java/org/rafaelia/rll/MainActivity.java` (blob `68f6665ba7aae60f627af3450d5017fbe47dcfb1`) created exactly one `TextView`:
```
RLL native runtime OK
arch=<number>
score=<number>
```
This is intentional JNI smoke-test source, **not** a functional science application. Earlier "APK compiled" statements must not imply any dashboard, formulas, data, sensors or observations were implemented.

## Small, reversible evolution
- Native `Activity` + `ScrollView` + four descriptive panels, no UI frameworks, no external dependency or new manifest permissions.
- Runtime status and detected architecture, Android ABI label, four distinct JNI score probes with expected results calculated independently in Java.
- Editable bounded integers (`|x|,|y| <= 10000`) and an on-demand native C calculation.
- Copy an on-device receipt only when the user presses the button; includes explicit `claim_allowed=false`, scoped gates and unmeasured dimensions. No network export.
- Native `kernel_bridge.c`, `KernelBridge.java`, JNI, gradle, signing workflow, model equations and permissions **unchanged**. Android framework dependency is explicit and cannot be called a full freestanding app.
- If JNI load/call fails, show typed FAIL/TOKEN_VAZIO instead of a fabricated PASS.

## Test, provenance and gates
- New source-side pytest guards verify real buttons, their callbacks, input bounds, no added network usage, source limitations and unchanged kernel bridge.
- The existing Android CI `:app:assembleDebug :app:assembleValidationUnsigned` must succeed on the exact feature HEAD before accepting build claims; then verify ZIP/APK hashes + on-device launch and button behavior on arm32/arm64, keeping signing and runtime separate.
- Do not claim any of the missing scientific products (CLASS/CAMB, cosmology fitted H(z), CMB, fσ8, GPS, sensor readout, ambisonics).
- Physical screen visual inspection remains `TOKEN_VAZIO_DEVICE_NOT_RUN`.

**F_ok:** user report corresponds to exact original Java source, UI path dedicated to local diagnostics. **F_gap:** screenshot proof, device boot, JNI ABI mismatch cases and real science capabilities. **F_next:** inspect exact-head CI and APK before any distribution. **Rollback:** revert `MainActivity.java`, new test and this note only.
