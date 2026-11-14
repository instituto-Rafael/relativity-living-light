# Scientific review | RLL, DESI DR2, DES-Dovekie and model comparators
**Version:** review draft 1.0 · **Cut-off:** 2026-11-14 · **State:** DRAFT / UNDER_REVIEW · **Scientific claim gate:** `claim_allowed=false`

**Authorial project:** Relativity Living Light (RLL). This document is a critical *review of the present implementation and evidence*, not a referee-accepted scientific paper. Neither a tag nor a repository DOI is equivalent to peer review.

## Abstract

The Relativity Living Light (RLL) project explores an additional logistic term in the homogeneous expansion history. We document the implemented background function, its null limit, the distinction between mathematical consistency and physically conserved stress-energy, and the competing \(\Lambda\)CDM, constant-\(w\)CDM, and CPL \(w_0w_a\)CDM descriptions. We reconcile the model's local effective \(w_0,w_a\) mapping with the newly published DES-Dovekie reanalysis and DESI DR2 BAO results. Under the current RLL pressure prescription, non-negative sector densities, and positive transition width, the local CPL derivative has \(w_{a,\mathrm{eff}}\geq0\), in tension with the negative-\(w_a\) region preferred by some published combined analyses. The implemented density/pressure pair also fails separate-fluid continuity during the transition unless pressure or interaction terms are specified differently. We therefore make no predictive-success or model-superiority claim. We outline reproducible, covariance-aware observational tests, provenance requirements, failure criteria, and a publication-grade figure plan.

**Keywords:** cosmological expansion; dynamical dark energy; BAO; Type Ia supernovae; DESI; DES-Dovekie; inverse problems; scientific reproducibility; model comparison.

## 1. Scope, attribution, and evidence levels

**Source distinction.** [DOC] Data vectors supplied by DESI, DES, Pantheon+, CMB collaborations are observations or reduced data; their fitted \(w_0,w_a\) parameters are *posterior inferences under a model*, not direct telescope readouts. [DOC] RLL's equations and code define a competing hypothesis. [DERIVATION] Algebra below is conditional on specific definitions. [NOT_RUN] No new joint likelihood, DESI-official bit-level ingest, or independent physical experiment was executed in this editorial review.

**Responsible attribution.** Cite the full experimental collaborations and original authors for instrument data, likelihood methods, calibrations and model interpretations. Credits for geometry in the separate private `papers` repository remain with its declared author and producing repository. The repository `rafaelmeloreisnovo/math` currently describes an OpenAI-generated mathematical manuscript collection; do not reassign its authorship to RLL. Bibliographic cross-links do not confer priority, equivalence of proofs, or permission to relicense third-party material.

## 2. Cosmological models: declarations before comparison

For a spatially flat background and negligible radiation within the limited low-redshift comparator:

\[
E(z)=\frac{H(z)}{H_0}.
\]

- **Flat \(\Lambda\)CDM:** \(E^2(z)=\Omega_m(1+z)^3+(1-\Omega_m)\).
- **Constant-\(w\)CDM:** \(E^2(z)=\Omega_m(1+z)^3+(1-\Omega_m)(1+z)^{3(1+w)}\).
- **CPL \(w_0w_a\)CDM:** \(w(a)=w_0+w_a(1-a)\) and
  \[
  E^2(z)=\Omega_m(1+z)^3+(1-\Omega_m)(1+z)^{3(1+w_0+w_a)}\exp[-3w_az/(1+z)].
  \]
- **RLL logistic as implemented in `rll_vs_lcdm.py`:**
  \[
  f(z)=\frac{1}{1+\exp[(z-z_t)/w_t]},\qquad w_t>0,
  \]
  \[
  g(a)=f(a)+[1-f(a)]a^{-3},\quad a=(1+z)^{-1},
  \]
  \[
  E_{\rm RLL}^2(a)=\Omega_m a^{-3}+\Omega_\Lambda+\Omega_{s0}g(a),
  \quad\Omega_\Lambda=1-\Omega_m-\Omega_{s0}.
  \]
  This benchmark omits optional radiation, magnetic and plasma terms documented elsewhere. Those terms are **not observationally calibrated merely because they are present symbolically**. The null model \(\Omega_{s0}=0\) reproduces the background form of flat \(\Lambda\)CDM.

