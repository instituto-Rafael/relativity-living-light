# RLL Dual-API Real Climate Calibration V1

**Status:** `ACTIVE_GOVERNED_DRAFT`  
**claim_allowed:** `false`

## Purpose

Materialize the two runtime authority selectors already declared by RLL:

- `RLL_AGENT_GITHUB_PAT_ENV`
- `RLL_AGENT_CLIMATE_KEY_ENV`

They are selectors for secret-bearing environment variables; they are not secret values.

The implementation preserves:

`SECRET != AUTHORITY != EXECUTION != EVIDENCE != CLAIM`

and:

`GITHUB_PROVENANCE != CLIMATE_SCIENTIFIC_SIGNAL`

## Two APIs, two roles

### GitHub API

Used only to observe repository/commit provenance for the exact calibration run.

It contributes control-plane custody:

- repository identity;
- resolved commit SHA;
- response hashes.

It is **not** used as a climatological input.

### Climate Engine API

Used for the external climate compute/data product:

1. `GET /metadata/dataset_dates`
2. `GET /metadata/dataset_variables`
3. `POST /timeseries/native/coordinates` for a baseline window
4. `POST /timeseries/native/coordinates` for a target window

The provider remains `EXTERNAL_COMPUTE_PRODUCT`. Upstream dataset authority is preserved.

## Agent runtime

The script resolves secrets from the selectors:

```text
RLL_AGENT_GITHUB_PAT_ENV -> name of GitHub secret env
RLL_AGENT_CLIMATE_KEY_ENV -> name of Climate Engine secret env
```

Existing aliases remain accepted, but ambiguous multiple aliases fail closed.

## GitHub Actions runtime

The manual workflow deliberately does **not** mirror the GitHub PAT into Actions.

```text
RLL_AGENT_GITHUB_PAT_ENV=GITHUB_TOKEN
GITHUB_TOKEN=${{ github.token }}

RLL_AGENT_CLIMATE_KEY_ENV=RLL_CLIMATE_ENGINE_TRIAL_TOKEN
RLL_CLIMATE_ENGINE_TRIAL_TOKEN=${{ secrets.RLL_CLIMATE_ENGINE_TRIAL_TOKEN }}
```

This preserves the existing RLL credential policy.

## Real calibration

For one declared dataset, variable, geometry and two date windows, the runtime computes:

- sample count;
- mean;
- population standard deviation;
- minimum;
- maximum;
- target minus baseline mean;
- z-shift relative to baseline dispersion;
- target/baseline ratio when defined.

Climate Engine's documented `-9999` missing sentinel is excluded.

No causal meaning is assigned to the residual.

## Privacy and receipts

Exact coordinates are not copied into the calibration receipt. The receipt stores:

- SHA-256 of canonical coordinates;
- top-level geometry count.

The workflow input itself remains part of the GitHub Actions control-plane event, so use only non-sensitive/public coordinates unless a separately reviewed privacy route is established.

Secret values, secret lengths, secret hashes and authorization headers are never written.

## Execution

Manual only:

`Actions -> RLL Dual API Real Climate Calibration — manual`

The workflow preserves an artifact even on failure, then fails closed with the runtime return code.

## Gates

A real calibration reaches `REAL_API_CALIBRATION_OBSERVED` only when:

1. both credentials resolve;
2. GitHub repository/commit probes succeed;
3. Climate metadata calls succeed;
4. baseline and target timeseries return HTTP 200;
5. both periods contain numeric samples.

Otherwise the receipt keeps a typed gap.

## Next scientific gate

A Climate Engine variable must be mapped to one declared RLL 8x8 variable with:

- units;
- conversion;
- cadence;
- primary-source authority;
- independent comparison path when available.

Only then can it become a candidate for `ΔOBS`; this V1 never promotes a physical or causal claim.
