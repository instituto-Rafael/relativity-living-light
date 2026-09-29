# RLL — Public Custody Chain Gate V1

**State:** `claim_allowed=false` by construction.  
**Purpose:** validate provenance and evidence boundaries for public-record research spanning supply chains, company ownership/capital, financial markets, policy/travel timelines, trade rules, and high-level aerospace engineering.

This gate does **not** infer motive, concealment, corruption, market manipulation, or political causality from temporal coincidence. It produces an auditable graph of what public records do and do not establish.

## 1. Canonical boundary

```text
SOURCE ≠ EVENT ≠ ENTITY ≠ MONEY/MASS ≠ INFERENCE ≠ CLAIM
```

Every edge must carry source references and an explicit state:

- `OBSERVED`
- `DERIVED`
- `HYPOTHESIS`
- `TOKEN_VAZIO`
- `BLOCKED`

A chronological edge such as `precedes`, `same_day_public_context`, or `next_observed_stop` is non-causal unless a separate causal evidence gate is satisfied.

## 2. Public-only source classes

Accepted source kinds:

1. official government publication;
2. regulatory filing;
3. court or legislative record;
4. official corporate publication;
5. official exchange or market data;
6. official trade/customs data.

Private records, leaked records, private banking details, non-public tax returns, non-public AWBs/bills of lading, and non-public cap tables are outside scope.

### Tax/financial disclosure distinction

The gate treats these as different objects:

```text
tax_return != public_financial_disclosure != electoral_asset_declaration
```

A tax record is accepted only when an explicit lawful public-release basis is recorded. Public financial disclosures and electoral declarations may be used as their own evidence classes without being relabeled as tax returns.

## 3. Company ownership and capital

For Brazil, the public CNPJ data model can provide fields such as capital social and QSA/administrator composition when present in the published dataset.

For U.S. public issuers, SEC filings may provide capital structure, material transactions, officers/directors, beneficial ownership disclosures, and acquisition consideration.

For private companies, absence of a complete public cap table is preserved as:

```text
TOKEN_VAZIO_PRIVATE_CAP_TABLE
```

Public Form D or investment-vehicle filings do not by themselves prove the complete ownership structure of the operating company.

## 4. Policy, travel and investment timeline

The seed contract includes public official records for:

- Executive Order 14257 (2 Apr 2025);
- Riyadh (13 May 2025);
- Doha (14 May 2025);
- UAE visit (15 May 2025);
- the White House-reported Saudi investment commitment announced 13 May 2025.

The investment record is typed as `investment_announcement`, not realized cash. Promotion to cash flow requires a second source evidencing realization.

Political-event records are descriptive only. The gate must never use a trip, tariff, meeting, or market movement by itself to assert motive or causality.

## 5. Aerospace boundary

The seed contract records only high-level public vehicle facts needed to test a mass/mission claim:

- Falcon 9: official vehicle-level propulsion family;
- Starship: official vehicle-level propulsion family;
- NASA HLS: current program-status source.

The gate intentionally excludes hazardous-material procurement identities, routes, quantities, acquisition instructions, or operational handling details.

An engineering statement such as “mission X is impossible” cannot be promoted from intuition or payload percentage alone. A later engineering gate must bind, at minimum, the mission phase, vehicle configuration, mass budget, staging/reuse boundary, and independently sourced performance variables.

## 6. Toroidal stability transform

The custody gate exposes a neutral authored transform for the user's seven-axis state:

```text
X7 = [
  mass_material,
  production_delivery,
  inventory_wip,
  logistics_lead_time,
  commodity_energy,
  fx,
  capital
]
```

Each coordinate must first be normalized to `[0,1]` by a predeclared rule.

Each normalized coordinate is interpreted as a phase on `S¹`; the seven coordinates form a product torus. The wrapped phase difference is:

```text
Δθ_i = wrap_pi(2π(x_i - y_i))
```

and the dimension-normalized toroidal distance is:

```text
d_T(x,y) = sqrt(mean(Δθ_i²)) / π
```

with stability score:

```text
S_T(x,y) = clamp(1 - d_T(x,y), 0, 1)
```

