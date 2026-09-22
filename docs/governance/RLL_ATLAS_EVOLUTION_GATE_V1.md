# RLL ATLAS Evolution Gate V1

State: `IMPLEMENTED_FAIL_CLOSED / claim_allowed=false`  
Date: `2026-08-27`  
Producer authority: `instituto-Rafael/relativity-living-light`  
Atlas authority/index: `rafaelmeloreisnovo/Mapa`

## Purpose

This layer converts the ATLAS route into an executable anti-regression contract for RLL scientific promotion. It does **not** certify RLL physics and does not replace the existing `TOKEN_VAZIO` closure ledger.

`ATLAS:X` is applied as:

`authority -> source -> L/O/T relations -> scale -> evidence -> G0..G7 -> delta -> index`

## Current gate state

| Gate | State | Meaning |
|---|---|---|
| G0 source/rights freeze | `PARTIAL` | some source identity exists; full rights/hash custody is incomplete |
| G1 observable schema | `PARTIAL` | DESI BAO is partially structured; all consumed vectors are not yet frozen |
| G2 full covariance | `TOKEN_VAZIO` | unified SN/BAO/CMB/growth covariance policy is not closed |
| G3 likelihood parity | `TOKEN_VAZIO` | identical likelihood/nuisance treatment across models is not closed |
| G4 baseline recovery | `TOKEN_VAZIO` | unified LCDM/wCDM/CPL recovery is not closed |
| G5 robust inference | `TOKEN_VAZIO` | multi-seed posterior + real Bayesian evidence is not closed |
| G6 growth/perturbations | `TOKEN_VAZIO` | CLASS/CAMB-equivalent physical backend is not closed |
| G7 claim decision | `BLOCKED` | cannot open while G0-G6 and independent replication remain incomplete |

## Anti-regression invariants

1. Gate maturity may not silently decrease.
2. Evidence pointers already in custody may not be removed by a successor record.
3. Invariants and blocking-token identities may not be silently deleted.
4. Historical records remain append-only; successors point to predecessors.
5. `TOKEN_VAZIO != PASS`.
6. A negative result is evidence and is preserved; it is not treated as project regression.
7. `claim_allowed=true` requires G0-G6 at `VERIFIED` or stronger, G7 verified, and every required blocker in its declared closure state.
8. A governance PASS is not a physics PASS.

## Machine artifacts

- `data/governance/RLL_ATLAS_EVOLUTION_GATE_20260827_V1.json`
- `tools/rll_atlas_evolution_gate.py`
- `tests/test_rll_atlas_evolution_gate.py`
- `.github/workflows/rll-atlas-evolution-gate.yml`

The workflow emits hashed receipts under `artifacts/governance/`.

## ATLAS projection

- `L:X`: preserve historical smoke/negative results and predecessor records.
- `O:X`: authority, custody, covariance, likelihood parity, baseline recovery, inference, perturbations, and replication remain independently testable.
- `T:X`: Mapa indexes; RLL implements/produces evidence.
- `REL:X`: `authority_for`, `source_of`, `evidenced_by`, `tested_by`, `blocks`, `unblocks`, `supersedes`, `indexed_by`.
- `SCALE:X`: program -> gate -> claim -> dataset/version -> file/blob/hash -> receipt.
- `EVID:X`: no promotion without evidence and a falsifier.
- `GAP:X`: missing proof stays `TOKEN_VAZIO`/`BLOCKED`.
- `LEARN:X`: successor records only; no silent evidence erasure.

## Immediate next scientific probe

Freeze one rights-cleared full likelihood and covariance, then execute LCDM/wCDM/CPL/RLL on identical inputs with robust multi-seed diagnostics. Preserve the existing negative smoke baseline rather than overwriting it.

## R3

`F_ok`: canonical producer pin + executable G0-G7 contract + anti-regression tests.  
`F_gap`: G2-G6 + independent replication.  
`F_next`: close the smallest evidence-producing gate, then append a successor record.
