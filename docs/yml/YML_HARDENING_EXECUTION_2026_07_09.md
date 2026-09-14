# YML Hardening Execution — 2026-07-09

## Scope

This execution record documents the non-scientific hardening commits applied after the deep YAML audit of `instituto-Rafael/relativity-living-light`.

The changes intentionally avoid modifying scientific model logic, observational datasets, claim status, likelihood math, priors, falsification thresholds or real-data values.

## Applied hardening

The following workflows were aligned with the baseline used by newer canonical workflows:

- `.github/workflows/RLL-CI.yml`
- `.github/workflows/RLL_SCIENTIFIC.yml`
- `.github/workflows/android-build.yml`
- `.github/workflows/bayes_analysis.yml`
- `.github/workflows/validate-schema-contracts.yml`
- `.github/workflows/formulas-artifacts-validation.yml`
- `.github/workflows/desi-dr2-bao-validation.yml`
- `.github/workflows/academic-parameter-governance.yml`

## Baseline controls

Where missing and operationally safe, the following controls were added:

```yaml
permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

For checkout steps that do not need repository write credentials:

```yaml
with:
  persist-credentials: false
```

For jobs without runtime bounds:

```yaml
timeout-minutes: <bounded value>
```

## Security summary update

`SECURITY_SUMMARY.md` was updated to reflect the current repository surface. The repository is no longer documented as a documentation-only surface; it includes scripts, tools, validation code, application paths and GitHub Actions workflows.

## Deliberately not changed

The following items were identified by the audit but intentionally left for a later, more schema-aware pass:

- `TOKEN_VAZIO` normalization inside raw-data manifests.
- Legacy/staging YAML redirection/removal.
- Expected-invalid fixture metadata.
- Data manifest schema migrations.

Those areas can affect consumers and tests, so they should be handled with explicit schema validation and a dedicated migration PR.

## Retrofeedback

- **F_ok:** workflow security baseline improved without changing scientific calculations.
- **F_gap:** manifest and staging cleanup still requires schema-aware migration.
- **F_next:** run YAML syntax validation and workflow audit on this branch before merge.
