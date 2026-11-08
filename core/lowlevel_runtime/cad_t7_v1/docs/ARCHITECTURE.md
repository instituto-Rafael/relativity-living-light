# RLL CAD / Q16 / T7 — module boundaries

```
       SOURCE — immutable equations, material assumptions, units
                              │
                   T7 sample of 7 parameters
                              │
         freestanding Q16 core (no libc, malloc, syscalls)
              ┌───────────────┼───────────────┐
       statics + truss   CRC32 software    SVG buffer writer
              │          NEON add4 helper     │
          Q16 output     (optional caps)    SVG memory bytes
              └───────────────┼───────────────┘
                     API / ABI (pure C)
                              │
             ┌────────────────┴─────────────────┐
    Hosted test/orchestration                  Android adapter
    8 pthread workers                         Java class -> DEX -> ART
    42 disjoint records                       JNI -> native ELF .so
    JSON/CSV/LE binary/SVG                     (NOT BUILT as APK)
             └────────────────┬─────────────────┘
                     human independent review
```

- **Core** `core/rll_cad.c`, `core/rll_cad_svg.c`, `core/rll_cad.h`: no libc, no heap, no static mutable state, no OS. Input/output buffers and capacities provided by caller; fails closed on malformed inputs. 64-bit software division for ARMv7 freestanding. Units, rounding and model constraints are part of ABI.
- **NEON**: optional ARMv7 128-bit `vadd.i32` four-value helper compiled and assembly-inspected, not a measured speedup of the nonlinear structural evaluation. Separate scalar fallback. A 32-bit device requires CPU feature check on the *host* before invoking NEON.
- **CRC**: software IEEE CRC32 tested with `123456789 -> CBF43926`. AArch64 `crc32b` variant is compiled only with `-march=armv8-a+crc`; it is NEVER called without the host probing a CPU feature bit. **No hardware CRC acceleration benchmark or runtime test**.
- **ELF**: `build/librllcad_android_armv7.so` is a cross-linked ELF32 ARM shared object, not Android executable DEX. `build/librllcad_android_arm64.so` is ELF64 AArch64. Both were statically linked `-nostdlib` and have no `DT_NEEDED` entries; no Android physical device has executed them in this build.
- **DEX/ART**: `android/RllCadBridge.java` is host-compiled class source; Android needs D8 and APK packaging; JNI glue `android/rll_cad_jni.c` requires platform header and NDK. DEX bytecode is generated from Java; ELF binary is loaded by ART's `System.loadLibrary` via JNI. NOT an interpreter-free bare-metal Android app.
- **L2**: 42× shared-array work set was measured as **5208 bytes** in 8 hosted worker threads. It is deliberately compact, but the application **cannot deterministically pin or schedule data in L2**. This footprint alone does not prove cache hits or multicore speedup.
- **8 workers**: hosted `pthread` dispatch to eight worker threads, 42 disjoint evaluation slots, no heap in numerical core; exact byte parity versus sequential outputs. Physical core count/affinity and energy measurements NOT_RUN; host threading does not satisfy a pure bare-metal OS-free scheduler.
- **Host persistence**: `host/demo.c` is a separate stdio utility; `tools/representations.py` does compression/JSON/SVG metadata and explicit lossless roundtrip. They do not alter the core's syscall-free claim.

## Compression experiment — same 42 canonical Q16 records

- `results/records42_canonical.json`: sorted-key compact JSON array, one record per T7 point.
- `results/records42.csv`: lossless 30-integer row representation with a schema header.
- `results/records42_le_q16.bin`: little-endian header `RLLQ16V1` + `<uint32 count=42>` + 42×30 little-endian signed 32-bit ints. **An external field-order/schema is required** to interpret the binary; see `tools/representations.py` and `results/records42.csv` header.
- `svg/design_00.svg` through `svg/design_41.svg`: graphical view and exact canonical JSON metadata inside each SVG. Each individual SVG is larger than its JSON because it has vector drawing instructions; concatenating the 42 SVGs yields the original 42 records exactly by parsing their metadata.
- `results/compression_42_compositions.csv`: source bytes, Shannon plug-in **byte** entropy, Zstandard -19/gzip -9/xz-6, roundtrip. Distinguish **absolute compactness** from compression *percentage*; highly repetitive SVG can compress by 90% and still be much larger than compressed JSON or packed binary.

These are representations of the **same synthetic numerical record data**, although SVG has extra drawable presentation and sidecar schema metadata is needed for packed binary. Shannon H(byte) is not thermodynamic entropy, engineering safety or a seven-dimensional spacetime measurement.

No backdoor into existing RLL cosmological claims: G4/G5 likelihood, ΛCDM, observational facts and physical RLL validation remain unchanged.