**Physical scope:** these background functions do not alone provide a covariant action, perturbation theory, growth predictions, lensing observables or microscopic demonstration of a "photonic superposition" sector.

## 3. Priority mathematical and physical audit

### 3.1 Local effective CPL coordinates: sign test

The checked repository source `scripts/map_rll_to_w0wa_eff.py` defines
\[
w_{\rm dark}(a)=-\frac{\Omega_\Lambda+\Omega_{s0}f(a)}
{\Omega_\Lambda+\Omega_{s0}g(a)},\quad
w_{0,\mathrm{eff}}=w_{\rm dark}(1),\quad
w_{a,\mathrm{eff}}=-\left.\frac{\mathrm dw_{\rm dark}}{\mathrm da}\right|_{a=1}.
\]

Let \(f_0=1/(1+\exp[-z_t/w_t])\) and \(G=\Omega_\Lambda+\Omega_{s0}>0\). Direct differentiation yields
\[
w_{0,\mathrm{eff}}=-\frac{\Omega_\Lambda+\Omega_{s0}f_0}{G},
\]
\[
\boxed{w_{a,\mathrm{eff}}=
\frac{\Omega_{s0}(1-f_0)}{G^2}
\left[\frac{f_0G}{w_t}+3(\Omega_\Lambda+\Omega_{s0}f_0)\right]\geq0.}
\]

This inequality is conditional on \(\Omega_{s0}\geq0,\Omega_\Lambda\geq0,w_t>0\) and \(0<f_0<1\). Under the model comparison defaults \(\Omega_m=0.315,\Omega_{s0}=0.059,z_t=1.164,w_t=0.405\), direct independent numeric/analytic calculation gives \(w_{0,\mathrm{eff}}\simeq-0.99540,\;w_{a,\mathrm{eff}}\simeq+0.02451\). **These are illustrative parameter mapping results, not a posterior fit.**

The proposal text reports \((-0.809,-0.618)\). That pair is an **unverified proposed mapping**, not derivable from the checked default canonical form under these sign assumptions. A separate formula, versioned parameters and independently checkable chain are required before it can be cited as a RLL prediction. Comparing two independent marginal differences with \(1\sigma\) error bars is *not* a joint \(68\%\) credible-region consistency test; the full \(2\times2\) covariance/posterior and a matching parameter definition are required.

This sign issue was already registered in `data/governance/RLL_W0WA_SIGN_FALSIFIABILITY_GATE_V1.json`. Do not promote it to a formal global falsification without mapping the entire allowed parameter domain into a matched joint likelihood.

### 3.2 Continuity equation: physical closure is unresolved

The checked existing scientific audit `docs/science/RLL_MATH_LITERATURE_COHERENCE_AUDIT_20260808.md` uses
\[
\rho_s=\Omega_{s0}\rho_{c0}g(a),\quad p_{s,\mathrm{doc}}=-\Omega_{s0}\rho_{c0}f(a).
\]
For a **separately conserved** FLRW component, \(\mathrm d\rho_s/\mathrm d\ln a+3(\rho_s+p_s)=0\). Instead,
\[
\frac{1}{\Omega_{s0}\rho_{c0}}\left[\frac{\mathrm d\rho_s}{\mathrm d\ln a}
+3(\rho_s+p_{s,\mathrm{doc}})\right]
=\frac{\mathrm df}{\mathrm d\ln a}(1-a^{-3}).
\]
This is nonzero during a genuine transition away from \(a=1\). It is a mathematical consistency constraint, **not** something corrected by graphical elegance or a better \(\chi^2\).

