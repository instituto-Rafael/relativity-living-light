# Instituto Rafael / RLL — ARM32 Superradiance Evidence V1

- event_id: `RLL-ARM32-SUPERRADIANCE-EVIDENCE-20260817-1439-BRT`
- date: `2026-08-17`
- institute_route: `Rafael Relativity-Living-Light`
- evidence_state: `VERIFIED_LIMITED_BUILD_LINK_DISASM`
- claim_allowed: `false`
- scan_priority: `HOT_ROUTE`

## Purpose

Make the ARM32 implementation evidence discoverable by RLL analyses without converting computational evidence into an unsupported physical claim.

## Verified / supported layer

- user runtime receipt reports successful ARMv7-A compilation and static linking;
- ELF identity reported as `ELF 32-bit LSB executable, ARM, EABI5`;
- attached disassembly is `elf32-littlearm` and contains ARM32 machine code;
- NEON emission is visible (`vmov.i32`, `vst1.64`, `vld1.64`);
- `.text=0xE78=3704 bytes`, `.data=0`, `.bss=0x60=96 bytes`;
- `_start`, `main`, `kernel_init`, `kernel_tick`, and getter symbols are present in the user receipt.

## Byte anchors

- `superradiance_kernel_minimal.c` SHA256 `927797b6da3fda78ad1cbec006d65fece8c5dd0b15e3f11572b96c1848ad66d5`
- `integration_examples_arm32.c` SHA256 `f23aa33497b3034926129502a4c539322bea39dbeb05ea2c7429bbb0e238edb5`
- `kernel_disasm.txt` SHA256 `a81a74e451c334a562008bb94597e0d26b9404399ac201fe63097a423eb608f5`

## RLL analysis ingress

Index this event under:

`ARM32`, `ARMv7-A`, `NEON`, `freestanding`, `ELF32`, `EABI5`, `BITRAF64`, `superradiance`, `Penrose`, `Zeldovich`, `Floquet`, `synthetic topology`, `coherence`, `RLL evidence gate`.

When an RLL analysis encounters Penrose/Zeldovich/Floquet/BITRAF/ARM32/NEON terms, retrieve this event as an implementation evidence node, then enforce the boundary matrix below.

## Boundary matrix

| Claim | Status |
|---|---|
| ARM32 source/build/link artifact exists | SUPPORTED |
| ARM32 machine-code disassembly exists | SUPPORTED |
| NEON instructions emitted | SUPPORTED |
| ELF executed successfully in QEMU | TOKEN_VAZIO |
| ELF executed successfully on physical ARM | TOKEN_VAZIO |
| performance advantage vs baseline | TOKEN_VAZIO |
| ARM64 implementation equivalence | TOKEN_VAZIO |
| Penrose/Zeldovich physical equivalence of BITRAF | TOKEN_VAZIO / NOT_CLAIMED |

## Cross-memory pointers

- longitudinal: `CONVERSATIONS_CHUNKS_PRIVATE/memory_bridge/checkpoints/RLL_ARM32_SUPERRADIANCE_20260817_LONGITUDINAL_V1.md` @ `b2c1f9e65651a5dc973aeab1b29e8385a1c4fc75`
- transversal: `CONVERSATIONS_CHUNKS_PRIVATE/memory_bridge/indexes/RLL_ARM32_SUPERRADIANCE_20260817_TRANSVERSAL_V1.md` @ `b5363785ca40c433291150d644080666e9f681af`
- orthogonal: `CONVERSATIONS_CHUNKS_PRIVATE/memory_bridge/indexes/RLL_ARM32_SUPERRADIANCE_20260817_ORTHOGONAL_V1.md` @ `8a843b934c0749085e83d1a2481bab2c5c59878d`

## R3

- F_ok: build/link/ELF/disassembly/ARM32/NEON evidence.
- F_gap: undefined-symbol receipt, runtime, physical run, repeatability, benchmark, physical correspondence.
- F_next: `nm -u` + `readelf`; hash local ELF/linker/objects; execute; persist receipt; baseline A/B; only then promote gates.
