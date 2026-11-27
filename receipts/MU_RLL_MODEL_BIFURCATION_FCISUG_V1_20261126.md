# μRECEIPT — RLL model bifurcation F/C/I/S/U/G V1

Date: 2026-11-26 (America/Sao_Paulo)  
State: TESTED_LOCAL / CI_PENDING  
Claim boundary: claim_allowed=false

## Source and authority

- Repository: instituto-Rafael/relativity-living-light
- Base commit: 99ecccfe2e10c12e4caab635fddbe0df1639ae35
- Predecessor: data/governance/RLL_GROWTH_SEMANTICS_ABC_V1.json
- Producer retained: tools/rll_growth_semantics_abc.py

## Delta

- Added a non-selective F/C/I/S/U/G branch contract.
- Mapped F/C/I to existing C/A/B semantics without duplicating equations.
- Kept S/U/G as typed TOKEN_VAZIO.
- Added fair-comparison gates and negative tests.
- Added isolated pull-request CI with read-only permissions.

## Local execution

- python compile: PASS
- structural gate: PASS_SCOPED
- claim_allowed: false
- unittest: 6/6 PASS
- pytest availability in construction workspace: TOKEN_VAZIO_DEPENDENCY_NOT_INSTALLED

The test suite uses Python stdlib unittest and remains discoverable by pytest.

## Non-promotion boundary

PASS_SCOPED means only that the bifurcation contract is structurally coherent.
It is not evidence that any branch is physically true, observationally preferred,
or superior to LambdaCDM, wCDM, CPL, interacting-sector, unified-dark-sector, or
modified-gravity alternatives.

## Rollback

The delta is isolated to five new files. Rollback removes only those files and
does not rewrite the predecessor contract, historical failures, or model code.

## R3

- F_ok: typed branches, provenance, urgency, gaps, falsifiers and rollback are materialized; local gate and 6 negative/contract tests pass.
- F_gap: remote CI, independent reproduction, physical closure and common posterior remain open.
- F_next: run focused tests, open PR, inspect checks, then update this receipt with a successor.