The 14-dimensional state is:

```text
X14_t = [X7_t, X7_t - X7_(t-1)]
```

This is an analytical representation of state plus change. It is **not** promoted as a physical law.

The author's remembered `delta_p` and `k` constants are intentionally left `TOKEN_VAZIO` until bound to an authoritative formula/source. The gate does not guess them.

## 7. Fail-closed conditions

The gate fails if any of these occur:

- a source is not public;
- source kind is outside the allowlist;
- an event has no source;
- a claimed realized investment has only an announcement source;
- a tax record lacks a lawful public-release basis;
- private/sensitive fields are inserted;
- hazardous procurement routes are inserted;
- causal language appears without passing the causal-evidence rule;
- toroidal vectors are malformed or not normalized.

Even on `PASS_GATE_CUSTODY_ONLY`:

```text
claim_allowed = false
```

because this gate verifies custody/provenance structure, not scientific, financial, political, or causal truth.

## 8. Multidimensional public-money and logistics layer

The custody model now distinguishes accounting stages instead of treating every public number as cash.

Brazil:

```text
empenho != liquidacao != pagamento
```

United States:

```text
appropriation != obligation != outlay
```

The gate rejects `cash_realized=true` before the jurisdiction-specific cash stage. Missing intermediate stages are not interpolated; they are emitted as `TOKEN_VAZIO_PUBLIC_MONEY_STAGE`.

For a traceable ledger period, the neutral reconciliation observable is:

```text
residual = opening_balance + inflows - outflows - closing_balance
```

A non-zero residual outside a predeclared tolerance is an anomaly for investigation, not evidence of wrongdoing.

### Directive-body history

Each public director/officer/administrator role is an effective-dated object:

```text
entity + person + role + effective_from + effective_to + as_of + source_refs
```

A role described as current must have an explicit `as_of` date. An end date before the start date fails closed. This prevents a filing from one year being silently projected into another.

### Shipment, receiving and schedule timing

For public shipment records:

```text
sent_at <= arrived_at <= received_at
```

The gate derives:

```text
arrival_lapse     = arrived_at  - sent_at
receiving_lapse   = received_at - arrived_at
lead_time         = received_at - sent_at
deadline_slip     = actual_end  - deadline_at
```

Positive `deadline_slip` means late; negative values mean completion before deadline. If the completion event is not publicly observed, it remains `TOKEN_VAZIO_COMPLETION`.

### Bullwhip proxy

For two matched public series over identical periods and units:

```text
BW = Var(upstream) / Var(downstream)
```

The gate requires at least four matched observations. A zero downstream variance leaves the ratio unresolved rather than manufacturing an infinite score. `BW > 1` is a variance-amplification observation; it is not by itself proof of the economic cause.

### Quantified uncertainty

The receipt exposes at least:

```text
source_hash_coverage
event_source_coverage
unhashed_sources
warning_count
error_count
```

Therefore the uncertainty budget can shrink monotonically as source snapshots and missing stages are materialized.

## 9. Pre-registered falsifiers

The seed contract now contains four hypothesis families:

1. public-money trace closure;
2. logistics timing stability;
3. upstream/downstream bullwhip;
4. effective-dated governance reconstruction.

Each hypothesis must declare both `metric_or_observable` and at least one falsifier. A hypothesis without either fails the Gate structurally.

The central interpretation rule remains:

```text
anomaly != causality
residual != wrongdoing
temporal coincidence != motive
missing record != zero
```

## 10. Artifacts

- `data/contracts/public_custody_chain_gate.v1.json`
- `data/pipelines/audit/public_custody_chain_gate.py`
- `tests/test_public_custody_chain_gate.py`

Future generated evidence should be append-only and should include input/output hashes when source snapshots are materialized.

## 11. R3

```text
F_ok   = public-only custody schema + non-causal event graph + toro X7/X14 transform + fail-closed tests.
F_gap  = source snapshots/hashes, normalized real time series, complete company histories, market/trade joins, independent causal tests.
F_next = materialize source snapshots; bind monthly/quarterly datasets; emit hashed artifacts; run the Gate before any interpretation layer.
```
