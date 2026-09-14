# SECURITY SUMMARY — Current Repository Surface (2026-07-09)

> **Status:** current operational security summary for `instituto-Rafael/relativity-living-light` after YAML and workflow hardening review.
>
> This file supersedes the older scoped restructuring note that described a documentation-only change set. The repository now includes documentation, data, scripts, tools, validation code, application components and GitHub Actions workflows.

## 1. Current execution surface

The repository is not documentation-only. Its current tracked surface includes, at minimum:

- Markdown, LaTeX, PDF and notebook documentation.
- CSV, JSON, YAML and manifest data assets.
- Python scripts under `scripts/`, `tools/`, `validation/` and related paths.
- Application/runtime paths such as `app/`, `src/` and low-level runtime components.
- GitHub Actions workflows under `.github/workflows/`.
- Artifact-producing validation and real-data governance pipelines.

## 2. Current security posture

The latest YAML/workflow audit did not identify literal secrets committed inside the reviewed YAML files. Some workflows reference GitHub Actions secrets by name, especially Android signing secrets, but no secret values are present in the YAML.

The main risk class is operational hardening drift, not exposed credentials. Legacy or auxiliary workflows must keep the same baseline used by the canonical real-data workflows:

- `permissions: contents: read` unless write access is explicitly required.
- `concurrency` with `cancel-in-progress: true` for deterministic CI behavior.
- `timeout-minutes` on jobs.
- `actions/checkout` with `persist-credentials: false` unless a later step explicitly needs push credentials.
- Clear claim boundaries for scientific workflows and real-data manifests.

## 3. Security controls expected for CI/CD

Every workflow should be reviewed against this baseline:

```yaml
permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Every checkout that does not need to push should use:

```yaml
with:
  persist-credentials: false
```

Every job should define a bounded runtime:

```yaml
timeout-minutes: 30
```

Use lower timeouts for schema/smoke checks and higher timeouts only for intentionally heavy scientific runs.

## 4. Data and claim-boundary posture

The repository contains real observational data manifests and pipelines, but scientific claims remain bounded by the state of the data, provenance, covariance policy, reproducible likelihood outputs and falsification gates.

`TOKEN_VAZIO`, pending ingestion slots and placeholder records are acceptable only when they are explicitly marked as incomplete and excluded from claim promotion. Prefer structured nulls plus `missing_fields` for machine-readable manifests where possible.

## 5. Secrets posture

Current policy:

- Never commit credentials, private tokens, keystores or API keys.
- Use GitHub Actions secrets for signing or private credentials.
- Avoid echoing secret-derived values in logs.
- Keep signing workflows isolated and reviewable.
- Prefer protected environments for release signing when repository settings support them.

## 6. Recommended recurring checks

- Run YAML syntax validation across all `*.yml` and `*.yaml`.
- Run workflow hardening audits for permissions, concurrency, timeout and checkout credential persistence.
- Run static analysis for Python and application code where applicable.
- Review notebook outputs before commit.
- Review artifact uploads for unintended sensitive content.
- Keep manifests explicit about real, pending, fixture, mock or historical status.

## 7. Historical note

Earlier versions of this file preserved a scoped 2025 restructuring review that described a documentation-heavy change set. That scope is no longer sufficient as a whole-repository security statement. The current summary should be treated as the active baseline; historical restructuring notes remain available through Git history.

## 8. Conclusion

The current repository is suitable for continued public scientific and engineering development when CI/CD hardening, claim-boundary discipline and secret hygiene are maintained. The active risk posture is **low-to-moderate operational risk** rather than documentation-only risk.

**R₃:**
- **F_ok:** no literal YAML secrets observed in the reviewed scope; canonical workflows show strong controls.
- **F_gap:** legacy/auxiliary workflows and manifests require continuous alignment.
- **F_next:** keep workflow hardening, real-data provenance and claim-boundary validation as mandatory gates.
