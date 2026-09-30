# RLL w0-wa sign/falsifiability audit — append-only receipt

Date: 2026-09-12  
Parent: rll/lab  
Claim allowed: **false**

## Delta

- Corrected isolated-sector formula:
  `wa_s=f0(1-f0)(3+1/wt)`.
- Derived canonical total-dark local CPL coordinate including `Omega_Lambda`.
- Proved under canonical positive bounds:
  `wa_eff >= 0`.
- Reclassified the issue from "model not falsifiable" to:
  `STRUCTURAL_SIGN_TENSION_POSTERIOR_OVERLAP_REQUIRED`.
- Recorded version discrepancy for 2602.18761: the currently indexed arXiv abstract shows `w0=+0.49 +/- 0.25`, while peer-reviewed JCAP 2026(06) 043 shows `w0=-0.49 +/- 0.25`; the published value is the active benchmark.
- Separated custom-license interoperability from scientific falsifiability.

## Boundary

A negative-`wa` best-fit point, even paired with the published negative `w0`, is not a direct observable and is not by itself a falsification of RLL.

The decisive gate is posterior overlap under a matched likelihood and validated local/global mapping.

```text
SIGN_TENSION != FALSIFIED
LOCAL_CPL_MAP != GLOBAL_LIKELIHOOD_EQUIVALENCE
CUSTOM_LICENSE != NON_FALSIFIABLE
```

## F_next

Use the public supplement DOI `10.5281/zenodo.18629072` as the reproduction source; first identify and verify the exact w0wa chain inside `paper_data.tar.gz`, then use `P(wa>=0|D)` only as a coarse pre-gate and compute 2D posterior/HPD overlap with the full RLL-accessible `(w0_eff,wa_eff)` domain.

`claim_allowed=false`
