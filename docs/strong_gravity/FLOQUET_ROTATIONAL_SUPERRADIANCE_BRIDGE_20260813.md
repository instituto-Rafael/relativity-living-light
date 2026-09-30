# Floquet Rotational Super-Radiance Bridge — Governed Integration

**Date:** 2026-08-13  
**Status:** DRAFT / EVIDENCE-GATED  
**Claim gate:** `claim_allowed=false`  
**Scope:** strong-gravity analogues, periodic/Floquet systems, angular-mode energy transfer.

## 1. Purpose

Materialize an append-only, falsifiable bridge for the 2026 experimental result on **Floquet rotational super-radiance**, without changing the semantics of existing Kerr/Blandford–Znajek (BZ), magnetorotational, black-hole-flux, or cosmology modules.

Primary source:
- Nature: https://www.nature.com/articles/s41586-026-10725-y
- Secondary article supplied for intake: https://www.inovacaotecnologica.com.br/noticias/noticia.php?artigo=extracao-energia-buraco-negro&id=010170260812

## 2. Hard scientific boundaries

The following are intentionally **not equivalent**:

1. Floquet rotational super-radiance in a modulated laboratory analogue.
2. Wave super-radiance in Kerr spacetime.
3. Blandford–Znajek electromagnetic extraction from a rotating black hole.
4. Existing `RLL_BH_flux` diagnostics/benchmarks.
5. Any cosmological RLL claim.

Therefore:

`LAB_ANALOG != KERR_SPACETIME != BZ_MECHANISM != RLL_BH_FLUX != COSMOLOGICAL_EVIDENCE`

and the global governance invariant remains:

`VISION != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`

No local analogue result is promoted to an astrophysical or cosmological claim by semantic similarity.

## 3. Minimal variable contract

Let

`x = (omega_F, m, omega, delta, gamma, phi, p_in, p_out)`

where:

- `omega_F_rad_s`: synthetic/Floquet angular modulation rate [rad/s]
- `m`: azimuthal mode integer
- `omega_rad_s`: incident angular frequency [rad/s]
- `modulation_depth`: dimensionless modulation depth
- `gamma_s_inv`: effective dissipation/loss rate [s^-1]
- `phase_rad`: modulation phase [rad]
- `p_in_w`: incident power [W]
- `p_out_w`: outgoing power [W]

Derived diagnostic:

`gain_energy = (p_out_w - p_in_w) / p_in_w`, for `p_in_w > 0`.

This gain is a diagnostic only. Positive gain is not, by itself, proof of Kerr super-radiance or astrophysical energy extraction.

## 4. Relations

- `REL-FLOQUET↔PHASE`: periodic phase modulation and mode selection.
- `REL-FLOQUET↔TOROIDAL`: ring/angular topology as a mathematical/engineering adjacency.
- `REL-FLOQUET↔BZ`: comparison of rotational energy-extraction concepts; **not mechanism equivalence**.
- `REL-FLOQUET↔RLL_BH_FLUX`: benchmark adjacency; **not cosmological evidence**.
- `REL-FLOQUET↔ORTHOGONAL`: factor decomposition for gain sensitivity and interactions.

## 5. Orthogonal/factorial route

For a balanced two-level design with factors `x_i ∈ {-1,+1}`, estimate projection coefficients

`beta_S = (1/N) * Σ y_k Π_{i∈S} x_{ki}`

for main effects and pairwise interactions. This is a deterministic diagnostic for controlled synthetic/test data. It does not replace the primary experiment's statistical model.

Suggested factors:
`omega_F`, `m`, `omega`, `delta`, `gamma`, `phi`.

Response:
`gain_energy`.

## 6. Urgency and execution tiers

### P0 — integrity before interpretation
1. Freeze source provenance and retrieval date.
2. Materialize machine-readable contract.
3. Preserve `claim_allowed=false`.
4. Add deterministic unit tests and negative controls.
5. Keep BZ/Kerr/RLL semantics untouched.
6. Maintain a gap/uncertainty ledger and receipt.

### P1 — empirical reproduction
1. Acquire the primary paper supplement/raw data when available and permitted.
2. Reproduce the reported gain/mode-selectivity curves.
3. Build a calibration and uncertainty budget.
4. Reproduce loss/dissipation dependence.
5. Run orthogonal/sensitivity decomposition only on traceable data.

### P2 — transfer tests
1. Compare the analogue equations against established Kerr-super-radiance conditions.
2. Map only quantities with dimensionally and physically justified correspondences.
3. Identify astrophysical observables separately.
4. Do not connect to cosmological evidence until an independent bridge and data gate exist.

## 7. Falsification and stop conditions

The bridge must remain non-promotional if any of these hold:

- the raw/supplementary data cannot be reproduced;
- gain disappears under calibrated controls;
- mode selectivity is not robust to loss/model uncertainty;
- the proposed Kerr correspondence is dimensionally or dynamically invalid;
- an astrophysical mapping requires an unverified free parameter;
- a cosmological conclusion depends only on analogy.

A negative result is preserved as evidence; it is never deleted to improve narrative coherence.

## 8. Operational-excellence path

`INTAKE → CLASSIFY → PROVENANCE → CONTRACT → IMPLEMENT → TEST → RECEIPT → REVIEW → EVIDENCE_GATE → CLAIM_GATE`

Every transition must preserve:
- append-only history;
- explicit uncertainty;
- source identity;
- separation of measured/simulated/estimated/extrapolated;
- reproducible inputs;
- failure evidence;
- `TOKEN_VAZIO` for unresolved states.

## 9. Current state

This branch materializes the scientific bridge, contract, and gap ledger. A candidate deterministic diagnostic implementation passed **6/6** tests in an isolated reference environment, but the GitHub connector blocked the code/test write before it reached the repository. Therefore repository execution/CI remains `TOKEN_VAZIO_TOOL_BLOCKED`.

It does **not** reproduce the Nature experiment and does **not** authorize a scientific claim.

Materialized:
- `data/contracts/floquet_rotational_superradiance.v1.json`
- `docs/strong_gravity/FLOQUET_GAPS_UNCERTAINTIES_LEDGER_20260813.md`

Pending/blocked:
- `data/pipelines/strong_gravity/floquet_superradiance_bridge.py`
- `tests/strong_gravity/test_floquet_superradiance_bridge.py`
- repository CI observation
