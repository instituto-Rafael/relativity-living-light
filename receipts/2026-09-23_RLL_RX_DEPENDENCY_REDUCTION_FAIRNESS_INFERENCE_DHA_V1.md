# RLL Rx dependency reduction receipt — fairness / inference / DHA V1

Date: 2026-09-23
State: PARTIAL_IMPLEMENTATION_WITH_GOVERNANCE_GAPS
claim_allowed: false

## Sources

- canonical implementation authority: instituto-Rafael/relativity-living-light
- parent main before PR #968: 68b2c62669b89cf4897aaf03d5aa4b61cbddf4c3
- PR #968 exact tested head: fc061e2240fe330d7eee07dedadaad02521764f4
- PR #968 merge commit: 2bdea159c5d517036f65f15280b25b3bc2d7bdb7
- PR #969 DHA successor initial head: ed652aafdf01069c2d4cbf3a7e5f9dac29b7a7ac

SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.

## Delta A — merged in PR #968

Added project-owned stdlib implementation surfaces:

- rx/fairness.py
- rx/inference.py
- tools/validate_rx_fairness.py
- tools/validate_rx_inference.py
- tests/test_rx_fairness_inference_stdlib.py
- integration into Rx CLI, zero-dependency gate, no-AI gate,
  development aggregate gate and Validacao Real workflow
- docs/architecture/RLL_ZERO_DEPENDENCY_MODULE_MATRIX_V1.md

Boundaries:

- no observational dataset changed;
- no physics contract changed;
- no legacy NumPy/SciPy/emcee/dynesty route deleted;
- emcee semantic parity remained TOKEN_VAZIO;
- dynesty nested evidence remained TOKEN_VAZIO;
- CLASS/CAMB remained an external benchmark authority;
- claim_allowed=false.

## Exact-head execution evidence for PR #968

Python canonical suite at head fc061e2240fe330d7eee07dedadaad02521764f4:

- total observed by quality monitor: 1955
- pytest summary: 1908 passed, 45 subtests passed, 2 failed
- the two failures were both workflow-documentation inventory checks:
  contract expected 102 active workflows while repository discovery found 107
- no new fairness, inference or zero-dependency test appeared in the failure list

Other observed exact-head checks included successful convention consistency,
formula/artifact inventory, repo-real-inventory, knowledge matrix and real-data
contract jobs.

This means the new module tests executed without an observed failure in the
canonical suite. It does NOT convert the whole repository run into PASS because
the two repository-wide documentation-contract failures remain real.

## Governance contradiction observed

Branch Maturity Gate V2 blocked the direct work -> main route with:

- INVALID_BRANCH_TRANSITION
- RELEASE_REQUIRES_EVIDENCE_OR_EXPLICIT_GAP

The declared topology is:

work -> rll/lab -> rll/integration -> rll/release -> main

Despite that blocked gate, PR #968 was merged into main at
2026-09-23T05:24:39Z. This receipt records the event without treating the merge
itself as evidence of gate success.

A direct retarget to rll/lab was evaluated and rejected as unsafe: current
rll/lab and the main-based work line are materially diverged. The compare
observed the work line 602 commits ahead and 151 commits behind rll/lab at that
point. Topology reconciliation is therefore a separate governed task, not an
automatic base-branch substitution.

## Delta B — DHA / Astropy successor in draft PR #969

The repository-wide dependency audit identified one actual Python consumer of
Astropy: src/rll/desi_dha_extractor.py.

The legacy route passes omega_grid directly to Astropy
LombScargle.power(), while the same route later interprets omega as the angular
frequency in cos(omega*x + phi). Astropy documents power() inputs as ordinary
frequency, not angular frequency. Therefore an explicit 2*pi semantic boundary
must be resolved before replacement.

Added:

- rx/dha.py
  - zero-third-party weighted floating-mean sinusoid baseline
  - explicit angular frequency in radians per x-unit
  - explicit omega <-> cycles conversion
  - no invented false-alarm probability
- tools/validate_rx_dha.py
  - synthetic angular-frequency recovery
  - detects the legacy Astropy call pattern
  - leaves Astropy semantic parity TOKEN_VAZIO
  - leaves false-alarm probability TOKEN_VAZIO
- runtime/test/development-gate wiring and module-matrix update

The legacy Astropy/SciPy/NumPy DHA route remains preserved. No historical DHA
result is promoted by this delta.

## Open dependency families

- emcee ensemble-sampler semantic parity: TOKEN_VAZIO
- dynesty/nested Bayesian evidence: TOKEN_VAZIO
- Astropy Lomb-Scargle normalization/FAP parity: TOKEN_VAZIO
- SciPy legacy optimization families: migrate one result contract at a time
- base package/pyproject dependency boundary: open
- Pantheon+ official full covariance/provenance: external evidence gap
- CLASS/CAMB growth/Boltzmann comparison: external benchmark required
- RX-PHYSICS-CANONICAL-V2 science convergence: not selected

## Rollback

All development in these slices is additive. Legacy scientific routes remain
available. The DHA successor is isolated in draft PR #969. A rollback can
remove the authored Rx surface without rewriting historical datasets/results.

## R3

F_ok:
- active Rx runtime was already zero-third-party;
- fairness and deterministic inference stdlib modules were added and merged;
- exact-head canonical suite showed no failure in those new module tests;
- DHA Astropy dependency was reduced to a typed semantic boundary and a
  zero-third-party angular-frequency successor baseline.

F_gap:
- repository workflow inventory contract 102 vs discovered 107;
- promotion topology is inconsistent with current main/rll-lab divergence;
- DHA Astropy normalization/FAP parity remains TOKEN_VAZIO;
- emcee/dynesty parity/evidence routes remain TOKEN_VAZIO;
- scientific V2 convergence and external observational/CLASS-CAMB gates remain.

F_next:
- run exact-head CI on draft PR #969;
- do not promote DHA until its gate is green and the topology route is
  reconciled;
- then continue one dependency family at a time under parity/rollback gates.
