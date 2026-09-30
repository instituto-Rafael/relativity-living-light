# RLL NOAA Trinity633 — Zero Trust / Privacy Hardening CI Receipt V2

Date: 2026-09-11
Parent: PR #851 merged at `75d3bac4eb60e3969a6d51da70296540ab7b3c7b`
Successor: PR #853
Tested head: `21e28625e85ffb1ad233721a9f8b3b6ab3a55b50`
State: `VERIFIED_LIMITED_HARDENING`
claim_allowed: false
compliance_claim: false

## Evidence observed

Real Data Contract CI:
- run: `34553568329`
- conclusion: `success`
- focused step: `Validate NOAA Trinity633 governance and focused tests` = PASS
- Trinity633 focused tests: `18 passed`
- existing focused real-data tests: `22 passed`
- raw JSON import tests: `4 passed`

Other observed applicable gates:
- RLL Governance Quality Gate — non-certification: PASS
- Real Data Bootstrap Validation: PASS
- Convention Consistency Check: PASS
- repo-real-inventory: PASS
- formulas-artifacts: PASS
- RLL Knowledge Matrix: PASS
- workflow architecture: `architecture_errors=0`

## Hardening now evidenced

- deny-by-default source allowlist;
- exact NOAA SWPC hostname and exact path allowlist;
- HTTPS-only source routing;
- URL userinfo/query/fragment/custom port rejected;
- cross-host redirect rejected by the existing custody fetcher;
- HTTP 200 + JSON content type + non-empty payload + SHA-256 required for custody;
- structural payload validation:
  - RTSW wind / RTSW IMF / Kp / F10.7: non-empty JSON list of objects with `time_tag`;
  - GloTEC: GeoJSON `FeatureCollection` envelope;
- application-layer network timeout and 5 MB/source cap;
- workflow `contents: read`, checkout credentials not persisted;
- orchestrator runner pinned to `ubuntu-24.04`;
- public non-personal scientific telemetry classification;
- raw NOAA payloads are workflow artifacts, not repository commits;
- `claim_allowed=false` and `compliance_claim=false`.

## Preserved gaps

- `TOKEN_VAZIO_INFRA_EGRESS_POLICY`: no claim that GitHub runner egress is firewall-restricted;
- `TOKEN_VAZIO_DEPENDENCY_LOCK`: repository dependencies are range-based, not a reviewed exact lock;
- `TOKEN_VAZIO_DEPENDENCY_HASHES`: package hashes are not verified;
- `TOKEN_VAZIO_PAYLOAD_SEMANTIC_FIELD_VALIDATION`: structural envelope is checked; physical field semantics remain outside this gate;
- `TOKEN_VAZIO_STATISTICAL_INDEPENDENCE`;
- `TOKEN_VAZIO_NUMERIC_RESIDUAL_ENGINE`;
- `TOKEN_VAZIO_CAUSA`.

Repository-global blockers remain separate:
- workflow inventory contract `expected=78 actual=88`;
- one historical invalid YAML under `PapersPub/11_giza_continuous_archaeoastronomy/metadata/vixra_candidate_intake.yml`.

## Decision

The Zero Trust/privacy/data-governance hardening is supported as
`VERIFIED_LIMITED_HARDENING` for the tested head only.

It does not authorize a scientific claim, standards certification, merge,
physical ΔOBS, causal attribution or independent-domain claim.

F_ok: focused hardening gate and 18 Trinity tests passed remotely.
F_gap: infrastructure egress, dependency lock/hashes, semantic payload fields and scientific residual gates remain typed TOKEN_VAZIO.
F_next: preserve PR #853 as draft until review; then build a separate typed 6h→3h→3h window layer that consumes governed receipts without mutating the Zero Trust boundary.
