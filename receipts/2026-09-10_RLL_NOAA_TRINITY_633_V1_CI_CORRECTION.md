# RLL NOAA Trinity633 V1 — CI correction receipt

Date: 2026-09-10/11 UTC
Parent receipt: `receipts/2026-09-10_RLL_NOAA_TRINITY_633_V1_PREFLIGHT.md`
PR: #851
Branch: `rll/noaa-trinity-633-v1-20260910`

## Observed CI evidence before correction

The first PR head reached GitHub Actions.

Observed PASS:
- Real Data Bootstrap Validation
- Convention Consistency Check
- formulas-artifacts
- repo-real-inventory
- Real Data Contract CI
- RLL Knowledge Matrix

Observed fail-closed:
- workflow inventory reconciliation reported `expected=78 actual=88`; its focused unit test itself reported `6 passed`.
- YAML Deep Audit reported one YAML syntax failure, isolated to
  `PapersPub/11_giza_continuous_archaeoastronomy/metadata/vixra_candidate_intake.yml`
  line 56; this file is outside the Trinity633 delta.
- the same YAML audit marked the Trinity step only MEDIUM because
  `continue-on-error` requires an explicit residual receipt.

## Corrective delta

The Trinity action no longer uses workflow-level `continue-on-error`.

External NOAA unavailability is now represented as a successful observation action
with typed `gate_status=SOURCE_CUSTODY_UNAVAILABLE`, a persisted receipt,
`observed_cross_domain=false`, and `claim_allowed=false`.

Contract/parser/internal execution errors remain process failures.

This preserves:

`TOKEN_VAZIO != 0`

`SOURCE_UNAVAILABLE != EXECUTOR_FAILURE`

`SOURCE_AVAILABILITY != EVENT_CORRELATION`

## State

`IMPLEMENTED_CI_RETRY_PENDING`

F_ok: first CI separated repo-wide historical drift from the Trinity-specific MEDIUM finding; Trinity error semantics were tightened.
F_gap: successor-head CI final status remains TOKEN_VAZIO until observed; workflow inventory 78/88 and unrelated Giza YAML syntax failure remain separate gaps.
F_next: evaluate successor-head focused Python/YAML/claim gates; do not merge while any applicable Trinity regression remains.
