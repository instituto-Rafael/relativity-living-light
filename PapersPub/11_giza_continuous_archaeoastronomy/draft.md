# A Governed Continuous-Geometric Test Framework for Great Pyramid Shaft Archaeoastronomy

**Draft:** `v0.1 — 2026-09-06`  
**Author:** Rafael Melo Reis (∆RafaelVerboΩ)  
**Status:** `PREPRINT_DRAFT / claim_allowed=false / novelty_allowed=false`  
**Scope:** continuous geometry, archaeoastronomical model comparison, precession reconstruction and falsification protocol.

## Abstract

The internal shafts of the Great Pyramid of Khufu have generated long-running interpretations involving ventilation, ritual passageways, stellar targets and astronomical chronology. This paper does not assume any of those interpretations as established. Instead, it defines an evidence-gated framework that separates exact continuous mathematics, surveyed architecture, astronomical reconstruction, cultural interpretation and historical intention. The framework combines (i) exact trigonometric and toroidal geometry, (ii) shaft-direction models derived from instrumented or published surveys, (iii) precession and proper-motion reconstruction, and (iv) explicit model comparison against full-star controls and competing archaeological explanations. The strongest proposed hypothesis is that multiple shafts could jointly encode a narrow epoch through precession-dependent alignment. That proposition is retained as falsifiable but unvalidated. A valid test requires simultaneous convergence of multiple shaft residuals, propagation of survey and astrometric uncertainty, look-elsewhere correction, and explicit comparison with geometric-only and non-stellar alternatives. The method is designed to prevent numerical coincidence, later cultural texts, preprint status or geometric elegance from being promoted to archaeological proof.

## 1. Research question

Can the known geometry of Khufu's pyramid shafts support a reproducible, statistically distinct, culturally plausible and multi-shaft astronomical fit at a common ancient epoch, after precession and relevant stellar motion are modeled and competing explanations are tested?

This question is narrower than the assertion that the builders deliberately encoded a date. The latter is a historical-intention claim and requires additional archaeological evidence.

## 2. Epistemic partition

We use five non-interchangeable layers:

1. `EXACT_MATH`: identities and consequences of declared definitions;
2. `MEASURED_ARCHITECTURE`: shaft positions, directions, bends, sections and uncertainties from surveys/robotic exploration;
3. `ASTROMETRIC_RECONSTRUCTION`: computed historical sky directions using explicit models;
4. `ARCHAEOASTRONOMICAL_HYPOTHESIS`: a proposed relation between architecture and celestial targets;
5. `HISTORICAL_INTENT`: a claim about what builders meant or intended.

No upward promotion is automatic.

## 3. Continuous mathematical layer

The exact trigonometric constants

\[
\sin30^\circ=1/2,
\qquad
\cos30^\circ=\sqrt3/2,
\qquad
\sin45^\circ=\cos45^\circ=\sqrt2/2
\]

are used only where a declared geometric construction requires them.

A continuous torus may be represented by

\[
X(u,v)=((R+r\cos v)\cos u,(R+r\cos v)\sin u,r\sin v),
\qquad R>r>0.
\]

This embedding is mathematically standard and does not imply that the pyramid is a torus or that Egyptian architecture encoded toroidal topology.

For the session's declared phase family,

\[
u(t)=\frac{\pi^{3/2}}{\sqrt5}t,
\qquad
v(t)=\frac{\pi^{3/2}}2t,
\qquad
w(t)=\sqrt2\pi t,
\]

we have the exact derivative ratio

\[
\frac{v'}{u'}=\frac{\sqrt5}{2}.
\]

Likewise,

\[
\cos30^\circ\sqrt{\frac{\pi}{12}}=\frac{\sqrt\pi}{4}.
\]

These are retained as mathematical invariants only. Their presence in a model has no archaeological evidential weight unless independently connected to measured construction data.

## 4. Shaft evidence and prior literature

The literature on the shafts predates modern robotic exploration. Trimble [trimble1964] proposed an astronomical reading of the King's Chamber shafts, while Badawy [badawy1964] developed a stellar/religious interpretation. Later work expanded both the astronomical and critical literature.

Instrumented exploration is especially important because it constrains the physical object independently of symbolic interpretation. Richardson et al. [richardson2013] document the Djedi robot's exploration of the southern Queen's Chamber shaft. Miatello [miatello2020] uses the robot-survey record in a detailed geometric and ritual interpretation. Sakovich [sakovich2005] argues for a competing explanation and explicitly criticizes the sufficiency of several earlier theories.

Accordingly, this paper treats shaft geometry as an empirical input, not as a diagram inferred from a preferred celestial target.

## 5. Orientation and precession as a chronological instrument

Spence [spence2000] proposed that trends in Old Kingdom pyramid orientation could be explained by simultaneous transit of circumpolar stars and used precession to infer chronology. Rawlins and Pickering [rawlins2001] challenged part of the astronomical calculation and its implications; Spence [spence2001reply] replied. Belmonte [belmonte2001] independently assessed Old Kingdom pyramid orientation and questioned aspects of achievable precision and model choice.

These papers establish an important methodological point: precession can be used in a serious chronological model, but the result depends on the observational method, stellar pair, measurement precision and chronology assumptions. Therefore, “precession can date an alignment model” is not equivalent to “the shafts were built as an exact timestamp.”

For long historical intervals, the astronomical reconstruction should use a documented precession framework appropriate to millennial-scale extrapolation. Capitaine, Wallace and Chapront [capitaine2003] provide IAU-2000-consistent precession quantities. Vondrák, Capitaine and Wallace [vondrak2011] provide long-term precession expressions, with a published corrigendum that must be applied.

## 6. Competing shaft hypotheses

We define four primary hypotheses:

