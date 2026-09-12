# RLL CI Quality/Cost Monitor V1 — append-only receipt

Date: 2026-09-12
Authority: instituto-Rafael/relativity-living-light
State: IMPLEMENTED_UNTESTED
Claim allowed: false

## Observed baseline

Exact jobs supplied for review:

- Claim Boundary Quality Gates
  - run: 34714586686
  - job: 103609421567
  - conclusion: SUCCESS
  - observed wall time from first to last log timestamp: ~301.4 s
  - important observation: the workflow executed `python -m pytest -q tests`, duplicating the repository-wide suite.

- Python tests
  - run: 34714586584
  - job: 103609421352
  - conclusion: SUCCESS
  - observed wall time from first to last log timestamp: ~264.3 s
  - pytest result: 1720 passed + 12 subtests
  - pytest time: 228.58 s
  - this workflow is retained as the canonical full-suite authority.

## Refactor

The optimization is non-compensatory:

1. Python tests remains full and canonical.
2. Claim Boundary retains:
   - validation-script compilation;
   - direct claim-boundary check;
   - seed artifact contract check;
   - deterministic audit prerequisites;
   - only the two focused regression files explicitly documented by the gate:
     - tests/test_real_seed_utils.py
     - tests/test_orbital_outputs.py
3. Claim Boundary superseded runs on the same ref may be cancelled.
4. pip cache is enabled for Claim Boundary.
5. A stdlib-only quality execution monitor records:
   - changed-file count;
   - critical/sensitive/focused counts;
   - risk class;
   - JUnit test count/failures/time;
   - candidate TTL state;
   - privacy/security boundaries.

## TTL policy

V1 TTL is advisory only.

Candidate TTL: 21600 s (6 h).

If the last full-suite PASS timestamp is unavailable:

`TOKEN_VAZIO_LAST_FULL_PASS`

and:

`skip_full_suite_allowed=false`.

Even when a TTL later becomes observable, V1 does not skip the canonical full suite.
This prevents an optimization heuristic from silently becoming a scientific or governance gate.

## Privacy and security

The monitor reads path names, git refs and JUnit metadata only.

It does not:
- read changed file contents for classification;
- dump environment variables;
- read secret values;
- upload repository contents beyond existing CI artifacts.

## Expected impact

The old design ran the full test suite in both reviewed jobs.
The new design should remove one redundant full-suite execution from Claim Boundary.

Expected time/cost reduction is not promoted to evidence until the new exact-head workflow is observed.

State:
`TOKEN_VAZIO_POST_REFACTOR_TIMELAPSE`

## Rollback

Revert the focused Claim Boundary test step to the prior full-suite command.
The Python tests authority is untouched, so rollback does not require reconstructing lost coverage.

SOURCE != CONFIG != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
