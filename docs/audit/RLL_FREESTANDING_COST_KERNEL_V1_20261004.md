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

## Post-merge revalidation target — append-only

Merged implementation authority:

- PR: `#1050`
- `rll/lab` merge SHA: `ff5f06613051b5e39874816f003277be39d01e7f`
- merge parents:
  - current governed base at merge time: `2666fe99a843ba66887b90548ce01d54437f35fc`
  - freestanding implementation head: `5daa6a395460d3fd9d0a6cdd79df40f2185d0ac2`
- workflow contract observed on the merged base: `inventory.active_workflows = 113`.

This append-only delta intentionally changes documentation only. Its pull-request CI is used to re-execute the already-merged freestanding kernel against the governed post-merge tree.

Required evidence before promoting this validation receipt:

- freestanding object compilation: `PASS`;
- unresolved external symbols: `0`;
- hosted arithmetic verifier: `PASS`;
- canonical Python suite: `PASS`;
- workflow contract reconciliation: `PASS`;
- workflow architecture gates: `PASS`.

Until those checks are observed on the validation head:

`POST_MERGE_REVALIDATION = TOKEN_VAZIO_EXECUTION`

Energy remains:

`ENERGY_MEASUREMENT = TOKEN_VAZIO_MEASUREMENT`

No timing value, CPU model, or runner duration is converted to joules without an actual power measurement source.
