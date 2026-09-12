# RLL Cosmology E0 Preflight — append-only receipt

Date: 2026-09-12  
Target authority: `instituto-Rafael/relativity-living-light` / `rll/lab`  
Change type: fail-closed scientific-promotion gate  
Claim allowed: **false**

## Source observation

The current joint real-data pipeline fits `Om` and `OL` independently while no `Ok` parameter or closure constraint is present. With `H(z)=H0*E(z)`, the optimizer therefore admits `E(0) != 1`; a fitted `H0` at an optimizer bound cannot be interpreted as the physical present-day Hubble constant until normalization is restored.

The same pipeline currently evaluates the growth contribution with a growth-index proxy proportional to `sigma8_0 * Omega_m(z)^0.55` and uses `r_d` inside the compressed-CMB acoustic-scale expression `l_A`. These are useful exploratory approximations but are not promoted as precision growth/CMB evidence by this gate.

## Delta

- added executable `tools/rll_cosmology_e0_preflight.py`;
- added fail-closed policy `data/governance/RLL_COSMOLOGY_E0_GATE_V1.json`;
- added focused regression tests;
- added a read-only GitHub Actions workflow that emits an auditable JSON report;
- preserved all historical result JSON/CSV files unchanged.

## Gate semantics

The ordinary preflight command records the current state without failing CI:

`python tools/rll_cosmology_e0_preflight.py`

A future scientific-promotion step must use:

`python tools/rll_cosmology_e0_preflight.py --require-ready`

and will fail closed until the normalization, growth and CMB checks pass.

## F_ok

The ambiguity is now machine-detectable and auditable instead of living only in review prose.

## F_gap

The likelihood itself is not reparameterized in this change. A successor must derive the flat dark-energy density by closure (or introduce curvature consistently), replace/separate the growth proxy, and implement/validate `r_s(z*)` before MCMC/model-selection promotion.

## F_next

Implement the smallest successor that makes the flat LCDM baseline satisfy `E(0)=1` by construction, rerun the same real-data inputs, and compare the new fit against the historical artifact without overwriting it.

SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
