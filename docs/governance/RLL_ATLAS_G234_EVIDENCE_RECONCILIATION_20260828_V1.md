# RLL ATLAS G2/G3/G4 evidence reconciliation — 2026-08-28 V1

State: `EVIDENCE_RECONCILED_PARTIAL / claim_allowed=false / publication_ready=false`.

This record is an append-only successor to the Ω6 projection. It does **not** rewrite the historical V2 record. It reconciles later observable execution evidence already merged into `rll/lab` and narrows G2/G3/G4 from `TOKEN_VAZIO` to `PARTIAL` only where the evidence permits.

## Why the projection changes

The successful Python-test run `33150360583` on head `a99e5caff4be0dea2a368592c80e36445e45ef89`, subsequently merged into `rll/lab`, produced an artifact digest-bound to `sha256:8bd1ca4aea1e53da2a8cd6da38965c12d66fb11457bb52dd474ed841327d2a97` containing:

- verified Pantheon+ full STAT+SYS covariance materialization;
- a six-model G4 background tournament;
- a G5 canonical frozen background-likelihood manifest;
- a G6 canonical inference receipt.

The inputs are hash-bound. G4 and G5 use the same DESI DR2, Pantheon+ and pure cosmic-chronometer background route. The G4 null-limit tests recover LCDM from GEDE `Delta=0`, IDE `beta=0`, and RLL `Omega_s0=0` at tolerance `1e-12`.

## Effective projection

- `G2_FULL_COVARIANCE: PARTIAL` — Pantheon+ full STAT+SYS and DESI DR2 covariance are materially used and hash-bound. Explicit cross-survey covariance and additional probe covariance remain open.
- `G3_LIKELIHOOD_PARITY: PARTIAL` — the declared six-model background tournament has one frozen data/covariance/selection/nuisance route and G5 freezes it by hashes. This does not establish parity for all probes or stable inference.
- `G4_BASELINE_RECOVERY: PARTIAL` — CLASS/CAMB standard LCDM/CPL recovery exists and the background null limits recover LCDM. RLL perturbative completion and full-probe baseline recovery remain open.

The effective maturity accounting is `7/21 = 0.333333`, up from `4/21`. This is **coverage of the evidence contract**, not probability that RLL is physically true.

## Negative evidence is part of the promotion

The promotion to PARTIAL is conditional on preserving adverse results:

- G4: RLL collapses to `Omega_s0=0`; `Δχ²≈5.23e-12` versus LCDM and `ΔBIC≈+22.31`. In this background scope RLL gains no fit improvement while paying the complexity penalty.
- G6: state is `BLOCKED_G6_CONVERGENCE_OR_EVIDENCE`; RLL has `max R-hat≈1.274 > 1.10`, and nested-seed stability also fails. The open gaps are `MCMC_CONVERGENCE` and `NESTED_SEED_STABILITY`.

CI success therefore means the software correctly produced an auditable blocked scientific result. It does not turn that result into a scientific PASS.

## Remaining blockers

Cross-survey covariance, official DESI joint/cross-block reproduction, DES Y6 executable likelihood custody, ACT DR6 LCDM posterior reproduction, RLL perturbation closure, independent CLASS/CAMB implementation, convergence repair, nested-seed stability, and materially independent replication all remain open.

## F_next

1. Resolve cross-survey covariance semantics without silently assuming zero correlation.
2. Reproduce official external likelihood baselines with immutable receipts.
3. Repair G6 convergence/seed stability without relaxing preregistered thresholds post hoc.
4. Close the perturbation theory before independent CLASS/CAMB implementation.
5. Require independent replication before any G7 claim decision.
