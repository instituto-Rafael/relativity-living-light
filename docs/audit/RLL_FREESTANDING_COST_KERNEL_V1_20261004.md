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

## First observed execution — 2026-10-04

Head observed: `5daa6a395460d3fd9d0a6cdd79df40f2185d0ac2`.

GitHub Actions Python tests run `37196355533`, job `111418944780` reported:

- checkout: `PASS`;
- `Build and execute freestanding cost kernel`: `PASS`;
- freestanding compile path executed before the hosted Python test environment;
- no scientific claim promotion was introduced.

Therefore the kernel execution token advances from:

`TOKEN_VAZIO_EXECUTION`

for the initial authored state to:

`FREESTANDING_KERNEL_EXECUTION_OBSERVED_PASS`

for that exact head and job only.

This does **not** close the PR-level non-regression gate. On the same head the workflow architecture/reconciliation gates found a separate repository workflow-inventory drift:

- contract expected active workflows: `110`;
- executable workflows discovered independently by strict validators: `111`;
- architecture YAML parsing itself: `PASS`;
- workflow inventory reconciliation: `MISMATCH`.

The repository synchronizer contract states that its write mode edits only `inventory.active_workflows`; it does not modify claims, branch settings, commits, or other workflow semantics.

Overall PR state after this first observation:

`TOKEN_VAZIO_FINAL_HEAD_NON_REGRESSION`

Energy remains:

`ENERGY_MEASUREMENT = TOKEN_VAZIO_MEASUREMENT`

until actual power telemetry is supplied by a measured source.
