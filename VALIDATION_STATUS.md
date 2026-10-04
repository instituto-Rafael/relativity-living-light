# VALIDATION STATUS — Relativity Living Light (RLL)

**State:** current evidence router; documentation-only reconciliation.  
**Primary scientific artifact:** `results/structure_d/joint_real_likelihood.json`.  
**Global claim gate:** `claim_allowed=false`.  
**Independent reproduction in this hotfix:** `TOKEN_VAZIO_REPRODUCTION`.

## 1. Current documented scientific state

The canonical artifact records a real-observational N=64 comparison generated with `scipy.optimize.differential_evolution`, seed `42`, tolerance `1e-06` and `maxiter=140` for LCDM, wCDM, CPL/w0waCDM and RLL.

| Model | chi2 | AIC | AICc | BIC |
|---|---:|---:|---:|---:|
| LCDM | 93.95354560099567 | 103.95354560099567 | 104.98802835961635 | 114.74796101779403 |
| wCDM | 92.79427056355686 | 104.79427056355686 | 106.26795477408318 | 117.74756906371489 |
| CPL/w0waCDM | 63.119554616395284 | 77.11955461639528 | 79.11955461639528 | 92.23173619991299 |
| RLL | 93.95983068903539 | 109.95983068903539 | 112.57801250721721 | 127.23089535591276 |

RLL minus LCDM is `+0.006285088039717834` in chi2, `+6.006285088039718` in AIC, `+7.589984147600859` in AICc and `+12.482934338118739` in BIC. RLL returns `Os0=0.0`. The literal artifact label `lcdm_preferred` conflicts with the lower CPL criteria and is therefore tracked as `CONTRADICTION`, not silently normalized.

Exact mirrored values and the language boundary live in `docs/RLL_CURRENT_RESULTS_PAPER_TABLE.md`.

## 2. Technical readiness that does not equal model validation

- DESI DR2 BAO uses the recorded official full covariance; its local technical gate is ready.
- CMB shift uses the recorded 3x3 covariance over `R`, `l_A` and `Omega_b h^2`.
- The parameter-origin registry is present and required before information criteria.
- CLASS/CAMB is absent in the recorded runtime; D+/fσ8 remains an internal approximation.
- Covariance readiness does not override the global `claim_allowed=false` state.

## 3. Repository execution and CI are separate evidence

No test suite was executed locally by this documentation hotfix. CI on the new PR is the gate for this branch.

For provenance only, provider CI observed on merged PR #1045 at exact head `e16ea9a7376ae89dd892d3d2bdffd6d18def4ab4` reported `2051 passed`, `64 subtests passed` and `6 failed`. The six failures reduce to four main-branch causes:

1. missing top-level description in `schemas/rll_operator_lab_receipt_v1.schema.json`;
2. missing internal crosswalk identity `DRIVE-CRIPTTRES` in the main contract;
3. main `LICENSE.md` blob differing from the provenance registry expectation, observed by two tests;
4. workflow contract count `125` versus `127` discovered workflows, observed by two tests.

The direct `work -> main` transition also failed the branch-maturity route. Those main-only failures are not reclassified as lab failures and are not repaired here because the governed path is `work -> rll/lab -> rll/integration -> rll/release -> main`.

## 4. Existing routes preserved

- Synthetic and real-data entry points remain routed by repository code and pipeline documentation; this file does not newly assert their current runtime success.
- The pre-movement/local-dynamics boundary remains canonical in `docs/RLL_PRE_MOVEMENT_SCALE_BRIDGE.md`.
- Formula authority remains in `docs/FORMULAS_CANONICAS_INDEX.md` and `rll_equation_registry.yml`.
- Claim language remains bounded by `docs/RLL_CLAIM_BOUNDARIES.md`.

## 5. Gates still open

| Gate | State |
|---|---|
| exact independent reproduction | `TOKEN_VAZIO_REPRODUCTION` |
| robust multi-seed fit | `TOKEN_VAZIO_ROBUST_FIT` |
| posterior/MCMC or nested sampling | `TOKEN_VAZIO_POSTERIOR` |
| external CLASS/CAMB growth benchmark | `TOKEN_VAZIO_BACKEND` |
| parameter-boundary and convergence audit | `TOKEN_VAZIO_DIAGNOSTIC` |
| `interpretation_label` versus metric ranking | `CONTRADICTION` |
| source-intake scientific mapping | `TOKEN_VAZIO_SOURCE_TO_RLL` |
| scientific superiority claim | `BLOCKED` |

## 6. R3

```text
F_ok   = current artifact, metrics, custody and branch-policy evidence are separated and routed.
F_gap  = scientific reproduction and several main-only platform inconsistencies remain open.
F_next = accept only PR/CI evidence on rll/lab; do not promote claim or bypass branch maturity.
```
