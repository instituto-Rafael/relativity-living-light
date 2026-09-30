# RLL Python Test Dependency Repair — append-only receipt

Date: 2026-09-12
Target: PR #884 / branch `science/flat-closure-successor-v1-20260912`
State at diagnosis: Python tests failed; flat-closure E0 gate passed.
Claim allowed: false.

## SOURCE

Observed GitHub Actions run `34706599074` on head `046b8bb5f05c8990298156f60aa226ad5a73ec6b`.

Result:
- 1663 tests passed;
- 20 tests failed;
- every failure came from `tests/test_rll_academic_safety_route56.py`;
- common root cause: missing `results/audit/rll_real_data_evidence_bridge.json`.

The Route56 test reads:
- `data/governance/RLL_ACADEMIC_SAFETY_ROUTE56_V1.json`;
- `results/audit/rll_real_data_evidence_bridge.json`;
- `results/audit/rll_cosmology_e0_preflight.json`.

The clean Python-test workflow did not materialize the evidence-bridge report before `pytest`.

## ARTEFACT

The Python-test workflow now materializes deterministic audit prerequisites before running the full suite:

1. `python tools/rll_real_data_evidence_bridge.py --output results/audit/rll_real_data_evidence_bridge.json --require-data-ready`
2. `python tools/rll_cosmology_e0_preflight.py --output results/audit/rll_cosmology_e0_preflight.json`
3. verifies both files are non-empty;
4. only then runs `pytest`.

No historical scientific result is rewritten.

## EXECUTION

New-head CI execution after this repair: TOKEN_VAZIO_EXECUTION until observed.

## EVIDENCE

The previous failure is classified as dependency/materialization ordering, not a demonstrated flat-closure mathematics failure.

## CLAIM

`claim_allowed=false`.
`IMPLEMENTED_UNTESTED != PASS`.

## F_ok

- E0 flat-closure focused tests passed on the previous head.
- Root cause of the global-suite failure is identified.
- CI dependency contract is now explicit in the Python-test job.

## F_gap

- rerun full Python suite on the new head;
- observe Claim Boundary Quality Gates on the same head;
- only then consider ready-for-review/merge.

## F_next

Require all mandatory checks on the exact repaired head to conclude success before promotion.

SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
