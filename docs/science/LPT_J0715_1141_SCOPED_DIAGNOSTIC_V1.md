# GPM J071507-114153 — isolated LPT observational diagnostic

**Scope:** source-informed local diagnostic; not a physical orbital fit, and not RLL cosmological confirmation.

## Reuse without duplicating producers

- B06 (`data/registries/rll_operational_integration_registry.json`): plasma/FRB observables and standard ν^-2 delay null.
- B07 (same registry): magneto-optical and instrumental/Faraday nulls.
- `data/contracts/rll_retarded_spacetime_state.v1.yml`: propagation environment variables and truth/claim boundaries.
- The new standalone `src/rll/lpt_j0715_1141.py` does **not** change existing RLL background fitting, astrophysical source data, or any workflow.

## Literature and attribution

- McSweeney et al. (2026), *A long-period transient with a Sun-like companion*, Nature Astronomy, https://doi.org/10.1038/s41550-026-03016-z.
- Authors' pulse data: https://doi.org/10.5281/zenodo.21386095.
- Authors' processing software: https://github.com/robotopia/j0715-1141-analysis. **Not copied**, upstream license needs independent checking before reuse.

## Input contract and examples

**ToA diagnostic:** UTF-8 CSV with `pulse_number,toa_seconds` using an explicit integer pulse number, increasing timestamps on **one already-corrected declared time standard**, and a declared clock in **seconds**. The nominal 7.9 min is an approximate *reference*, not an independently fitted ephemeris. Example:

```sh
python src/rll/lpt_j0715_1141.py --mode toa --input /path/to/normalized_toa.csv --period-seconds 474
```

**Faraday diagnostic:** UTF-8 CSV with `orbital_phase,rm_rad_m2,rm_sigma_rad_m2`; phase is fraction [0,1), RM comes from a prior multi-frequency polarimetric fit, uncertainty is positive. The script compares a constant-RM null against a **fixed first orbital harmonic**, for a descriptive delta χ², *not* a significance or independent RLL mechanism test.

```sh
python src/rll/lpt_j0715_1141.py --mode rm --input /path/to/normalized_rm.csv
```

**Tests:** `python -m unittest discover -s tests -p test_lpt_j0715_1141.py -v`.

## Gates / falsifiers

- Data ingestion is **NOT_RUN** until the Zenodo archive is actually inspected and its file-level identity, license, timestamps and input transformation are verified.
- Never use gaps to infer skipped pulse numbers. Degenerate phase sets, invalid RM uncertainty, missing headers, NaN/Inf and ambiguous units must fail closed.
- Against the physical baseline: evaluate barycentric timing, a binary Römer delay/orbital ephemeris, standard dispersion/Faraday, coronal variation and instrument calibration **before** testing any RLL residual; keep uncertainty and correlations.
- Synthetic passing tests validate only the *mathematical operators*. No real-dataset fits, strong-physics claims, or cosmological promotion follow.

**State:** `IMPLEMENTED_TESTED_SYNTHETIC_ONLY` only if executable tests return PASS; otherwise `IMPLEMENTED_UNTESTED`. `claim_allowed=false`. Rollback: abandon the isolated branch or revert its additive commit; no existing files changed.
