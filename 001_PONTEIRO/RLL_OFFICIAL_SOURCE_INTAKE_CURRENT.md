# RLL — PONTEIRO oficial de dados (V1 · HOLD)

START: `docs/science/RLL_OFFICIAL_SOURCE_INTAKE_V1.md`.

ROUTE: `data/contracts/rll_official_source_intake.v1.json` → `tools/rll_official_data_intake_v1.py` → `tests/test_rll_official_data_intake_v1.py` → `.github/workflows/rll-data-pipeline.yml` (manual, optional) → SHA-256 raw/receipt → independent data/physics gate.

Agent: `.github/agents/rll-official-data-intake.agent.md`, successor to existing `.github/agents/rll-secretary.agent.md` authority controls. Secrets are not copied or used in public GET. No new Actions workflow.

STATE: `IMPLEMENTED_HOST_TESTED_ONLY`, `LIVE_FETCH_NOT_RUN`, `AGENT_PAT_RUNTIME_TOKEN_VAZIO`, `DESI_NUMERICAL_NOT_INGESTED`, `CLAIM_ALLOWED=false`.

ROLLBACK: close the draft PR or revert the additive files and scoped YAML delta only. No legacy deletion.
