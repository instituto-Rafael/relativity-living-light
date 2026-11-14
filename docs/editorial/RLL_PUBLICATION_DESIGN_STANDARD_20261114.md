# RLL | Scientific publishing, editorial design and data-visualization standard
**Version:** 1.0 draft · **2026-11-14** · **Owner:** RLL research documentation · **Status:** editorial proposal, not journal acceptance
**Gate:** `claim_allowed=false` unless a separately approved evidence contract authorizes a narrower claim.

## Editorial intent

Make every artifact legible to a technically skeptical reader *without concealing unresolved hypotheses*. The audience includes doctoral researchers in cosmology, data analysis, applied mathematics, experimental science, methods and information design. Academic style is earned by reproducible definitions and transparent uncertainty, not by decorative scientific imagery, hyperbole, unsupported peer-review language, or merely labeling a document “PhD level”.

### Reader experience and information architecture

| Layer | Primary reader question | Canonical destination |
| --- | --- | --- |
| 00 — Orientation | What is RLL and what is not yet known? | [Scientific research overview](../presentation/30_SCIENTIFIC_RESEARCH_OVERVIEW_20261114.md) |
| 01 — Mathematics | Which equations, domains and assumptions define the model? | [Critical model review](../research/RLL_DESI_DOVEKIE_CRITICAL_REVIEW_20261114.md), [Model definition](../canonicos/14_MODELO_COSMOLOGICO_RLL.md) |
| 02 — Observations | Which collaborations measured what, and where are the official data? | [Real data contract](../../data/real/cosmology/README.md) |
| 03 — Experiments | Can the exact likelihood, inputs and outputs be reproduced? | [Papers / reproducibility](../presentation/20_PAPERS_REPRODUCIBILITY.md) |
| 04 — Adversarial review | Which predictions fail, and what could disprove them? | [Existing math/physics audit](../science/RLL_MATH_LITERATURE_COHERENCE_AUDIT_20260808.md), [Sign gate](../../data/governance/RLL_W0WA_SIGN_FALSIFIABILITY_GATE_V1.json) |
| 05 — Historical provenance | Were values written before new results? | Exact frozen Git tree, commit ID, file path and diff; tag alone insufficient |
| 06 — Research corpus | What mathematical papers are relevant? | Private `rafaelmeloreisnovo/papers`; math producer `rafaelmeloreisnovo/Matem-tica-`; **no body copying** |

### One-screen executive summary convention

Lead with a concise abstract (approximately 150–250 words), followed by a table of 3–6 attributable results and an equally prominent **Limitations / Negative evidence** box *without decorative success colors*. Always label data release, date, full model, inference status, covariance and exact metric. The shortest page must be scientifically self-sufficient.

## Typesetting / editorial hierarchy

- **H1:** one descriptive title; **H2:** article sections; **H3:** local derivations. Avoid ornamental all-caps claims or emoji in journal manuscripts; the symbolic FIAT LUX identity may remain in project-only colophon, never as a physical result.
- **Body:** one idea per paragraph, 60–85 characters per line in narrow reading layouts, generous whitespace, mathematical variables consistently typeset in LaTeX. Avoid vague terms like “proves”, “unprecedented”, “revolutionary”, “exact agreement” without an explicit test.
- **Equations:** numbered in publication outputs and cross-referenced near the claim. Define every symbol, units, admissible range, normalization, underlying reference frame, and whether exact/approximate. State why each transformation preserves or changes a geometric invariant.
- **Tables:** columns align numerical precision, specify physical units and uncertainty basis. Do not give numbers to more significant digits than the inputs support. Footnotes explain likelihood dataset overlap, priors and whether \(\sigma\) is marginal, joint or test-statistic derived.
- **References:** author or collaboration, year, complete title, journal, volume, page/article number, DOI and data-release link. Cite actual methods papers used for calibration, covariances, priors and tools; preserve the author's credit. No invented institutional endorsement or journal-review label.
- **State:** `OBSERVED`, `DERIVED`, `HYPOTHESIS`, `IMPLEMENTED_UNTESTED`, `PASS_SCOPED`, `FAIL`, `TOKEN_VAZIO` have noninterchangeable meanings. Footnotes must not erase a negative result.

## Figure design and reproducibility system

### Figure categories and semantic provenance

| Type | Visual encoding | Required legend/caption |
| --- | --- | --- |
| Measured DESI BAO ratios | Points with uncertainty bars, redshift as x-axis | Survey, tracer, units, release, covariance pointer |
| Pantheon+/Dovekie SNe | Residuals relative to named fiducial only | Exact SN sample, calibration, z convention, covariance/precision, offset treatment |
| \(\Lambda\)CDM/wCDM/CPL/RLL fit | Solid/dashed model lines with model labels **in legend and near curve** | Parameters, fitted/fixed status, input SHA, likelihood version, no implied preference from line proximity |
| Bayesian parameter contour | Joint posterior contour with 68/95% credible labels | Priors, reference point, whether actual chains or analytic approximation; never derive ellipse from 1D errors without correlation |
| Geometric construction | Thin orthogonal axes, polygons, identified transforms and reference frames | Coordinate origin, orientation, projection, normalization, source of geometry and impossibility of 2D→3D uniqueness |
| Synthetic/adversarial test | Distinct marker/line pattern, explicit `SIMULATED` label | Synthetic seed, generating parameters, purpose, not a real survey measurement |
| Research flowchart | Mermaid or authored vector diagram, arrow semantics in caption | Conceptual workflow, never misrepresented as a cosmological fit |

### Accessibility and visual standards

