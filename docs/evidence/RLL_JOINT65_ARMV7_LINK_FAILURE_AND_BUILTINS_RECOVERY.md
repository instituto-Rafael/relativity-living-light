# RLL Joint65 ARMv7 — freestanding link failure and static-builtins recovery

Observed on physical ARMv7 Termux after successful 179K selective bootstrap.

## Falsifier

The strict direct-`ld.lld` link failed with unresolved compiler ABI helpers:

```text
__aeabi_memcpy8
__aeabi_l2d
__aeabi_d2lz
__aeabi_ldivmod
__aeabi_uldivmod
```

Provenance of the helpers:
- `__aeabi_memcpy8`: structure copies/returns in the model context and entry;
- `__aeabi_l2d` / `__aeabi_d2lz`: Q16 int64 ↔ double bridge in `rll_canonical_real_models.c`;
- `__aeabi_ldivmod` / `__aeabi_uldivmod`: 64-bit fixed-point/parser divisions.

Therefore the prior label `strict no-runtime freestanding` is falsified for the Joint65 source set as currently written.

## Recovery gate

`scripts/run_rll_joint65_armv7_static_builtins_gate.sh` keeps:
- no libc/bionic;
- no dynamic loader;
- no DT_NEEDED;
- all input datasets embedded;
- original pinned production source.

It adds only:
- Clang's statically linked compiler-rt builtins archive already installed with the toolchain;
- a local byte-copy implementation for `__aeabi_memcpy{,4,8}`.

A PASS here proves physical execution of the original Joint65 source with **static toolchain runtime**, not strict runtime-free execution.

States:

```text
RLL_JOINT65_SELECTIVE_BOOTSTRAP_ARMV7=PASS
RLL_JOINT65_STRICT_NO_RUNTIME_LINK=FAIL
RLL_JOINT65_STATIC_BUILTINS_PHYSICAL=PENDING
RLL_JOINT65_STRICT_NO_RUNTIME_PHYSICAL=TOKEN_VAZIO
```

The strict hardening path remains separate: remove 64-bit compiler divisions, remove struct-copy libcalls and narrow the Q16↔double bridge to 32-bit VFP conversions before claiming runtime-free execution.


## Physical recovery observed — PASS

A later physical Termux/ARMv7 run closed the static-builtins recovery gate:

```text
timestamp=2026-09-22T18:37:56-03:00
arch=armv7l
artifact_sha256=4ea887b8a679dd0db6f5ad36ec63030a5fed6ed0affd7a8c6b229f3452020a2b
compiler_rt_builtins_sha256=dcb6cfe8f1afa5bb37b935173e7b90709cb474c3d6b6104e8b8f386a5f108e60
local_runtime_shim_sha256=b3462dd2612f79428e7415d52b8b731e3f0b1342ce4c9dc59a7cb403e0a167cb
execution_exit=0
undefined_symbols=0
PT_INTERP=0
DT_NEEDED=0
libc_like_undefined=0
aeabi_undefined=NONE
status=PASS
receipt_sha256=db822ebf5152f21b9e57faa4af7c0df68299ec08a56aa7a3142fdad0a067639b
```

Promotion:

```text
RLL_JOINT65_STATIC_BUILTINS_PHYSICAL=PASS
RLL_JOINT65_STRICT_NO_RUNTIME_LINK=FAIL
RLL_JOINT65_STRICT_NO_RUNTIME_PHYSICAL=TOKEN_VAZIO
```

The repository runner was subsequently hardened to include the stack-check symbols required by the Termux compiler-rt archive. This does not convert the route into a strict zero-runtime build; compiler-rt remains statically linked by design.

The executed entry returns a fail bitmask over the 65-row shape, CMB covariance path, pinned Q16 chi-square values, delta and claim gate. Thus `execution_exit=0` means those checks passed for the executed artifact. The receipt stores the expected values rather than directly printing the computed values; future receipt formats should add an observed-value witness.