The physically distinct options are (A) derive a conserved effective pressure \(p_{\rm cons}=-\rho_s-(1/3)\mathrm d\rho_s/\mathrm d\ln a\), or (B) specify a covariant interaction/exchange \(Q_s\) with explicit balancing in another sector. These alternatives change the physical definition and may change CPL mapping and perturbation dynamics. They require a separately versioned model and model comparison rather than retrospective adjustment to fit observed signs.

## 4. External findings, with exact dataset labels

| Primary or peer-reviewed result | Data combination and model | Published inference | Scientific reading |
| --- | --- | --- | --- |
| DES Collaboration, 2026 [1] | DES-Dovekie (~1600 DES + ~200 low-z SNe) + DESI DR2 + CMB (Planck, ACT, SPT), flat CPL | \(w_0=-0.803\pm0.054,\;w_a=-0.72\pm0.21\); reported \(3.2\sigma\); Bayes odds roughly 5:1 | Authors call Bayesian preference **weak**. Quoted values are inferred constraints, not directly measured observables. |
| Lozano Torres, 2026 [2] | DESI DR2 + DES Y6 BAO + full Planck + supernovae + chronometers, CPL; the specific full-combination summary is in the paper | \(w_0=-0.740\pm0.082,\;w_a=-0.893\pm0.285\); \(\Delta\chi^2\sim-12\); \(\ln B_{\rm CPL,\Lambda}\sim-0.5\) | Frequentist improvement but **inconclusive** Bayes evidence vs \(\Lambda\)CDM. Do not present these numbers as independent measurements directly by telescopes. |
| DESI Collaboration, 2025 [3] | DESI DR2 BAO, 13 compressed primary observables in local RLL data | \(D_M/r_d,\;D_H/r_d,\;D_V/r_d\) constraints | Independent official source file and full survey covariance still need exact local validation. |
| Lodha et al. (DESI Collaboration), 2025 [4] | DESI BAO + CMB + Pantheon+, Union3 or DESY5 | Changing supernova sample changes model comparison; Pantheon+ gives inconclusive Bayes evidence for CPL vs \(\Lambda\)CDM | Report each dataset-specific combination separately, with priors and covariance. |
| Brout et al., 2022 [5] | Pantheon+ Type Ia supernovae | 1701 light curves, 1550 unique SNe | Multiple light curves are not independent unique objects. Pantheon+ and DES-Dovekie are different releases and must not be silently pooled. |

**Clarification of physical language:** \(w_0>-1,\;w_a<0\) in CPL can imply \(w(a)\) crosses \(-1\); the time dependence of \(\rho_{\rm DE}\) follows its continuity equation and *cannot* be replaced by saying simply "the universe is no longer consistent with \(\Lambda\)". The confidence significance is conditional on model, likelihood, prior and data combination. A 3.2-sigma preference is not definitive evidence of new physics.

## 5. Historical comparison: archived RLL results are not today's DESI+Dovekie fit

The audit in `results/coerente/2026-07-09_uploaded_validation_bayes/README.md` records 33 points, \(\chi^2_{\Lambda}=25.65409,\;\chi^2_{\rm RLL}=25.84226\), plus a legacy Bayes factor \(B_{\rm RLL,\Lambda}\approx0.00131497\). However the same audit flags an asymmetry: one \(\Lambda\)CDM log evidence is declared as a *fixed-parameter log likelihood*, which is not a fully matched Bayesian evidence computation. Hence **do not promote the ratio as definitive model odds**. Preserve it as a dated, limited archival artifact.

The later exploratory 13-observable BAO-only comparison is at [RLL_DESI_DR2_BAO_PANTHEON_CROSSWALK_20261114](RLL_DESI_DR2_BAO_PANTHEON_CROSSWALK_20261114.md) on its separate branch `research/desi-dr2-pantheon-source-audit-20261114`; its \(\chi^2/AICc\) values are not a likelihood matched to Dovekie/Planck. In that scoped analysis \(\Lambda\)CDM had the best AICc. No dataset/parameter result should be copied between these scopes without its methodology and provenance.