- `G-H1`: architectural geometry dominates shaft placement;
- `G-H2`: culturally relevant stellar targeting dominates;
- `G-H3`: geometry and astronomy were jointly optimized;
- `G-H4`: multiple shafts jointly encode a narrow epoch through precession-dependent alignment.

A fifth object, `G-H5`, is only a mathematical representation: four physical shafts can generate eight directed rays if each line is explicitly treated bidirectionally. This operation does not create four additional shafts.

Wall [wall2007] is particularly important as an adversarial source because it directly examines the star-alignment hypothesis for the shafts. The framework therefore requires a model to survive critical literature rather than merely cite supportive literature.

## 7. Geometric and astronomical state vectors

For shaft `i`, define a measured geometric state

\[
D_i=(x_i,y_i,z_i,A_i,h_i,w_i,L_i,\Sigma_i),
\]

where position, azimuth, elevation, aperture, path length and uncertainty are all explicit and versioned. A bent shaft must be represented as a polyline or piecewise-axis model; replacing it with one ideal straight line must be declared as an approximation.

For stellar source `j`, define

\[
S_j(t)=(\alpha_j(t),\delta_j(t),\mu_{\alpha,j},\mu_{\delta,j},\varpi_j,v_{r,j}).
\]

The astrometric state is propagated to epoch `t` and transformed to the local sky at Giza.

## 8. Residual and joint epoch statistic

For unit direction vectors,

\[
\epsilon_{ij}(t)=\arccos(\hat D_i\cdot\hat S_j(t)).
\]

For a declared target assignment, a joint statistic is

\[
\chi^2(t)=\sum_i\frac{\epsilon_i(t)^2}{\sigma_{shaft,i}^2+\sigma_{survey,i}^2+\sigma_{astro,i}^2}.
\]

A candidate epoch

\[
t^*=\arg\min_t\chi^2(t)
\]

is not by itself evidence of intent. The minimum must be compared against null models and the search space used to obtain it.

## 9. Look-elsewhere and control catalog

Selecting Orion, Sirius, Thuban or any culturally attractive star after inspecting the shaft directions creates a substantial selection effect. The principal control is therefore a magnitude-limited star catalog evaluated with the same fitting procedure.

The relevant question is not “can one famous star be made to fit?” but rather:

> Does a culturally constrained target set and a common epoch produce a multi-shaft fit substantially better than the distribution of best fits obtained from the allowed control catalog under the same uncertainty model?

This makes the hypothesis falsifiable.

## 10. Cultural evidence boundary

Texts and religious symbolism can constrain target plausibility, but chronological and contextual distance must be declared. Later Egyptian religious material cannot automatically prove Fourth-Dynasty construction intent. Cultural evidence is therefore used as a prior or interpretive constraint only when its temporal and contextual relation is independently defended.

## 11. Cross-hypothesis integration with RLL

This paper reuses several RLL mathematical governance units as methodology:

- scale-bearing ratios remain distinct even when numerically reducible (`T01`);
- repeated integers such as 42 or 121 carry no semantic identity by value alone (`T12`);
- spherical and toroidal geometry may be used as declared model spaces without transferring physical meaning (`T03`, `T06`, `H31` boundary);
- Theory Hashing binds source, transformation and claim history (`T14`);
- typed relations separate identity, analogy, correlation and causation (`T16`).

No cosmological RLL hypothesis is treated as evidence for Giza.

## 12. Anti-plagiarism procedure

The paper uses paraphrase plus citation as the default. Verbatim source language is unnecessary for the core argument. Bibliographic metadata is stored separately in Markdown, BibTeX and JATS-compatible XML. Every proposed new inference is tagged `DERIVED_HERE` or `USER_HYPOTHESIS`; every published model is identified by source.

The project does not claim originality for standard trigonometry, torus parameterization, precession equations, the star-alignment hypothesis, the simultaneous-transit hypothesis, robotic shaft observations or prior critical arguments.

## 13. Preprint and author correspondence

The package is structured so that it can later be exported to a preprint archive. An archive deposit must preserve `DRAFT/PREPRINT` state and must not be presented as peer review. In particular, viXra is treated as an e-print archive rather than a validation authority.

A separate machine-readable correspondence manifest records DOI/publisher routes for selected authors. Its default state is `NOT_SENT`. Contacting an author should ask a concrete scholarly question, cite the exact paper, and distinguish the RLL hypothesis from the author's own claims.

## 14. Falsification outcomes

`G-H4` is weakened or rejected if any of the following occurs:

1. independently measured shaft models produce mutually incompatible epoch minima;
2. the claimed epoch disappears under realistic shaft-bend uncertainty;
3. equally good or better fits are common in the control catalog;
4. the selected stars are not culturally defensible for the relevant period;
5. the fit depends on a chronology prior stronger than the astronomical information;
6. independent reproduction fails.

Conversely, a surviving common epoch would justify further investigation, not automatic historical-intent promotion.

## 15. Conclusion

The academically defensible result at this stage is methodological. The Great Pyramid shafts support a testable research program because their geometry can be measured, ancient sky positions can be reconstructed, and competing explanations can be compared. The specific claim that the builders encoded an exact precessional timestamp remains unproven.

The next evidential step is not another numerical analogy. It is a source-bound reconstruction of all four shaft geometries with uncertainty, followed by a full-star-control historical sky calculation and adversarial model comparison.

## Data and code availability

No new archaeological measurement dataset is introduced in this draft. The required measurement manifest remains open until authoritative shaft centerlines and uncertainties are source-bound. Reproduction requirements are specified in `reproducibility.md`.

## Competing interests

None declared in this research note.

## References

See `references.md`, `references.bib` and `metadata/references.jats.xml`.
