# RELATIVITY LIVING LIGHT
### Research overview · Evidence-first cosmological modeling
**Review edition — 14 November 2026** · **Scientific stage: exploratory and falsifiable** · **Peer-review status: not established** · **`claim_allowed=false`**

> The purpose of this page is to help a cosmologist, mathematician, reviewer, or interested reader understand what RLL specifies, what has been tested, and what remains unresolved. It is not a press release or a declaration of discovery.

[Read the full critical review](../research/RLL_DESI_DOVEKIE_CRITICAL_REVIEW_20261114.md) · [Research data](../../data/real/cosmology/README.md) · [Reproducibility](20_PAPERS_REPRODUCIBILITY.md) · [Publication and figure standard](../editorial/RLL_PUBLICATION_DESIGN_STANDARD_20261114.md)

---

## Research question

Can a reproducibly defined additional component in the cosmological expansion background offer explanatory or predictive value **beyond** standard \(\Lambda\)CDM and well-established dynamical dark-energy alternatives, while satisfying stress-energy continuity, uncertainty calibration, and external observational likelihoods?

**What is authored here?** A candidate phenomenological RLL logistic background with a null limit, mathematical and experimental tests, and a growing computational corpus. The proposal's use of geometric or photonic terminology is *not a measured microphysical origin*.

**What is already known?** DESI, DES, Pantheon+, and CMB collaborations independently provide constraints on expansion history and dark-energy models. Their work must be cited and their inference procedures reproduced; numerical resemblance is not priority or independent discovery.

## The observational picture

| Dataset or peer-reviewed analysis | Model and exact scope | Finding | Interpretation |
| --- | --- | --- | --- |
| DES-Dovekie reanalysis, DES Collaboration (2026) | DES-Dovekie + DESI DR2 BAO + Planck/ACT/SPT CMB, flat CPL | \(w_0=-0.803\pm0.054\), \(w_a=-0.72\pm0.21\), reported 3.2σ | Bayes odds ~5:1 represent **weak** preference, per original authors [1]. |
| DESI DR2 + DES Y6 BAO, SNe & chronometers, Lozano Torres (2026) | Joint CPL analysis with full Planck likelihood; depends on SNe compilation | Representative full-combination \(w_0=-0.740\pm0.082\), \(w_a=-0.893\pm0.285\) | Improved \(\chi^2\) over ΛCDM, but Bayes factor against ΛCDM **inconclusive** [2]. |
| Pantheon+ (2022) | 1,701 light curves from 1,550 distinct SNe | Distance-redshift constraints | Requires statistical/systematic covariance, redshift convention, standardization and nuisance handling [3]. |
| RLL local BAO-only review (2026-11-14) | 13 RLL-stored DESI observables; approximated block covariance | Best AICc in this **exploratory scope**: ΛCDM | Not an official DESI joint analysis and not a Pantheon+/CMB model ranking [4]. |

*Reading rule:* \(w_0\) and \(w_a\) are inferred parameter posteriors under a specified model. **DESI measures redshifts and BAO features; it does not directly measure the truth of CPL or RLL.**

## Model architecture

~~~mermaid
flowchart LR
    subgraph Sources["Observed sources"]
      D["DESI DR2<br/>BAO distance ratios"]
      S["Pantheon+ / DES-Dovekie<br/>SN Hubble diagram"]
      C["CMB / chronometers / growth<br/>separate likelihoods"]
    end
    subgraph Theory["Frozen predictions"]
      L["Lambda-CDM"]
      W["constant-w / CPL"]
      R["RLL background<br/>closure pending"]
    end
    D --> I["Versioned data + full<br/>covariance/precision and masks"]
    S --> I
    C --> I
    L --> P["Matched likelihood, nuisance<br/>parameters, priors, convergence"]
    W --> P
    R --> P
    I --> P
    P --> G{"Physical consistency<br/>and evidence gates"}
    G -->|"passed in declared scope"| O["Scoped scientific result"]
    G -->|"failed or not tested"| H["Explicit limitation / next falsifier"]
~~~

*Figure 1 — conceptual, not observational data.* **Alt text:** observational catalogues are fed through provenance and covariance checks; independently defined models meet a common likelihood and a physical closure gate; only a scoped result can be reported.

## Key mathematical finding: transparent negative evidence

The implementation `rll_vs_lcdm.py` includes a logistic extension. Under the *currently documented dark-sector pressure prescription*, positive transition width and nonnegative sector densities, its **local** effective CPL slope satisfies
\[
w_{a,\mathrm{eff}}\geq0.
\]