### Historical priority gate

- The verified RLL Git tag `v1.0.0` targets commit `0b3f4cb06efaa11008b37de519de581268bca5c0`, dated **2025-09-19**. The README examined at this exact commit does not contain the claimed specific \((-0.809,-0.618)\) calculation.
- DESI DR2 Results II was submitted **2025-03-18**, before that tag [3]. Therefore the tag alone cannot prove prediction prior to DESI DR2.
- DES-Dovekie first appeared as arXiv:2511.07517 in November 2025, after that tag [1], but this temporal order alone **does not establish a pre-registered numerical forecast**.
- Required evidence: exact immutable parent commit, file and line declaring parameter values; derivation/inputs; timestamp; documented freeze before relevant external results; no later hindsight tuning; comparison to all already available DESI measurements; independently rerun model. Until then `PRIOR_NUMERIC_FORECAST=NOT_VERIFIED`.

## 6. Reproducible experimental protocol

**P0 physical gate:** choose (A) separately conserved closure or (B) interaction with explicit source/exchange terms *before* likelihood fitting. Compute independent exact/symbolic continuity test. Define perturbation equations and growth prescriptions for any claims using \(f\sigma_8\), lensing or CMB.

**P1 observational inputs:** freeze source versions and licenses for the DESI DR2 BAO official vector, full covariance and likelihood; Pantheon+ official light-curve/magnitude vector and STAT+SYS covariance; DES-Dovekie Hubble diagram and its supplied **precision** (inverse-covariance) matrix; Planck (full or explicitly compressed, never interchangeable); chronometers only if truly independent from BAO; and growth probes with covariance.

**P2 inference parity:** use the same selection mask, distance convention, nuisance marginalization, radiation/neutrino/curvature baseline, calibration parameters, priors, parameter count, numerical accuracy and convergence criteria for \(\Lambda\)CDM, constant \(w\), CPL and each frozen RLL closure. Label BAO-only, SNe-only, CMB-only and joint combinations separately; use \(\ln\mathcal{L}\), \(\chi^2\), AICc, posterior intervals, and evidence \(\ln Z\) only when actually computed by a normalized likelihood with declared proper priors.

**P3 adversarial checks:** verify covariance positive definiteness and double counting; DES-Dovekie stored matrix is a *precision* matrix in the existing fetch/likelihood code, not a covariance; perform 2D posterior overlap \((w_0,w_a)\), zero-sector limit, parameter-boundary and prior-sensitivity tests, simulated injection/recovery only as software tests, and independent code reproduction.

**P4 final claim:** publication claims require exact environment lock, SHA-256 of original inputs, executable commands, artifacts, numerical tolerances, figures derived from traced outputs and external review. `IMPLEMENTED_UNTESTED≠PASS`; an existing `dynesty` import is not proof of a successful nested-sampling run.

### Data-to-claim traceability

~~~mermaid
flowchart TD
    A["DESI DR2 / DES-Dovekie / Pantheon+ / CMB"] --> B["Pinned input + licensing + covariance/precision contract"]
    B --> C["Reproducible likelihood + nuisance/priors"]
    D["Frozen RLL physical closure"] --> C
    E["LCDM / wCDM / CPL comparators"] --> C
    C --> F["Independent fits + convergence and perturbation gates"]
    F --> G{"Adversarial consistency checks pass?"}
    G -->|No| H["Scoped failure / unresolved gap / correction receipt"]
    G -->|Yes| I["Evidence-graded statement, not automatic superiority"]
~~~

*Diagram 1 (conceptual workflow, not a plot of physical data):* each edge represents a needed verification operation, not a result already obtained. A text alternative: datasets plus physics definitions feed a consistent likelihood, followed by diagnostics and an explicit claim gate.

## 7. Related geometric investigations, correctly scoped

