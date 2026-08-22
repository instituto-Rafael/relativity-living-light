# RLL Formula ↔ Literature Edge/Vector Audit V1

**Date:** 2026-08-22  
**Route:** `WORK -> rll/lab -> rll/integration -> rll/release -> main`  
**State:** `IMPLEMENTED / CI_PENDING`  
**append_only:** `true`  
**claim_allowed:** `false`  
**publication_effect:** `NONE`

## Purpose

This checkpoint converts literature comparison into a fail-closed evidence graph. It is not a paper-counting score and it does not promote any RLL claim.

The graph separates:

`formula -> exact prediction -> falsifier -> reference -> independence group -> false-positive controls -> edge -> evidence vector -> TOKEN_VAZIO/F_next`

A new bibliography edge is an increase in **provenance/coverage**, not necessarily an increase in support. A contradictory or null edge is positive operational progress when it reduces uncertainty.

## Inventory boundary

The repository manifest records 486 extracted formulas from 53 sources. The DESI hypothesis intake contains 50 additional hypothesis records. Therefore `486 + 50 = 536` is only a raw union upper bound before cross-source/version deduplication.

`deduplicated_total = TOKEN_VAZIO_DEDUP_COUNT`

The ChipQuantum `E_1..E_300` placeholders are not added to this count because they are explicitly not materialized formulas.

## Evidence classes

- `PAIR_A`: at least two sufficiently independent evidence groups, exact-formula relevance, and explicit false-positive/systematics controls.
- `PAIR_B`: multiple author groups but materially shared data/pipeline/systematics.
- `CLASS_MATCH`: literature tests the physical/model class, not the exact RLL equation.
- `CONTRADICTED_EXTERNAL_2PLUS`: at least two independent observational paths quantitatively contradict the written exact prediction under its declared interpretation.
- `TOKEN_VAZIO_EXACT_TEST`: exact formula has not been tested in a frozen equal-treatment likelihood/measurement gate.
- `MALFORMED`: a mathematical/type/dimensional/normalization contradiction precedes observation.

`CLASS_MATCH != SUPPORTS_EXACT` is a hard invariant.

## Seed decisions

| Formula | Current V1 state | Independent routes | Boundary |
|---|---|---:|---|
| H15 `sigma8(z)=sigma8_0[1-q^(-z)]` | `CONTRADICTED_EXTERNAL_2PLUS` | ACT DR6 CMB lensing; DES Y6 3x2pt | applies to conventional sigma8 interpretation; successor requires new ID |
| H21 `N_eff ~= 4.86` | `CONTRADICTED_EXTERNAL_2PLUS` | ACT DR6 primary CMB; Planck+BAO; BBN light elements | applies to conventional cosmological N_eff |
| H25 `Gdot/G=-H0(1-q)` | `CONTRADICTED_EXTERNAL_2PLUS` | lunar laser ranging; pulsar timing | applies to secular conventional Gdot/G |
| H35 power-like expression times `exp(pi i)` | `MALFORMED` | internal mathematical/type gate | complex amplitude is a possible successor object, not a repair in place |
| H01 evolving `w(z)` | `TOKEN_VAZIO_EXACT_TEST` | DESI DR2 is `CLASS_MATCH` only | theta_999/Spiral and exact frozen likelihood missing |
| H03 modified `H(z)` | `TOKEN_VAZIO_EXACT_TEST` | DESI DR2 is `CLASS_MATCH` only | exact H03 vs matched baselines must run in canonical chain |

## Bibliographic groups and controls

### Structure growth / H15

ACT DR6 CMB lensing (`arXiv:2304.05202`) reports a high-significance lensing spectrum and non-zero structure amplitude. Its analysis includes extensive null/consistency tests, systematic-error estimates and blinding. A companion foreground paper (`arXiv:2304.05196`) uses two independent sky simulations, bias hardening, source/cluster mitigation and frequency nulls.

