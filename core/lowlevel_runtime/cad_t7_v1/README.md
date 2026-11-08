# RAFAELIA Ω — T7-CAD/Q16 freestanding engineering prototype V1

This is an editable SVG CAD **mathematical demo** over a 2D, three-member, pin-jointed truss. 7 parameters select 42 reproducible configurations within an abstract toroidal parameter space T⁷. It is **NOT** a validated bridge, nor a full 7D physical mechanics simulator. All dimensions are measured in millimetres. Baseline diagonal slope is exactly 45 degrees; other angles are represented through tangent, not unsupported transcendental calculations.

## Artifacts

- [svg/bridge.svg](svg/bridge.svg): generated vector structure, actual model circular-bar diameters as stroke widths and physical mm viewBox units; fully editable SVG.
- [svg/design_00.svg ... design_41.svg](svg/): 42 parameterized designs, each with an embedded canonical numeric record for exact reconstruction.
- [results/models42.json](results/models42.json): 42 Q16 samples with units and exclusions.
- [results/compression_42_compositions.csv](results/compression_42_compositions.csv): CSV/JSON/LE packed/SVG data sizes, compressor ratios and byte entropy.
- [results/records42_le_q16.bin](results/records42_le_q16.bin): fixed-order packed records, not self-describing without schema.
- [core/rll_cad.c](core/rll_cad.c), [core/rll_cad_svg.c](core/rll_cad_svg.c), [core/rll_cad.h](core/rll_cad.h): freestanding, Q16.16, bounded buffers, no libc/malloc/syscalls.
- [build/librllcad_android_armv7.so](build/librllcad_android_armv7.so), [build/librllcad_android_arm64.so](build/librllcad_android_arm64.so): compiled Android-targeted ELF32/ELF64 native kernel shared objects with no `DT_NEEDED`, but **not device-tested** and not a functioning Android app without JNI.
- [android/](android/): Java/DEX-facing source and JNI adapter (not Android DEX or APK build).
- [docs/ENGINEERING_CONTRACT.md](docs/ENGINEERING_CONTRACT.md): load assumptions, equations, units, limits, falsifiers.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): L2-workset, NEON, CRC32, pthread host and DEX separation.

## Computational baseline

Illustrative three-member triangular truss: span **1000 mm**, height **500 mm**; diagonal circle area **500 mm²**, tie area **300 mm²**; ideal Young modulus **200 GPa**, yield stress **250 MPa**; apex vertical load **1 kN**, ΔT **20 K**, α **12×10⁻⁶/K**.

Calculated with Q16.16 and independently checked against a double-precision analytic reference:

| Metric | Q16 result (approx) |
|---|---:|
| Diagonal compression each | 0.70709 kN |
| Tie tension | 0.50000 kN |
| Diagonal nominal stress | 1.41418 MPa |
| Vertical apex displacement | 0.01123 mm |
| Idealized Euler pinned-pinned limit each | 78.5352 kN |
| Unrestrained thermal expansion across span | 0.23999 mm |
| Yield/deflection/buckling safety for a real bridge | **NOT CERTIFIED** |

Linear elastic pin-jointed assumptions. **Shear, torsion, beam bending, restrained thermal forces, fatigue and code checks are NOT calculated.** An actual truss cannot be built safely from these outputs. Simulated values are not observational scientific evidence.

## Build and verify (Linux x86-64 host)

```
./build.sh
```

Requirements: clang/ld.lld, Python 3 stdlib, zstd, pthreads on host. Builds a Linux test harness and shared object; generates 42 SVGs and three alternative encodings; tests independent double oracle (all 42), CRC32 IEEE test vector, guarded invalid inputs, 8 hosted worker threads compared with serial, SVG roundtrip, byte-packed/CSV/JSON parity, ARMv7 and AArch64 cross-ELF. Cross-architecture compilation is **not physical device execution**. Advanced SIMD CRC hardware outputs are assembly-inspected only; the current numerical solver itself is scalar.

For Android use a proper NDK+ART/DEX/JNI build. Pure freestanding ELF cannot itself be executed as a DEX class. Hardware feature probes and eight-core scheduling belong to the hosted layer, not the bare-metal kernel.

## Provenance, compression, limitations

The repo's prior `RLL_DYNAMIC_STRUCTURAL_GEOMETRY_CONTEXT_V1.json` and `RLL_ADAPTIVE_GEOMETRY_FEATURE_LAYER_V1.json` explicitly distinguish diagnostic parameter geometry from physical metrics. This work consumes those contracts; it does not claim a physical T⁷ universe, proof of RLL cosmology, or stability of any real structure.

`SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM`; `claim_allowed=false`. Numerically equivalent representations are confirmed by exact 42-record roundtrip; **the SVG representation includes extra visual instructions**, while the binary representation needs the external field schema. Compressed percentages do not measure physical thermodynamic entropy.

**R3 = <freestanding ELF arithmetic and SVG bridge model, actual structural/material/hardware verification NOT_RUN, independent FEA/beam models/Android DEX and hardware tests next>.**
