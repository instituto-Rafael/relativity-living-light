# 001_PONTEIRO — RLL POLYMORPHIC EVIDENCE DAG

**CURRENT_STATE:** structural proposal, claim_allowed=false, no automatic ingestion/network.
**Source:** `data/contracts/rll_epistemic_evidence_graph.v1.json`
**Gate:** `tools/ci/rll_polymorphic_evidence_gate_v1.py`; **tests:** `tests/test_rll_polymorphic_evidence_gate_v1.py`
**Orchestrator:** `.github/workflows/rll-calibration-orchestrator.yml` existing PR#1160; adds offline stage, does not create a new workflow.
**Docs:** `docs/workflows/RLL_POLYMORPHIC_EVIDENCE_ORCHESTRATION_V1.md`.
**Roles:** DESI/Pantheon/NOAA observations; Nature/SciELO articles; Zenodo archive; Science X discovery; Crossref metadata; Supabase private index.
**Bayes:** prior + likelihood + frozen covariance + independent sample groups + k. No numeric posterior/physical validation in CI.
**GAP:** real G4/G5 and independent CMB/biochemistry tests not yet executed; provider secrets NOT_VERIFIED; WS01 gate preserved.
**ROLLBACK:** additive commit revert; original 133 archive blobs preserved; main not mutated.