DES Y6 (`arXiv:2601.14559`) is a physically distinct low-redshift 3x2pt route combining cosmic shear, galaxy clustering and galaxy-galaxy lensing. Its control family includes dedicated redshift-calibration (`arXiv:2509.07964`) and observational-systematics masking/decontamination (`arXiv:2509.07943`).

These are not treated as two copies of one pipeline.

### Relativistic species / H21

ACT DR6 extended-model inference (`arXiv:2503.14454`) gives `N_eff = 2.86 +- 0.13` and no evidence for new free-streaming light species. Planck 2018 + BAO (`arXiv:1807.06209`) gives `N_eff = 2.99 +- 0.17`. A distinct BBN light-element route (`arXiv:2401.15054`) finds `Delta N_eff = -0.10 +- 0.21` after robust nuclear-rate marginalization.

The graph records instrument/method independence explicitly; it does not merely count papers.

### Time variation of G / H25

Lunar Laser Ranging (`arXiv:gr-qc/0411113`) reports `Gdot/G=(4 +- 9)e-13 yr^-1` on Solar-System scales. Pulsar timing of J1713+0747 (`arXiv:1802.09206`) gives `Gdot/G=(-0.1 +- 0.9)e-12 yr^-1` in a strong-field system using combined NANOGrav/EPTA timing. The modalities and physical environments are distinct.

### Dynamical dark energy / H01 and H03

DESI DR2 BAO (`arXiv:2503.14738`) reports that a time-evolving `w0-wa` class can fit combined datasets better than LambdaCDM in some combinations, with significance depending on the supernova sample and with an explicit systematics caveat. This is retained as `CLASS_MATCH` only. It cannot validate H01 or H03 by resemblance.

## Evidence vector

Each seeded formula carries a non-scalar vector:

`V = [math_defined, units_closed, exact_prediction, independent_groups, false_positive_controls, external_concordance, contradiction_strength, reproducibility, claim_boundary]`

No weighted sum is defined. In particular, adding references cannot mechanically move a formula toward validation.

## Non-regression gates

The validator `tools/validate_formula_literature_edges.py` fails closed when:

1. `claim_allowed` changes from `false`, `publication_effect` changes from `NONE`, or `append_only` is disabled;
2. `PAIR_A` lacks two exact-evidence independence groups or false-positive controls;
3. `CONTRADICTED_EXTERNAL_2PLUS` lacks two independent contradiction paths;
4. `TOKEN_VAZIO_EXACT_TEST` is silently promoted using only class-level literature;
5. any TOKEN_VAZIO lacks `cause`, `evidence_needed`, `falsifier`, or `F_next`;
6. a historical reference/edge disappears or mutates in a successor snapshot;
7. an open gap disappears without an explicit closure receipt.

Tests in `tests/test_formula_literature_edges.py` include adversarial fixtures for those cases.

## What this V1 does not claim

- It does not audit all 486 formulas individually because the full formulas artifact is not materialized in the repository/release.
- It does not call 536 entries unique.
- It does not turn external observable agreement into independent RLL replication.
- It does not make DESI's dynamical-dark-energy result proof of an RLL expression.
- It does not erase H15/H21/H25 if successor formulas are introduced.
- It does not change any prior negative scientific result.

## F_ok / F_gap / F_next

**F_ok**: literature now has machine-addressable references, independence groups, false-positive controls, immutable formula-reference edges, non-scalar evidence vectors, explicit falsifiers and append-only tests.

**F_gap**: full 486-formula materialization, deterministic cross-source deduplication, remaining per-formula edges, exact H01/H03 likelihoods, and independent RLL implementation/replication remain open.

**F_next**: run CI on this work branch; if green, merge only to `rll/lab`. Then materialize the full formulas artifact, compute deterministic dedup IDs, and expand edges by the highest-value falsifiable family. Promotion beyond lab must continue through `rll/integration -> rll/release -> main` with receipts.
