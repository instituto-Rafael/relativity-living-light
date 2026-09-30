# fσ8 growth sample

Path: `data/real/cosmology/fsigma8_growth_real.csv`

Columns:

```text
z,fs8,sigma,survey,method,reference,source_url,notes
```

This is a heterogeneous historical real-data compilation used only as an **exploratory growth surface** until covariance/overlap and physical growth-model gates pass.

## Provenance correction

The rows that use the common Oxford source URL are anchored to the compilation published in:

- A. Mehrabi, S. Basilakos, F. Pace (2015), *How clustering dark energy affects matter perturbations*
- MNRAS 452, 2930–2939
- DOI: `10.1093/mnras/stv1478`
- Table 2 contains the fσ8 points and the original per-measurement references.

A historical result artifact recorded `10.1093/mnras/stw1614`; that DOI is unrelated to this growth compilation and is superseded append-only in `data/governance/RLL_EXTERNAL_EVIDENCE_REGISTRY_V1.json`. Historical result JSON is not rewritten.

## Boundary

- individual rows originate from different surveys and methods;
- full heterogeneous covariance is `TOKEN_VAZIO`;
- survey cross-covariances/overlap are not yet represented;
- the current joint pipeline's growth-index expression is a proxy and remains claim-blocked by the E0 gate;
- paper-grade inference requires validated D(z)/perturbations and a covariance/overlap policy.

`SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM`
