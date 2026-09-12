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
- Recorded that arXiv:2602.18761 reports `w0=+0.49 +/- 0.25`, not `-0.49 +/- 0.25`.
- Separated custom-license interoperability from scientific falsifiability.

## Boundary

A negative-`wa` best-fit point is not a direct observable and is not by itself a falsification of RLL.

The decisive gate is posterior overlap under a matched likelihood and validated local/global mapping.

```text
SIGN_TENSION != FALSIFIED
LOCAL_CPL_MAP != GLOBAL_LIKELIHOOD_EQUIVALENCE
CUSTOM_LICENSE != NON_FALSIFIABLE
```

## F_next

Materialize a public DESI chain; use `P(wa>=0|D)` only as a coarse pre-gate, then compute 2D posterior/HPD overlap with the full RLL-accessible `(w0_eff,wa_eff)` domain under pinned dataset/priors/version.

`claim_allowed=false`
