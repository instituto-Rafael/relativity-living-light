# 001_PONTEIRO — RLL six-type epistemic taxonomy V2

**CURRENT_STATE:** proposed classification, nonordinal, read-only, claim_allowed=false.
**SOURCE:** `data/contracts/rll_epistemic_evidence_graph.v1.json` and
`data/contracts/rll_scientific_validation_orchestrator.v1.json` (7 governed evidence states).
**NEW CONTRACT:** `data/contracts/rll_epistemic_taxonomy.v2.json` (6 types + unclassified gap).
**VALIDATION:** `tools/ci/rll_epistemic_taxonomy_gate_v2.py` +
`tests/test_rll_epistemic_taxonomy_gate_v2.py`.
**EXECUTION:** existing `.github/workflows/rll-calibration-orchestrator.yml`, PR-safe only.
**DOCS:** `docs/workflows/RLL_EPISTEMIC_TAXONOMY_V2.md`.
**Boundary:** type ≠ evidence state ≠ demonstration ≠ observational measurement.
**GAP:** No new astrophysical fit, Bayesian posterior or independent replication.
**ROLLBACK:** close PR DRAFT; original V1 and main unchanged.
