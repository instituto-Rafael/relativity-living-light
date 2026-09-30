# RLL Formula ↔ Literature Edge/Vector Audit V1

**Date:** 2026-08-22  
**Route:** `WORK -> rll/lab -> rll/integration -> rll/release -> main`  
**State:** `IMPLEMENTED / CI_REVALIDATION`  
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

## Execution checkpoint — G4 -> G5 -> G6

Append-only event: GitHub Actions run `32568668295`, artifact `9474792910`, artifact digest `sha256:39eaa9ba025bac35c448bac81870d18e0b0ff40a207c00340609b24541f5b0a2`.

The run produced six uploaded files, including current G4, G5, G6 and Pantheon covariance receipts. Software-level infrastructure reached G6 without losing upstream evidence.

Observed G6 state is **not PASS**:

- `state = BLOCKED_G6_CONVERGENCE_OR_EVIDENCE`
- `claim_allowed = false`
- `scientific_confirmation = false`
- `F_gap = [MCMC_CONVERGENCE]`
- LambdaCDM `max_Rhat = 1.0102527461564457`
- RLL `max_Rhat = 1.2428791680240134`
- RLL `Rhat(Omega_s0) = 1.2428791680240134`
- RLL `Rhat(z_t) = 1.1433443407756332`
- nested evidence finite for all six nested runs and none hit maxiter
- `lnB10_mean(RLL-LCDM) = -0.8153567290360115`
- `lnB10_span = 0.6288161348702488`
- narrow-prior sensitivity `lnB10 = -1.6987967377687028`
- G4 BIC proxy and G6 nested mean have the same unfavorable sign for RLL

This event closes the earlier `TOKEN_VAZIO_POST_G6_OBSERVABLE_RECEIPT` only as **observed execution evidence**. It does **not** close G6 scientifically because the preregistered MCMC convergence criterion failed.

The Python integration test is therefore required to distinguish:

`software execution valid + scientific state BLOCKED`

from

`software/infrastructure failure`.

A BLOCKED receipt is accepted by software CI only when `pass_all=false`, `F_gap` exactly matches failed convergence/evidence components, claims remain blocked, and the receipt is strict JSON. It is never rewritten to PASS to make CI green.

**Promotion rule:** G7 synthetic recovery and G10 clean-environment replication are not authorized from this G6 event. G8 perturbation closure may continue only as the already-declared parallel physical-closure route.

## F_ok / F_gap / F_next

**F_ok**: literature now has machine-addressable references, independence groups, false-positive controls, immutable formula-reference edges, non-scalar evidence vectors, explicit falsifiers and append-only tests. G4/G5 receipts are reproducible in CI, pre-existing Pantheon covariance is reverified rather than trusted by existence, and G6 now emits an auditable blocked receipt instead of disappearing behind a generic Python failure.

**F_gap**: `MCMC_CONVERGENCE` in G6; full 486-formula materialization; deterministic cross-source deduplication; remaining per-formula edges; exact H01/H03 likelihoods; G8/G9 physical closure; and independent RLL implementation/replication remain open.

**F_next**: finish CI revalidation with execution-vs-science state separation. If software CI is green, merge only to `rll/lab` while preserving G6 as BLOCKED. Then design a preregistered G6 convergence follow-up rather than tuning chains post-hoc, and in parallel materialize the full formulas artifact and deterministic dedup IDs. Promotion beyond lab remains `rll/integration -> rll/release -> main` with receipts.
