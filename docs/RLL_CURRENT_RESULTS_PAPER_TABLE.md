# RLL — Current Results Paper Table

**Evidence state:** `DOCUMENTED_FROM_CANONICAL_ARTIFACT`; not independently reproduced in this hotfix.  
**Primary authority:** `results/structure_d/joint_real_likelihood.json`.  
**Global claim gate:** `claim_allowed=false`.  
**Rule:** this table mirrors the artifact; it does not alter inputs, formulas, code, outputs or scientific claims.

---

## 1. Artifact identity

| Field | Value |
|---|---|
| schema | `rll.joint_real_likelihood.v2` |
| created_utc | `2026-07-03T10:25:07Z` |
| runtime_seconds | `332.9936774949997` |
| optimizer | `scipy.optimize.differential_evolution` |
| seed | `42` |
| tol | `1e-06` |
| maxiter | `140` for each model |
| N | `64` |
| dataset_type | `real_observational` |
| rd_policy | `derived_power_law_from_H0_Om_Ob_h2_for_all_models` |
| interpretation_label | `lcdm_preferred` |
| claim_allowed | `false` |

The literal `interpretation_label` conflicts with the numerical ranking below: CPL has the lowest chi2, AIC, AICc and BIC in this artifact. This is recorded as a documentation-level `CONTRADICTION`; it is not silently repaired or promoted into a scientific conclusion.

## 2. Dataset routes

| Block | Repository path | Recorded policy |
|---|---|---|
| H(z) | `data/real/Hz_data_real.csv` | real observational input |
| DESI DR2 BAO primary | `data/real/cosmology/desi_dr2_bao_primary_points.csv` | real observational input |
| DESI DR2 BAO covariance | `data/real/desi_dr2_bao_covariance.csv` | official full covariance; technical gate ready |
| fσ8 | `data/real/cosmology/fsigma8_growth_real.csv` | internal growth approximation |
| CMB shift | `data/real/CMB_shift_real.json` | full 3x3 `R`, `l_A`, `Omega_b h^2` covariance |
| parameter registry | `data/inputs/cosmology_joint/parameter_origin_registry.json` | required before information criteria |

`bao_covariance_policy.claim_allowed=true` is scoped only to use of the official full BAO covariance in `chi2_with_covariance`. It does not override the global RLL claim gate.

## 3. Model comparison

| Model | chi2 | AIC | AICc | BIC | N | k | dof |
|---|---:|---:|---:|---:|---:|---:|---:|
| LCDM | 93.95354560099567 | 103.95354560099567 | 104.98802835961635 | 114.74796101779403 | 64 | 5 | 59 |
| wCDM | 92.79427056355686 | 104.79427056355686 | 106.26795477408318 | 117.74756906371489 | 64 | 6 | 58 |
| CPL/w0waCDM | 63.119554616395284 | 77.11955461639528 | 79.11955461639528 | 92.23173619991299 | 64 | 7 | 57 |
| RLL | 93.95983068903539 | 109.95983068903539 | 112.57801250721721 | 127.23089535591276 | 64 | 8 | 56 |

## 4. chi2 decomposition

| Model | H(z) | DESI DR2 BAO | fσ8 | CMB shift |
|---|---:|---:|---:|---:|
| LCDM | 28.689146678458307 | 19.07091845950121 | 23.66253932342459 | 22.530941139611556 |
| wCDM | 28.258331520090362 | 15.463676477799806 | 22.64875516585215 | 26.423507399814547 |
| CPL/w0waCDM | 20.49695533658436 | 11.122948121040453 | 18.805525163391785 | 12.694125995378686 |
| RLL | 28.70658045782483 | 19.198725661654947 | 23.654558176474517 | 22.399966393081083 |

## 5. Fitted parameters

| Model | H0 | Om | OL | Ob_h2 | sigma8 | w | w0 | wa | Os0 | zt | wt |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LCDM | 60.00000063178996 | 0.3503201008429801 | 0.9136504178095255 | 0.022872788797639595 | 0.6150485187669168 | — | — | — | — | — | — |
| wCDM | 60.0 | 0.34919655279051753 | 0.8834497383304587 | 0.0229115351627258 | 0.6155086296600447 | -0.966834665064835 | — | — | — | — | — |
| CPL/w0waCDM | 60.151105071543775 | 0.35154565089251294 | 0.6601205008594014 | 0.022739101387779917 | 0.6227661015511812 | — | -0.30051397418196235 | -1.8230601347523976 | — | — | — |
| RLL | 60.00304290371374 | 0.3503449701210798 | 0.9131849509974717 | 0.022873041854710837 | 0.6156702423950631 | — | — | — | 0.0 | 6.006796735267388 | 0.7806099951360136 |

Values near configured parameter limits require a dedicated bounds and convergence audit before physical interpretation.

## 6. Deltas versus LCDM

| Model minus LCDM | delta_chi2 | delta_AIC | delta_AICc | delta_BIC | Descriptive reading |
|---|---:|---:|---:|---:|---|
| wCDM | -1.1592750374388032 | 0.8407249625611968 | 1.2799264144668285 | 2.9996080459208656 | slightly lower chi2; worse information criteria |
| CPL/w0waCDM | -30.833990984600383 | -26.83399098460039 | -25.868473743221074 | -22.51622481788104 | numerically preferred in this artifact |
| RLL | 0.006285088039717834 | 6.006285088039718 | 7.589984147600859 | 12.482934338118739 | no chi2 improvement; penalized by extra parameters |

RLL reaches `Os0=0.0`, the LCDM-like limit represented in this implementation. This is a result of this run, not proof that every RLL formulation is structurally excluded.

## 7. Allowed and blocked language

Allowed:

> The current canonical artifact records a shared N=64 comparison of LCDM, wCDM, CPL/w0waCDM and RLL. In this artifact, CPL has the lowest recorded chi2 and information criteria. RLL returns `Os0=0.0`, has delta_chi2 approximately +0.0063 versus LCDM and is disfavored by AIC, AICc and BIC. The global claim gate remains closed.

Blocked:

- RLL is confirmed or scientifically superior;
- RLL beats LCDM or CPL;
- this single artifact is an independent reproduction;
- covariance readiness alone validates the model;
- the source-intake packages validate RLL.

## 8. Evidence gaps

| Gap | State | Consequence |
|---|---|---|
| independent reproduction of this exact artifact | `TOKEN_VAZIO_REPRODUCTION` | result remains documented, not independently reproduced |
| multi-seed robustness | `TOKEN_VAZIO_ROBUST_FIT` | ranking stability not established |
| posterior/MCMC or nested sampling | `TOKEN_VAZIO_POSTERIOR` | parameter uncertainties and evidence not established |
| CLASS/CAMB growth backend | `TOKEN_VAZIO_BACKEND` | D+/fσ8 remains an internal approximation |
| interpretation-label reconciliation | `CONTRADICTION` | `lcdm_preferred` conflicts with recorded CPL metrics |
| boundary/convergence diagnostic | `TOKEN_VAZIO_DIAGNOSTIC` | near-limit parameters remain uninterpreted |

## 9. R3

```text
F_ok   = table synchronized to the canonical JSON, with exact metrics and scoped covariance readiness.
F_gap  = reproduction, robust seeds, posterior, external growth backend, convergence and label reconciliation remain open.
F_next = let CI validate documentation coherence; keep claim_allowed=false.
```
