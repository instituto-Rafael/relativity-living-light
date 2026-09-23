# RLL Closure Program V1

Status: EXECUTABLE_PLANNING_CONTRACT
Claim allowed: false

## Purpose

This document composes the remaining RLL work into one dependency-aware program. It does not choose unresolved scientific semantics. Every workstream names the discipline that must do the work, the prerequisite chain, the artifact that must be produced, the falsifier, and the TOKEN_VAZIO/successor state it is intended to close.

The machine-readable authority is:

- data/governance/RLL_CLOSURE_WORKSTREAM_REGISTRY_V1.json
- data/governance/RLL_GATE_NAMESPACE_REGISTRY_V1.json
- tools/rll_closure_queue.py

## Two independent G namespaces

The project currently has two valid but different G-series. From this version onward, cross-contract references must be qualified:

- REGIME:G0..G6 = physical/geometric applicability.
- SCI_GATE:G0..G11 = scientific evidence progression.

A region routed to REGIME:G5 is not thereby at SCI_GATE:G5.

## Work ownership by discipline

Software/DevOps/governance closes deterministic wiring, workflow inventory, permissions, receipts and execution graph defects.

Cosmology/scientific computing owns versioned background physics semantics, common data surfaces, sound-horizon policy and null-limit behavior.

Theoretical/mathematical physics owns the perturbation equations, gauge, super-horizon initial conditions, conservation/Bianchi consistency and stability.

Boltzmann-solver specialists independently implement the frozen closure in CLASS and CAMB. Neither implementation may use generated outputs from the other as its physical source.

Statistics/Bayesian inference owns covariance, nuisance policies, prior transforms, convergence, logZ uncertainty, robustness and ablations.

Data engineering owns immutable source identity, hashes, ordering, cross-block covariance and external-likelihood custody.

Low-level/ARM/Termux owns physical-device replay, toolchain identity and cross-runtime receipts.

Independent reproduction must be performed through a materially independent runner/implementation or sampler; a rerun of the same hidden state is not G10 closure.

Mathematics/geometry executes MF-0001..MF-0251 under formal/domain/unit gates but may not promote geometry directly into cosmology.

RMRCTI remains a residual/stability diagnostic until a separately derived causal mapping exists.

## Critical path

WS00 wiring/governance
  -> WS01 canonical background physics
       -> WS03 perturbation closure
            -> WS04 CLASS
            -> WS05 CAMB
                 -> WS06 cross-backend parity
                      -> WS07 growth
                      -> WS09 DES Y6/lensing
       -> WS12 H0/r_d full-Boltzmann integration
  -> WS02 canonical full-covariance likelihood
       -> WS10 DESI official joint/cross-block
            -> WS13 joint Bayesian evidence
                 -> WS14 robustness/ablation
                 -> WS15 independent replication
                      -> WS20 publication/claim router
  -> WS11 ACT DR6 LCDM posterior
       -> WS08 CMB binding (also depends on WS06)
  -> WS16 physical Termux Execution Fabric witness
  -> WS17 MF expression execution
  -> WS18 RMRCTI hidden-truth/real-trace work
  -> WS19 workflow/branch/platform governance

## Promotion rule

A workstream is never marked CLOSED merely because its target file exists. Closure requires the domain-specific receipt and falsifier outcome required by its contract. Presence is not evidence; execution is not claim.

## Immediate tranche

1. Wire tools/validate_rx_dha.py before the aggregate Rx development gate.
2. Restrict the write-enabled validation job explicitly to workflow_dispatch.
3. Reconcile .github/workflow-contract.yml to executable workflow reality.
4. Materialize the closure queue and namespace registry.
5. Re-run CI.
6. Then execute the exact Rx plan on physical Termux/ARM.

## Scientific tranche after engineering closure

Do not silently instantiate RX-PHYSICS-CANONICAL-V2. Human/scientific authority must version the chosen background semantics. Then the perturbation closure can be derived and independently implemented in CLASS and CAMB.

## R3

F_ok: closure responsibilities, dependencies, outputs and falsifiers are machine-readable.

F_gap: scientific choices, physical ARM execution, external-likelihood custody and independent replication remain evidence-dependent.

F_next: close WS00/WS19 in CI, run WS16 physically, then resolve WS01 explicitly before WS03.
