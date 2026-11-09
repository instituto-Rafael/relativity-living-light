# 001_PONTEIRO — RLL | Barontini relational-time intake

- **INTENT:** reproduce an external quantum-simulator relational-time experiment without promoting a cosmological RLL claim.
- **CURRENT_STATE:** docs/presentation/05_CURRENT_STATE_RLL.md; additive scoped study.
- **SOURCE:** G. Barontini, Phys. Rev. Research 8 L022047 (2026), DOI 10.1103/1h9j-df4k; data DOI 10.5281/zenodo.19651064.
- **CONTRACT:** data/contracts/rll_barontini_relational_time.v1.json; seven names and pinned MD5; dataset license unresolved.
- **EXECUTOR:** scripts/rll_barontini_time_intake.py; offline audit default, explicit --fetch only.
- **TEST:** tests/test_rll_barontini_time_intake.py; 11/11 PASS_LOCAL_STD_LIB; GitHub exact-head CI TOKEN_VAZIO until readback.
- **PROTOCOL:** docs/science/RLL_BARONTINI_RELATIONAL_TIME_INTAKE_V1.md.
- **EVIDENCE:** offline negative-path tests; original data not fetched/hashed locally in session; experiment NOT_REPRODUCED; claim_allowed=false.
- **FALSIFIERS:** MD5 mismatch, nonfinite/malformed rows, duplicate t, tau ties, time-order errors, missing uncertainties/method reproduction.
- **BOUNDARY:** simulation != RLL cosmology; no DESI/Pantheon/CMB/ΛCDM code changes, no main changes.
- **NEXT:** retrieve upstream bytes with explicit network opt-in, verify SHA256 and reproduce paper under registered constraints.
