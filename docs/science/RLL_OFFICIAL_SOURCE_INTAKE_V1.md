# RLL — entrada oficial de dados climáticos/cosmológicos (V1, HOLD)

**Role:** bridge existing `.github/workflows/rll-data-pipeline.yml` and `rll-secretary` agent to official public data under bounded manual controls. No new workflow. No change to scientific models. No automatic credential use. `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`.

## Provider boundaries

| Profile | Official source | Actual fetch | Value semantics | Still missing |
|---|---|---|---|---|
| `nasa_power_daily` | https://power.larc.nasa.gov/docs/services/api/temporal/daily/ | fixed daily point HTTPS GET at 0° lat, 0° lon for 2025-01-01 to 2025-01-07, `T2M,PS`, `time-standard=UTC` | gridded analysis-ready climate product, **not** direct field-station observations | provider version, resolution, station cross-check and uncertainty model |
| `desi_dr2_publications` | https://data.desi.lbl.gov/doc/papers/dr2/ | official index HTML only, bounded 768 kB | authoritative publications *metadata*, **not numerical cosmology data** | select specific raw release, license, exact hash, redshift/binning, BAO vector/covariance, independent likelihood |

The DESI cosmology pipeline under `data/real` remains authoritative for numerical physics. This V1 **does not** download actual DESI DR2 BAO covariance or update a fit. The distinction is deliberate, not an implied success.

## Agent and PAT boundaries

Already present: `.github/agents/rll-secretary.agent.md`, `copilot-setup-steps.yml`, `tools.agent.rll_agent_seven_guards`, repository PAT assurance, and Climate Engine bridge. New profile `.github/agents/rll-official-data-intake.agent.md` is a specialized **instruction profile**. It does not automatically authenticate, run Actions, create permissions or act as a workflow runner. Agent `PATGITHUB` and Actions `GITPAT` are separate. `CLIMATE` and `CLIMA` are external Climate Engine bindings; neither is used for public NASA POWER/DESI GET. No secret value was read or changed.

## Actions execution

Existing `.github/workflows/rll-data-pipeline.yml` gains two optional inputs without changing current defaults: `official_source` choice defaults `none`; `official_fetch` boolean defaults `false`.

- `official_source=none`: legacy dataset pipeline unchanged.
- `official_source=nasa_power_daily`, `official_fetch=false`: offline metadata receipt; no network.
- `official_source=nasa_power_daily`, `official_fetch=true`: at most one bounded official HTTPS GET; schema/fill checks; raw bytes + receipt + checksum stored in **Actions artifact only**.
- `official_source=desi_dr2_publications`: documentation discovery only, never numerical BAO validation.

All runs use `contents: read`, with `persist-credentials: false`, timeout, no secret and explicit opt-in for network. Artifacts are ephemeral, not automatically promoted or committed. The optional existing `commit_artifacts` path is disabled for official intake even when set to true, preventing accidental promotion.

Local validation:

```sh
python -m unittest -v tests.test_rll_official_data_intake_v1
python tools/rll_official_data_intake_v1.py --source nasa_power_daily --mode metadata_only --output-dir artifacts/rll-pipeline/official-data
```

## Fail-closed controls / acceptance

- HTTP redirects denied; only allowlisted HTTPS endpoints; no arbitrary URL, path or token input.
- Maximum one network request per manual execution; 512kB NASA JSON or 768kB DESI index HTML.
- Reject non-JSON, incomplete dates, invalid/missing parameters, all-missing values, non-finite numbers, invalid DESI index markers, oversize or empty payload.
- Typed `TOKEN_VAZIO` for absent data; retain raw exact bytes and SHA-256 in output artifact.
- Tests are mocks/synthetic controlled payloads, **not live network verification**. CI exact-HEAD and live provider status must be checked separately.
- No RLL likelihood, H(z), covariance, Q16, ARM or physical model fit executed.
- GitHub branch topology: work branch → `rll/lab` → `rll/integration` → `rll/release` → `main` after governance gates. This implementation is a draft branch/PR only.

## R3

`F_ok`: Official allowlist and guarded manual runtime proposed and locally testable.
`F_gap`: Live provider response, agent PAT runtime verification and DESI numeric/covariance ingestion remain unproven.
`F_next`: Exact-HEAD Actions gate in PR, then manually run dry-run metadata; after approval test a single NASA POWER fetch; pin a specific DESI numeric file separately.
