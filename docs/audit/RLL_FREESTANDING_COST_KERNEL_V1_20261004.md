# RLL Freestanding Cost Kernel V1 — receipt

Date: 2026-10-04
State: IMPLEMENTED_UNEXECUTED
Claim allowed: false

## Purpose

Provide a lowest-layer arithmetic kernel for CI cost/completion telemetry without hosted-runtime assumptions inside the kernel itself.

## Kernel contract

`tools/ci/rll_freestanding_cost_kernel.c`

- C11 freestanding translation unit;
- no headers;
- no libc;
- no heap;
- no I/O;
- no syscalls;
- no floating point;
- integer-only arithmetic;
- bounded inputs to keep multiplication inside unsigned 64-bit range.

The hosted verifier exists only to execute the pure kernel and expose a process PASS/FAIL result in GitHub Actions. It is not part of the freestanding kernel.

## Calculations

The kernel directly computes:

- saved runner time in milliseconds;
- gain in permille;
- completed-test throughput in milli-tests/second;
- energy in millijoules only when an externally measured average power in milliwatts is supplied.

Energy is not inferred from runner time.

If no real power measurement exists:

`ENERGY_MEASUREMENT = TOKEN_VAZIO_MEASUREMENT`

## Baseline verification vectors

Observed prior values are used only as deterministic arithmetic vectors:

- Claim Boundary baseline: 301403 ms;
- focused Claim Boundary: 34583 ms;
- expected saved time: 266820 ms;
- expected gain: 885 permille;
- canonical Python run: 1727 tests / 285030 ms;
- expected throughput: 6059 milli-tests/s.

A synthetic unit conversion vector checks the energy formula using an explicitly supplied measured-power placeholder value. It does not assert that GitHub runner power was 100 W.

## Non-regression boundary

This kernel does not decide whether a full suite may be skipped.

`skip_full_suite_allowed=false` remains controlled by the existing fail-closed quality monitor.

## Execution gate

Until CI compiles the freestanding object, proves no unresolved external symbols, links the hosted verifier, and executes it successfully:

`TOKEN_VAZIO_EXECUTION`

SOURCE != CONFIG != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