Some DES-Dovekie/DESI combinations favor \(w_a<0\). That is a real, falsifiable **sign tension** under stated assumptions; a full model-level exclusion still requires a matched likelihood and domain-overlap calculation. The repository also records a nonzero continuity residual for the presently documented density/pressure pair if one assumes **separate conservation**.

Both limitations are described and derived in the [critical mathematical and observational review](../research/RLL_DESI_DOVEKIE_CRITICAL_REVIEW_20261114.md). They are not hidden in an appendix.

## Interpreting the project's history

The RLL `v1.0.0` Git tag targets a 2025-09-19 commit, which is an independently checkable **document state**. It is not evidence that the specific pair \((-0.809,-0.618)\) was already predicted at that time; the archived README examined does not contain the required calculation. The DESI DR2 Results II preprint dates from March 2025. Both facts must be reported when discussing timing or authorship.

### Evidence maturity

| Element | Evidence grade | What remains |
| --- | --- | --- |
| Published DESI/DES/Pantheon+ results | External primary sources | Check release/model/covariance each reuse |
| RLL logistic algebra and null limit | Definition / derivation | Resolve stress-energy closure |
| Local \(w_0,w_a\) sign restriction | Algebraic check + existing source gate | Global posterior overlap and alternative closure |
| RLL observed BAO exploratory comparison | Scoped local calculation | Official input/likelihood verification |
| RLL Pantheon+/DES-Dovekie solver code | Implemented code | This review did not rerun full pipeline |
| Earlier 33-point Bayes artefact | Historical source audit | Symmetric evidence methodology and raw inputs |
| General physical superiority / novelty | **NOT_ESTABLISHED** | Independent replication, robust pre-registration and peer review |

## Figure portfolio to be rendered only from verified outputs

1. **Observed BAO ratios versus redshift:** plot \(D_M/r_d,D_H/r_d,D_V/r_d\) in separate, unit-labelled panels; points carry source DOI and covariances are retained in the statistical calculation.
2. **Matched distance-modulus residuals:** Pantheon+ or DES-Dovekie, explicitly **not silently merged**; show residuals and covariance-aware uncertainty, not invented scatter.
3. **\(w_0,w_a\) posterior contours:** actual joint 68%/95% credible contours; mark the \(\Lambda\) point and the *entire RLL-accessible domain*, not invented ellipses from separate marginal errors.
4. **Physical consistency residual:** \(\mathcal C(a)\) against \(z\) with declared \(\Omega_{s0},z_t,w_t\), and reference zero. This is a calculated diagnostic, not observed cosmology.

Each plot requires executable source, hashes/versions of input, units, accessibility, caption, and an explicit statement of whether its points are observed, derived, or simulated. **No scientific plots are fabricated in this document.**

## Bibliography and credit

The [versioned BibTeX catalogue](../editorial/RLL_REFERENCES_EXTERNAL_20261114.bib) is provided for scholarly citation workflows, separate from data validation.

[1] DES Collaboration (2026). *The Dark Energy Survey supernova program: a reanalysis ... updated Type Ia supernova calibration*. MNRAS 548, stag632. https://doi.org/10.1093/mnras/stag632

[2] Lozano Torres, J. A. (2026). *Dynamical dark energy from DESI DR2 and DES Year 6 BAO, supernovae, and cosmic chronometers*. MNRAS 551, stag1607. https://doi.org/10.1093/mnras/stag1607

[3] Brout, D., et al. (2022). *The Pantheon+ Analysis: Cosmological Constraints*. ApJ 938, 110. https://doi.org/10.3847/1538-4357/ac8e04

[4] DESI Collaboration (2025). *DESI DR2 Results II: Measurements of BAO and Cosmological Constraints*. Physical Review D 112, 083515. https://arxiv.org/abs/2503.14738

**Other relevant original works:** Lodha et al., *Extended dark energy analysis using DESI DR2 BAO measurements* (2025), https://doi.org/10.1103/w4c6-1r5j; and the original collaborative paper indexes at https://data.desi.lbl.gov/doc/papers/dr2/ and https://www.darkenergysurvey.org/des-y6-cosmology-results-papers/.

We thank the teams who publicly disseminate calibrated observations, likelihood implementations, and reproducibility guidance. Attribution is not an endorsement of RLL.

**R3** — Confirmed: research scope, primary sources, mathematical gates; unresolved: matched likelihood/physics and peer review; next: correct closure and re-run with official covariance. **FIAT LUX.**
