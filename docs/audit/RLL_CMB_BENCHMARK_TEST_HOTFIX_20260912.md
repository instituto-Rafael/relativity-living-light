# RLL CMB Benchmark Test Hotfix — 2026-09-12

Authority: `instituto-Rafael/relativity-living-light`
Claim allowed: **false**

## OBSERVED FAILURE

Exact scientific benchmark workflow passed.

The only failing assertion in both full Python and Claim Boundary suites was:

```text
assert "does not validate RLL perturbations" in source
```

The source expresses the same boundary across two adjacent Python string literals:

```text
"This benchmark ... It does "
"not validate RLL perturbations, growth, ..."
```

Therefore the source text does not contain the concatenated phrase literally,
although Python runtime concatenation preserves the intended message.

Observed failures:
- Python tests: 1704 PASS, 1 FAIL, 12 subtests PASS;
- Claim Boundary: 1625 PASS, 1 FAIL, 12 subtests PASS.

## HOTFIX

Change only the brittle source-text assertion to the literal fragment that is
actually present:

```text
"not validate RLL perturbations"
```

No production/scientific code changes.
No tolerance changes.
No claim boundary weakened.
No benchmark output rewritten.

## CONSEQUENCE

This is a test-representation defect, not a scientific-model defect.

`TEST_LITERAL_LAYOUT_FAILURE != SCIENTIFIC_FAILURE`.

Re-execution remains required before PASS is promoted.

SOURCE != CONFIG != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
