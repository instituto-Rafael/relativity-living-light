# RLL Real-Data Evidence Bridge V1 — append-only receipt

Date: 2026-09-12  
Parent: merged PR #878 / E0 cosmology preflight  
Claim allowed: **false**

## Delta

1. External literature/evidence registry pins DESI DR2, Pantheon+, Planck distance priors, a historical fσ8 compilation source, and a modern growth-method reference.
2. Published DESI/Pantheon+ numbers are marked context-only, never optimizer targets.
3. A provenance error is superseded append-only: historical `data/results/model_comparison.json` points the growth input to DOI `10.1093/mnras/stw1614`, which is unrelated to the growth compilation. The active provenance anchor is Mehrabi/Basilakos/Pace 2015, DOI `10.1093/mnras/stv1478`, Table 2.
4. The legacy mixed `Hz_data_real.csv` remains immutable. A new 28-row `Hz_cosmic_chronometers_independent.csv` excludes obvious BAO-derived H(z) rows before future joint fits.
5. The joint pipeline is routed to the independent H(z) partition for successor runs.
6. Growth and CMB remain exploratory/claim-blocked until the E0 physics gates are repaired.

## F_ok

Real-data identity, hashes, covariance shape, source URLs, literature identities and obvious probe-overlap are now machine-checkable.

## F_gap

- flat closure / E(0)=1 still requires successor implementation;
- CMB l_A still requires validated r_s(z*);
- growth still requires D(z)/perturbations plus covariance/overlap policy;
- Pantheon+ full fit remains a separate validation surface.

## F_next

Run the flat-closure successor on the independent H(z)+DESI background partition, preserve historical outputs, and compare old/new results before MCMC.

SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
