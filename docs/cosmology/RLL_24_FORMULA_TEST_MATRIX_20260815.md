# RLL — Matriz Governada de 24 Fórmulas para Testes — 2026-08-15

Status: `TEST_DIAGNOSTIC_INTAKE / claim_allowed=false / direct_model_integration=false`

Authority preserved:
- `data/contracts/cross_domain_equation_intake.v1.json`
- `data/inputs/cosmology_joint/desi_50_hypothesis_intake.v1.csv`
- `book/24_resultados_figuras_painel.md`

This artifact does **not** create a parallel theory contract and does **not** edit protected canonical model/likelihood code.

## Purpose

Select only the source-registry formulas that materially help the current RLL falsification pipeline as:
1. normalization/modulation gates;
2. stability diagnostics;
3. residual/signal diagnostics;
4. statistical inference checks.

The selection is deliberately 24, not because 24 is privileged, but because these are the formulas in the supplied 001–123 cut that currently have a defensible test role in RLL.

Invariant:

```text
source formula != repaired test formula
mathematical identity != RLL mechanism
graph reference != evidence
diagnostic PASS != cosmological claim
claim_allowed=false
```

## Selection topology

| Family | Count | Source IDs | RLL role |
|---|---:|---|---|
| Spiral / normalization | 7 | 005, 006, 007, 022, 023, 024, 025 | preflight for H01/H03 and other spiral-bearing hypotheses |
| Spectral / stability | 7 | 051, 053, 055, 057, 059, 060, 085 | type, finite norm, eigenmode and stability gates |
| Signal / residuals | 5 | 061, 063, 067, 069, 070 | residual structure, spectral leakage, autocorrelation, PSD/SNR |
| Statistical inference | 5 | 072, 073, 076, 079, 080 | summaries, uncertainty, covariance-aware fit and null-tail reporting |

## Repairs that are mandatory before test use

- **ID006**: `M_n=s^n F_n` is not a contraction asymptotically because `s*phi > 1`; retain it only as a growth/modulation diagnostic.
- **ID007**: replace the asserted condition by the explicit normalized operator `Mtilde_n = M_n / sqrt(sum |M_k|^2)`.
- **ID055**: use the actual 300-node first and second moments; do not inherit the old ID054 confusion between `<M>` and `<M^2>`.
- **ID059**: for `x_(n+1)=A x_n`, asymptotic stability uses `rho(A)<1`.
- **ID060**: `Re(lambda)<0` is a continuous-time criterion for `xdot=A x`.
- **ID079**: cosmological residual fits use a covariance-aware form `chi2=r^T C^-1 r` where appropriate; the Pearson count form is not a generic RLL likelihood.
- **ID080**: a p-value is a tail probability for a declared statistic/null distribution; `p<0.05` is not a universal promotion gate.

## Existing graph bindings

The registry binds formulas only to figures that already exist in `rll/lab`. These links are interpretive/diagnostic, not evidence promotion.

| Figure | Use in this matrix |
|---|---|
| `figs/paper/unified_H_ratio.png` | expansion residual/summary context; especially H03 shadow-model comparisons |
| `figs/paper/unified_f_and_weff.png` | contextual view for spiral-bearing background/transitional hypotheses |
| `figs/paper/unified_mu_residuals.png` | residual dispersion/SNR/chi-square context |
| `figs/paper/unified_growth_fs8.png` | growth residual/statistical context |
| `figs/paper/RLL_validacao_real.png` | aggregate fit/null-test context |
| `figs/paper/corner_plot_unified_highres.png` | posterior/uncertainty visualization |
| `figs/paper/post_2d_Os_zt.png` | 2D posterior/degeneracy visualization |

For formulas where no existing canonical figure is mathematically adequate, the registry records:

```text
TOKEN_VAZIO_NO_CANONICAL_GRAPH
```

No graph is invented just to fill the field.

## H03 first shadow test

H03 remains the nearest executable candidate in the governed DESI intake:

```text
H(z)^2 = H0^2 [Omega_m (1+z)^3 + Omega_Lambda (sqrt(3)/2)^z]
```

The 24-formula matrix does not promote H03. It supplies reusable gates around it:

- ID005: freeze `s=sqrt(3)/2` as the stated source parameter;
- IDs022–024: verify the geometric factor in its actual mathematical scope;
- ID072/073: descriptive summaries only;
- ID076: uncertainty reporting conditional on inference regime;
- ID079: covariance-aware residual statistic;
- ID080: null-tail reporting without confusing it with Bayes evidence;
- graph: `figs/paper/unified_H_ratio.png` for shadow-model comparison after implementation.

## Signal diagnostics: no forced DFT

IDs 061/063/069/070 are not automatically applied to DESI vectors. Cosmological sampling can be irregular and covariance-coupled. A frequency/autocorrelation diagnostic must declare sampling, windowing/interpolation (if any), estimator, covariance, and look-elsewhere control before a peak is interpreted.

Therefore the registry deliberately leaves several graph fields as `TOKEN_VAZIO_NO_CANONICAL_GRAPH`.

## Validation

```bash
python scripts/validate_rll_formula_test_matrix_24.py
python -m unittest tests.test_rll_formula_test_matrix_24
```

The validator enforces:
- exactly 24 unique source IDs;
- family distribution `7/7/5/5`;
- `claim_allowed=false` for every row;
- graph path existence when a graph is referenced;
- explicit `TOKEN_VAZIO` when no canonical graph is adequate;
- the critical source-registry repairs above.

## Promotion boundary

Nothing in this matrix modifies:
- canonical RLL background equations;
- RLL likelihood code;
- real-data manifests;
- published result receipts.

A formula can move from diagnostic intake toward model integration only through the existing RLL gates: dimensional/formal closure, physical mechanism, nested baseline, frozen data/covariance, mock recovery, deterministic execution, model comparison and independent reproduction.

**F_ok:** 24 test-relevant formulas selected and graph references bound conservatively.  
**F_gap:** no H03 implementation or new residual-spectrum/autocorrelation figures in this artifact.  
**F_next:** run H03 as a shadow model and generate synthetic-recovery + covariance-aware comparison receipts without touching canonical outputs.
