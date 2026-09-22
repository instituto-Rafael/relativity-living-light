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