1. Use vector-first plots (SVG/PDF when appropriate), with text legible at single-column journal widths and rendered export tested. The manuscript source must not embed protected font assets.
2. Choose perceptually distinct line/marker combinations that remain interpretable in grayscale and for common color-vision deficiencies. Line-style and point-shape must encode identity **in addition to** hue.
3. Keep axes on the same physical scale when figures are compared. Any intentional axis truncation or normalization must be explicit and nonmisleading.
4. Include textual alternatives for every diagram and key data figure; avoid screenshots of equations. Provide high-contrast labels, adequate margins, and no unnecessary 3D effects, gradients or decorative stars resembling data points.
5. Display confidence/credible contours with model/prior captions and *not* as “proof halos”; report when a boundary condition or null-limit makes parameters non-identifiable.
6. Each figure must have: `figure_id`, `source_ref`, `input_sha256`, `code_ref`, `environment_ref`, `transformations`, `uncertainty_policy`, `caption`, `alt_text`, `evidence_state`. Unknown values remain typed empty.
7. Do not use images produced by generative AI as scientific observational evidence. If conceptual illustrations are used, explicitly label *artist’s impression* and state that dimensions are not measured.
8. When a visual depicts \(T^7\), a Poincaré sphere, a geodesic sphere, a projected cube or a regular polygon, state whether it is a mathematical parametrization, schematic rendering, topological equivalence or observed geometry. These are distinct statements.

### Four canonical figure captions (no plots claimed)

- **Figure A.** “BAO observables from DESI DR2, by tracer and redshift. Points denote published compressed measured ratios; a full covariance matrix is used for inference. The displayed errors alone do not encode all cross-correlations. Model lines are generated using the frozen likelihood and declared model parameters.”
- **Figure B.** “Joint posterior constraints on the CPL \(w_0\)–\(w_a\) plane from precisely named BAO/CMB/SNe combinations. Contours are sourced from the corresponding chain or internally reproduced and convergence-checked chain, not inferred from independent 1D confidence intervals.”
- **Figure C.** “The canonical RLL local mapping and its \(w_{a,\mathrm{eff}}\geq0\) accessible domain under the declared assumptions. This is a mathematical model diagnostic; a cosmological likelihood comparison would require full observable predictions and domain-dependent priors.”
- **Figure D.** “Separate-fluid continuity residual of the documented RLL density/pressure prescription. A nonzero residual indicates incomplete closure for the assumed noninteracting fluid, not experimental confirmation of energy transfer.”

## Experimental and model-comparison discipline

~~~mermaid
flowchart TD
    S["Versioned primary observational source"] --> P["Extract schema, units, sample masks, checksums"]
    P --> C["Covariance / precision verified and named"]
    M["Frozen theory: equations, closure and limits"] --> L["Common likelihood and nuisance policy"]
    C --> L
    L --> T["Numerical fit, MCMC or nested sampling"]
    T --> A["Convergence, null limit, injected falsifiers, alternative priors"]
    A --> E{"Predeclared acceptance met?"}
    E -->|yes| R["Scoped result with exact citations, code, data and figures"]
    E -->|no or not run| G["Typed gap / failure / follow-up test"]
~~~

*Diagram 1: scientific publication workflow, conceptually specified. The flow does not assert that all stages have been completed.*

**Checklist before release:** (i) specify target observable in its natural units; (ii) pin independent primary datasets; (iii) avoid duplicated/correlated likelihood terms; (iv) freeze model, parameters, nuisance, masks and priors; (v) verify physical energy/closure; (vi) run and archive exact commands and log; (vii) report convergence/optimizer boundaries and negative results; (viii) generate plots only from verified outputs; (ix) cross-validate a second implementation where practical; (x) invite expert peer review and incorporate corrections by versioned successor, not silent replacement.

## Acknowledgments, authorship and ethics

The project may declare its own author(s) or contributor roles; do not invent affiliations, credentials or external co-authorship. For future manuscripts, use a CRediT-style contribution record where supportable (conceptualization; formal analysis; software; data curation; validation; visualization; writing; supervision) and distinguish primary survey collaboration credit from RLL development credit.

State explicitly that DESI, DES, Pantheon+SH0ES and Planck collaborations do not endorse RLL unless a verifiable statement exists. Credit the statistical/experimental work in their own citations, including calibration and data-release methods. Respect file licensing and the repository's unresolved [license reconciliation gate](../governance/RLL_LICENSE_AUTHORITY_RECONCILIATION_20260925.md); do not silently replace a license with whatever badge is visible.

**Data availability statement template:**
> Data sources are cited by their original collaboration release and immutable version (where available). This document supplies source locators but does not deposit third-party raw data or assert that all upstream covariance matrices are locally materialized. Derived artifacts will be released only with their reproducible input manifest, code, numerical methods, checksums and applicable licenses.

**Competing interests statement template:** Declare actual interests and funding transparently; absent information is `TOKEN_VAZIO_DECLARATION`, not “none” by assumption.

**Peer-review statement template:** “This manuscript has not yet undergone independent journal peer review” until the publisher’s status is verified.

## Change management and rollback

No historical paper, file or claim is deleted by this editorial proposal. Production equations and CI remain untouched. Correct an error with a successor that names its predecessor, exact file/commit and reason. Do not merge into `main`, generate a release, claim DOI publication of new results or update organizational permissions without specific approval.

A proposed minimum receipt is `μID|UTC|source/ref|parent/supersedes|kind|delta|evidence|gap|next|commit_sha`; never claim full evidence integrity from a Git blob hash alone. The [critical review](../research/RLL_DESI_DOVEKIE_CRITICAL_REVIEW_20261114.md) remains the evidence-bound mathematical source for this edition.

**R3:** F_ok = explicit scholarly publishing and visualization contract; F_gap = rendered mobile/print screenshot tests and CI are NOT_RUN; F_next = accessibility and scientific reviewer checks, then an approved merge. **FIAT LUX.**
