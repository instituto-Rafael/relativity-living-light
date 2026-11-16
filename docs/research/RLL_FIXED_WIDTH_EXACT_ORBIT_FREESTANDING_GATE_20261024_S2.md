# RLL / RAFAELIA — fixed-width freestanding exact-orbit successor (S2, 2026-10-24)

**State:** SOURCE_IMPLEMENTED / LOCAL_HOST_TESTS_PASS / CROSS_COMPILE_OBJECT_ONLY / EXACT_HEAD_CI_PENDING / REVIEW_PENDING / PHYSICAL_COUPLING_BLOCKED.
**Promotion:** HOLD; `claim_allowed=false`, `release_allowed=false`. This note supersedes only the CI-status and implementation-boundary part of `docs/research/RLL_EXACT_QUANTIZATION_TOPOLOGY_GATE_20261024.md`; no predecessor is erased.

## Authority and history
- Source producer: `instituto-Rafael/relativity-living-light`, base `rll/lab`; this change lives only in an unmerged working branch and a DRAFT pull request.
- Prior mathematical reference: `tools/rll_exact_quantized_orbit.py` from PR #1127; merge on 2026-10-24 20:09:24 UTC, merge SHA `3cffa22f72961521d9e207c810aec9b6b3d3897f`.
- PR #1127 merged despite `[NÃO PROMOVER]` labeling, with zero submitted GitHub reviews in the reviewed snapshot. This does **not** confer human scientific approval; this S2 document makes no attempt to reverse Git history or imply independent review.
- PR #1127 Python tests workflow #40121015157 completed success, including Run tests with auditable receipt; ten HEAD-associated workflow runs showed success. CI success is scoped to that earlier HEAD, not inherited by S2.

## Exact operator
For integer `b>0`, `n>=0`, `alpha=sqrt(3)/2`:
`k=floor(b*alpha^n)`. A bounded freestanding C kernel computes `k` using checked unsigned 64-bit products, bit shifts and an integer square root. It derives `g=gcd(b,k)`, cycle length `b/g`, sign `(-1)^(b-g)`. The header exports `rll_q_orbit_u32` and a typed status. A structural zero (valid `k=0`) is never conflated with a failure status.

## C ABI contract
- `RLL_Q_OK=0`: output `exact_step`, `cycles`, `vertices_per_cycle`, `permutation_sign`, `boundary_integer` are valid.
- `RLL_Q_INVALID_INPUT=1`: `base==0`; downstream MUST NOT consume numeric result fields.
- `RLL_Q_UNREPRESENTABLE=2`: conservative width/certification limit (including exponent >63, product/square-root preconditions); downstream MUST NOT consume numeric result fields.
- C core requires 32-bit unsigned int, 64-bit unsigned long long, no libc, no malloc/heap, no syscalls, no floats, no stdlib headers, no runtime self-tests. Host Python test harness is intentionally separate.
- This is *not* constant time. Fixed-width, bounded loops and no external symbols are demonstrated; actual ARM runtime/energy/power not measured.
- Conservative overflow refusal can occur even when a mathematical result exists; the caller must propagate typed uncertainty and may use the unbounded Python reference separately.

## Local evidence (scope-specific)
- Host test: `python -m unittest discover -s tests -p 'test_rll_quantized_orbit_u32_freestanding.py' -v` -> 3 methods PASS in a scoped worktree.
- Host clang: `-std=c11 -ffreestanding -fno-builtin -fno-stack-protector -shared -nostdlib -Wl,-z,defs -Wall -Wextra -Werror`, C ABI callable with Python `ctypes` and no `nm -u` unresolved symbols on that host.
- Matrix: 13 bases x 32 exponents, successful cases compared with Python exact reference; failed-width cases remain `UNREPRESENTABLE`. Negative/boundary tests include `(b,n)=(100,2)` -> 75, 25 cycles, odd permutation and `(16,4)` -> 9.
- Cross compilation (not device execution): `clang --target=armv7a-linux-androideabi29 -O2 -ffreestanding -fno-builtin -c` and `clang --target=aarch64-linux-android29 ... -c` each produced an object locally; `nm -u` showed no undefined symbols.
- S2 new-head GitHub workflow results, full-suite regression, memory/performance measurements, ARM physical execution, and independent review: `TOKEN_VAZIO` until exact evidence observed. No release claim.

## Applicability
Read-only formal gate for integer quantizers and cyclic graphs. Forbidden without separately authorized reviewed contract: modifying RLL likelihoods/CMB/DESI fits, physical quantities, geodesic solvers, toroidal dynamics, cosmological claims, runtime defaults, workflows or release policy.

## Falsifiers and rollback
F1: an `RLL_Q_OK` result mismatches integer-oracle `k`, GCD, cycle length, parity or exact boundary. F2: a compilation introduces unresolved libc/EABI symbols or overflow silently produces `RLL_Q_OK`. F3: `INVALID_INPUT` or `UNREPRESENTABLE` is consumed as numeric zero. F4: branch/CI or deployment claims are inherited without exact SHA and independent evidence.

Rollback is a revert of only these four additive S2 files **after human review**, retaining branch, PR, SHA, evidence history and predecessors; no source deletion. R3: F_ok=local code+host tests+cross-compile objects; F_gap=HEAD CI, provider validation, external reviewer, hardware, physics; F_next=exact-head CI readback and independently approved test, then optional ARM device A/B benchmark.
