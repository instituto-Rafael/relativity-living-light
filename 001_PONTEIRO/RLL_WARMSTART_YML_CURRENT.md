# 001_PONTEIRO — RLL G4/G5 warmstart / 133 legacy YML

- State: DRAFT/HOLD; original checks active; `claim_allowed=false`.
- Historical Git-blob archive: `NOVOexport/legacy-workflows/20261107/` (133 copies).
- Archive router YML: `.github/workflows/rll-legacy-archive-index.yml`.
- New manual/PR workflow: `.github/workflows/rll-calibration-orchestrator.yml`.
- Scoped preflight/test: `tools/ci/rll_warmstart_preflight_v1.py` + `tests/test_rll_warmstart_preflight_v1.py`.
- Detailed scientific route: `NOVOexport/legacy-workflows/20261107/WARMSTART_ROUTING.md`.
- G4 frozen: ΛCDM, wCDM, CPL, GEDE, IDE, RLL; G5 freezes verified data/covariance.
- Seven wCDM-CMB parameters remain `TOKEN_VAZIO_FULL_CMB` in background-only G4.
- Nondestructive migration; preserve 3 manual aliases; do not move other required jobs until shadow equivalence.
- Rollback: close draft PR; main unchanged.