The `papers` repository includes mathematical constructions involving polygons, chords, triangulations and provenance. They may contribute exact geometry and robust parameterization to inverse problems. However \(\mathbb R^2\to\mathbb R^3\) projection inversion is generally nonunique, and triangulating a circumsphere does not yield a unique object's volume from angular data alone. BAO cosmological distances are **radial/angular standard-ruler observables**; to claim a new geometric RLL prediction one must derive an identifiable change to \(H(z)\), \(D_M(z)\), \(D_H(z)\), lensing or growth **before** confronting the data, and test against null/alternative models. Metaphorical Poincaré spheres are not evidence of cosmic topology.

## 8. Bibliography (primary/peer-reviewed sources)

1. **DES Collaboration** (2026). *The Dark Energy Survey supernova program: a reanalysis of cosmology results and evidence for evolving dark energy with an updated Type Ia supernova calibration*. **Monthly Notices of the Royal Astronomical Society**, 548, stag632. DOI: https://doi.org/10.1093/mnras/stag632 ; arXiv: https://arxiv.org/abs/2511.07517 .
2. **Lozano Torres, J. A.** (2026). *Dynamical dark energy from DESI DR2 and DES Year 6 BAO, supernovae, and cosmic chronometers: a 3σ preference without decisive Bayesian evidence*. **Monthly Notices of the Royal Astronomical Society**, 551, stag1607. DOI: https://doi.org/10.1093/mnras/stag1607 .
3. **DESI Collaboration**, Abdul-Karim, M., et al. (2025). *DESI DR2 Results II: Measurements of Baryon Acoustic Oscillations and Cosmological Constraints*. **Physical Review D**, 112, 083515. https://arxiv.org/abs/2503.14738 . Official publications and chains: https://data.desi.lbl.gov/doc/papers/dr2/ .
4. **Lodha, K., et al. (DESI Collaboration)** (2025). *Extended dark energy analysis using DESI DR2 BAO measurements*. **Physical Review D**, 112, 083511. DOI: https://doi.org/10.1103/w4c6-1r5j ; preprint https://arxiv.org/abs/2503.14743 .
5. **Brout, D., et al.** (2022). *The Pantheon+ Analysis: Cosmological Constraints*. **The Astrophysical Journal**, 938, 110. DOI: https://doi.org/10.3847/1538-4357/ac8e04 . Data release: https://github.com/PantheonPlusSH0ES/DataRelease .
6. **DES Collaboration** (2026). *DES Year 6 Cosmology Results*. Primary collaboration index: https://www.darkenergysurvey.org/des-y6-cosmology-results-papers/ .

**Repository sources (not peer-reviewed validations):** [Canonical RLL model](../canonicos/14_MODELO_COSMOLOGICO_RLL.md), [existing mathematical/physics failure audit](../science/RLL_MATH_LITERATURE_COHERENCE_AUDIT_20260808.md), [Sign-falsifiability registry](../../data/governance/RLL_W0WA_SIGN_FALSIFIABILITY_GATE_V1.json), [Dovekie three-model likelihood](../../products/rll-evidence-runner/src/rll_evidence/dovekie_fit_three_model.py), [Nested-evidence implementation](../../products/rll-evidence-runner/src/rll_evidence/dovekie_nested_evidence.py), [source fetch contract](../../scripts/fetch_dovekie_inputs.py).

## 9. Editorial and governance

The [scientific editorial design standard](../editorial/RLL_PUBLICATION_DESIGN_STANDARD_20261114.md) governs diagrams, reproducibility, bibliographic attribution and graphical claims. The [reader-facing overview](../presentation/30_SCIENTIFIC_RESEARCH_OVERVIEW_20261114.md) is an accessible synopsis, **not a substitute** for equations and experiments.

**R3** · F_ok: sources/canonical implementation and mathematical limitations checked; F_gap: full experimental reanalysis, complete historical priority and resolved physical closure not established; F_next: physical closure specification with a fixed signed test, then covariance-complete data rerun. **FIAT LUX.**
