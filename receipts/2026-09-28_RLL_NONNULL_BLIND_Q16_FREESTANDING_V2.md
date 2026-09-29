# Receipt — RLL Non-null Blind Recovery Q16 Freestanding V2

Date: 2026-09-28
claim_allowed: false
Provider run: 36502520567
Provider job: 109196432925
Tested branch head: 4e497b670166218609ce59abaef39c2cea063afe

## Materialized runtime

core/lowlevel_runtime/c/rll_nonnull_blind_q16_freestanding.c

Observed runtime properties:
- one translation unit
- no hosted include
- no external declaration
- no libc/stdlib/stdio/string/math runtime
- no heap/malloc/free/GC
- no structs/classes/function pointers
- no runtime file parser
- Q16.16 integer arithmetic
- flat static arrays + integer offsets
- _start entry
- direct Linux write/exit syscall boundary

## x86_64 evidence

The provider compiled with clang freestanding/no-builtin/nostdlib, statically linked with GNU ld, observed empty nm -u, no INTERP and no NEEDED, then executed the ELF with return code zero.

Exact provider line:
RLLNONNULLQ16V2 state=PASS exact=1311,65536,19661 stress=1311,65536,21299 stress_delta=0,0,1638 stress_gate=DIAGNOSTIC null_os=0 grid_evals=1782 claim_allowed=0
PROGRAM_RC=0
PASS_X86_64_STATIC_EXECUTION

### Exact non-null arm

Injected and recovered:
Omega_s0 = 1311 Q16 ~= 0.02000427
z_t      = 65536 Q16 = 1.0
w_t      = 19661 Q16 ~= 0.30000305

Exact arm chi-square is zero by construction and the injected grid cell is recovered.

### Deterministic stress arm

Fixed perturbation sigma*{-2,-1,0,1,2}/32 produced:
recovered = 1311,65536,21299
delta     = 0,0,1638

Omega_s0 and z_t remain at the injected cell, while w_t moves one frozen grid cell from approximately 0.3000 to 0.3250.

This observation is preserved as a diagnostic. V1's exact-stress requirement is superseded by contract V2; no injection, noise vector, grid cell or data point was retuned to make the result green.

### Null arm

recovered Omega_s0 = 0

No assertion is made for z_t/w_t at null amplitude because those shape parameters are non-identifiable when the RLL sector vanishes.

## ARMv7 evidence

The identical C source was cross-compiled without runtime headers/libraries.
Provider observations:
Class: ELF32
Machine: ARM
PASS_ARMV7_FREESTANDING_OBJECT
ARMV7_STATIC_LINK=TOKEN_VAZIO_TOOLCHAIN_LINKER
ARMV7_PHYSICAL_EXECUTION=TOKEN_VAZIO

The ARM object passed the undefined-symbol gate, including no unresolved __aeabi_*.

No claim is made for a linked ARM executable or physical ARM execution in this receipt.

## Interpretation boundary

PASS_X86_64_STATIC_EXECUTION != PHYSICAL_ARMV7_EXECUTION
PASS_ARMV7_OBJECT != PASS_ARMV7_STATIC_LINK
SYNTHETIC_RECOVERY != REAL_DATA_MODEL_SELECTION
SAME_BINARY_RECOVERY != INDEPENDENT_REPLICATION
STRESS_DIAGNOSTIC != PROMOTION_GATE
LOWLEVEL_PASS != COSMOLOGICAL_VALIDATION
claim_allowed=false

## R3

F_ok = single-unit freestanding source + x86_64 static build/link/execute PASS + nm -u empty + no INTERP/NEEDED + exact non-null recovery PASS + null-boundary recovery PASS + stress sensitivity preserved + ARMv7 ELF32 object PASS + no unresolved ARM helper symbols.

F_gap = ARMv7 static link on an ARM-capable linker + physical ARMv7 execution + generator/recovery separation + independent reimplementation + held-out real-data discrimination.

F_next = run this exact source on the physical ARMv7 canonical runner -> freeze ELF/source hashes -> split generator and recovery into independently built executables -> only then bind recovered diagnostics to held-out observational data.
