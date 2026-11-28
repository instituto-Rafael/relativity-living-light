# μRECEIPT — RLL model bifurcation F/C/I/S/U/G V1

Date: 2026-11-26 (America/Sao_Paulo)  
State: TESTED_LOCAL / CI_PENDING  
Claim boundary: claim_allowed=false

## Source and authority

- Repository: instituto-Rafael/relativity-living-light
- Base branch: rll/lab
- Base commit: c73b560bed94f12a9c9714afc556615fa907a937
- Predecessor: data/governance/RLL_GROWTH_SEMANTICS_ABC_V1.json
- Producer retained: tools/rll_growth_semantics_abc.py

## Delta

- Added a non-selective F/C/I/S/U/G branch contract.
- Mapped F/C/I to existing C/A/B semantics without duplicating equations.
- Kept S/U/G as typed TOKEN_VAZIO.
- Added fair-comparison gates and negative tests.
- Added six frozen branch contracts with typed unknowns, predeclared rejection and E1/E2/E3 result relations.
- Froze the logistic derivative coordinate and the branch-I sign invariant q_s<=0 for A>0, w_t>0 and z>=0.
- Reused the repository Python test workflow instead of adding a new workflow inventory entry.

## Local execution

- python compile: PASS
- structural gate: PASS_SCOPED
- claim_allowed: false
- unittest: 9/9 PASS
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

- F_ok: typed branches, provenance, urgency, gaps, falsifiers and rollback are materialized; local gate and 9 negative/contract tests pass.
- F_gap: repository Python CI, independent reproduction, physical closure and common posterior remain open.
- F_next: traverse the governed promotion path rll/lab -> rll/integration -> rll/release -> main; do not bypass branch-maturity gates.
