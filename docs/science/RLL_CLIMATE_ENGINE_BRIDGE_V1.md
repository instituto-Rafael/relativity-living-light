# RLL — Climate Engine External Compute Bridge V1

Status: `IMPLEMENTED_UNTESTED`  
Route: WORK → `rll/lab`  
Claim boundary: `claim_allowed=false`

## Purpose

Connect RLL to Climate Engine as an **external computation and visualization provider**, not as a primary sensor/source authority and not as a causal validator.

The bridge preserves:

`SOURCE != COMPUTE_PROVIDER != EVIDENCE != CLAIM`

`VISUALIZATION != EVIDENCE`

`CROSS_PROVIDER_AGREEMENT != STATISTICAL_INDEPENDENCE`

`RESIDUAL != CAUSE`

## External capability observed

Climate Engine documents API families for metadata, time series, raster/map IDs, zonal statistics and reports. This V1 intentionally binds only four bounded operations:

- dataset dates metadata;
- dataset variables metadata;
- native coordinate time series;
- raster map values / map-id generation.

Authoritative public references at implementation time:

- https://www.climateengine.org/apis/introduction-to-the-apis/
- https://www.climateengine.org/apis/timeseriesEndpoints/
- https://www.climateengine.org/apis/mapidEndpoints/
- https://api.climateengine.org/

## Zero Trust

The API key is read only from:

`CLIMATE_ENGINE_API_KEY`

The bridge does not:

- write the key to source control;
- include it in the request URL;
- print it;
- hash it into a receipt;
- persist raw tile handles.

Network execution is opt-in. Default behavior is `DRY_RUN`.

Only HTTPS requests to `api.climateengine.org` are allowed. Final redirects must remain on the same allowed host. Responses are byte-capped and SHA-256 hashed.

## RLL route

```text
PRIMARY SOURCE / DATASET AUTHORITY
        ↓
Climate Engine
(EXTERNAL_COMPUTE_AND_VISUALIZATION)
        ↓
SHA-256 response receipt
        ↓
sanitized derived product
        ↓
RLL comparison / falsifier
        ↓
TOKEN_VAZIO_DELTAOBS until a separate numeric gate passes
```

A map is a derived view. A time series returned by the provider is a derived product. Their agreement with an RLL path is useful for cross-checking, but does not by itself establish statistical independence or a shared physical cause.

## Examples

Dry-run metadata:

```bash
python3 scripts/rll_climate_engine_bridge.py \
  --operation metadata_variables \
  --dataset GRIDMET
```

Dry-run time series:

```bash
python3 scripts/rll_climate_engine_bridge.py \
  --operation timeseries_coordinates \
  --dataset GRIDMET \
  --variable pr \
  --coordinates '[[-121.61,38.78]]' \
  --start-date 2026-09-01 \
  --end-date 2026-09-02
```

Dry-run map:

```bash
python3 scripts/rll_climate_engine_bridge.py \
  --operation map_values \
  --dataset GRIDMET \
  --variable pr \
  --temporal-statistic mean \
  --start-date 2026-09-01 \
  --end-date 2026-09-02
```

To execute, the user must supply their own authorized key at runtime and append `--execute`.

## Relation to NOAA Trinity633 / ΔOBS

This V1 does **not** wire itself into Trinity633 because the current `rll/lab` and `main` histories are divergent and the existing maturity topology requires WORK → lab promotion.

After the topology is reconciled, the intended use is:

```text
NOAA direct custody path ─┐
                          ├─> normalized comparison ─> ΔOBS candidate gate
Climate Engine path ──────┘
```

The two paths may share upstream datasets or processing ancestry, so independence must be established rather than assumed.

## R3

F_ok: external compute bridge, secret boundary, host allowlist, response hash and sanitization contract materialized.

F_gap: API key is external user authority; no live request or Climate Engine response has been observed in this branch; provider-path independence from direct NOAA custody is unestablished.

F_next: run focused tests; open draft PR to `rll/lab`; after exact-head CI, perform one metadata probe and one bounded data/map probe with a user-owned API key.
