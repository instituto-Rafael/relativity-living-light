# RLL — NOAA → Trinity633 Observation Cycle V1

Status: `IMPLEMENTED_UNTESTED`  
Claim boundary: `claim_allowed=false`  
Authority: NOAA public products are external SOURCE; RLL remains authority for its own analysis code and claim gates.

## 1. Purpose

Materialize the symbolic chain

`TOKEN_VAZIO → VERBO → CHEIO → NOVO_VAZIO → RETROALIMENTAR → NOVOS_VAZIOS`

as a reproducible observation/provenance cycle without converting source availability, cross-domain data presence, correlation, residual, cause or RLL evidence into synonyms.

The time topology is:

`★‡ Trinity633 = 6 h → 3 h → 3 h = 12 h`

and repeats.

## 2. Three phases

### LUX_6H

`TOKEN_VAZIO → VERBO → CHEIO`

Actions:
1. resolve only declared NOAA endpoints;
2. fetch through the existing climate custody fetcher;
3. enforce HTTPS + declared hostname;
4. hash payloads;
5. emit one receipt per source and a Trinity receipt.

No physical event is inferred.

### SPIRITUM_3H

`CHEIO → NOVO_VAZIO`

Actions:
1. refresh the same declared sources;
2. count which measurement families have auditable custody;
3. expose missing families as gaps;
4. preserve `TOKEN_VAZIO_NUMERIC_RESIDUAL_ENGINE` until a numerical ΔOBS implementation exists.

Three available families are only a readiness gate. They are not proof that three independent physical instruments observed one event.

### VERBUM_3H

`NOVO_VAZIO → RETROALIMENTAR → NOVOS_VAZIOS`

Actions:
1. refresh custody;
2. emit the gap ledger;
3. emit F_ok/F_gap/F_next;
4. seal the run receipt.

The only authorized "verbum" is the minimum bounded statement supported by the receipt.

## 3. NOAA source families

The first cycle binds five declared families:

- solar-wind plasma: RTSW wind;
- heliospheric magnetic field: RTSW magnetometer/IMF;
- geomagnetic index: planetary Kp;
- solar radio flux: F10.7;
- ionospheric TEC: GloTEC.

Different measurement families are **not automatically statistically independent**. This implementation intentionally records `statistical_independence_established=false`.

## 4. Workflow reuse

No competing workflow is created.

The existing `.github/workflows/rll-real-data-orchestrator.yml` is the execution surface. Its schedule is split into three UTC expressions representing the 6h→3h→3h transitions:

- LUX: `17 0,12 * * *`
- SPIRITUM: `17 6,18 * * *`
- VERBUM: `17 9,21 * * *`

Sequence example: 00:17 → 06:17 → 09:17 → 12:17 → 18:17 → 21:17 UTC.

A manual run may select a phase explicitly.

## 5. Epistemic invariants

`SOURCE ≠ ARTEFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM`

`SOURCE_AVAILABILITY ≠ EVENT_CORRELATION`

`MEASUREMENT_FAMILY_DISTINCT ≠ STATISTICAL_INDEPENDENCE`

`CROSS_DOMAIN_READINESS ≠ OBSERVED_CROSS_DOMAIN`

`RESIDUAL ≠ CAUSE`

`TOKEN_VAZIO ≠ 0`

Current forced outputs:

- `observed_cross_domain=false`
- `statistical_independence_established=false`
- `numeric_residual=TOKEN_VAZIO_NUMERIC_RESIDUAL_ENGINE`
- `cause=TOKEN_VAZIO_CAUSA`
- `claim_allowed=false`

## 6. Next scientific gate

The next allowed promotion is not "new physics". It is a typed numerical layer that:

1. parses source timestamps and declared variables;
2. builds a six-hour baseline;
3. evaluates a three-hour challenge window;
4. evaluates a three-hour feedback window;
5. propagates timing/data uncertainty;
6. preregisters thresholds;
7. compares against known/common-mode explanations;
8. emits ΔOBS/RESIDUAL only when the numerical gate passes.

Until then, Trinity633 is an auditable observation-routing and provenance machine.


## 7. Zero Trust, data governance and privacy

The execution boundary is deny-by-default. Before any Trinity network action, the
repository runs `scripts/validate_rll_noaa_trinity_governance.py` against the
machine contract, source registry, governance contract and existing orchestrator.

The bounded policy is:

- exact five-source allowlist; no arbitrary URL input;
- NOAA SWPC authority + exact declared hostname;
- HTTPS only, platform CA validation and same-host redirects only;
- no URL userinfo, custom ports, query parameters or fragments;
- non-parameterized `PUBLIC_GET` sources only;
- fixed 30 s timeout and 5 MB/source cap;
- HTTP 200 + JSON content-type + non-empty payload + SHA-256 required for custody;
- repository credentials are not used; checkout keeps `persist-credentials: false`;
- workflow permission remains `contents: read`;
- raw payloads are artifacts for custody/reproducibility and are not committed by this workflow;
- data class is `PUBLIC_NON_PERSONAL_SCIENTIFIC_TELEMETRY`;
- device/user identifiers, precise person location, audio/biometrics, profiling and secrets are forbidden by the Trinity policy.

These are engineering controls, not an assertion of legal or standards certification:
`compliance_claim=false`.

A source outage remains an observed external state. A policy/contract violation
fails closed. Therefore:

`SOURCE_UNAVAILABLE != POLICY_VIOLATION != EXECUTOR_FAILURE`.
