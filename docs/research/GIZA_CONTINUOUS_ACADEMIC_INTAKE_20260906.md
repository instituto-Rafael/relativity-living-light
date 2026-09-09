# RLL — Giza Continuous Academic Intake — 2026-09-06

**State:** `GOVERNED_ACADEMIC_INTAKE / APPEND_ONLY / claim_allowed=false / novelty_allowed=false`  
**Owner:** `research-governance`  
**Target paper package:** `PapersPub/11_giza_continuous_archaeoastronomy/`  
**Preprint route:** `PREPRINT_READY_ONLY`; no external submission performed.

## 1. Boundary

This intake absorbs the continuous geometric layer developed in the 2026-09-06 session into RLL without converting numerical resemblance into archaeological or physical evidence.

Invariants:

```text
exact_identity != historical_intent
measured_shaft_geometry != stellar_target
stellar_target != precessional_timestamp
precessional_fit != archaeological_date
preprint != peer_review
citation != endorsement
hash != proof
```

The existing RLL hypothesis and publication governance remains authoritative. This file does not replace `docs/cosmology/DESI_50_HYPOTHESIS_INTAKE_20260815.md`, `knowledge_ecosystem/publication_doi_pipeline.md`, or any existing PapersPub contract.

## 2. Continuous mathematical kernel admitted as exact mathematics

The following are exact identities or explicit definitions and require no archaeological interpretation:

\[
\sin 30^\circ=\frac12,
\qquad
\cos 30^\circ=\frac{\sqrt3}{2},
\qquad
\sin45^\circ=\cos45^\circ=\frac{\sqrt2}{2}.
\]

Define continuous phases

\[
u(t)=\frac{\pi^{3/2}}{\sqrt5}t,
\qquad
v(t)=\frac{\pi^{3/2}}2t,
\qquad
w(t)=\sqrt2\,\pi t.
\]

Then

\[
\frac{v'(t)}{u'(t)}=\frac{\sqrt5}{2}
\]

wherever the derivatives are taken, and

\[
\cos30^\circ\sqrt{\frac{\pi}{12}}=\frac{\sqrt\pi}{4}.
\]

These statements are tagged `EXACT_MATH`. They are not evidence that Khufu's builders selected any of these constants.

For a ring torus with `R>r>0`, RLL already uses the standard continuous embedding

\[
X(u,v)=((R+r\cos v)\cos u,(R+r\cos v)\sin u,r\sin v).
\]

This intake reuses that object only as a declared mathematical model. It does not infer a toroidal monument, toroidal cosmology, or toroidal Egyptian design.

## 3. Archaeological/astronomical hypotheses admitted for testing

| ID | Hypothesis | State | Minimum falsifier |
|---|---|---|---|
| `G-H1-GEOMETRIC-GRID` | Shaft geometry is primarily constrained by the internal geometric grid of the pyramid. | `HYPOTHESIS` | surveyed centerlines cannot be reconstructed from the declared geometric constraints within measurement uncertainty |
| `G-H2-STELLAR-TARGET` | One or more shaft terminal directions intentionally targeted culturally relevant stars/regions of sky. | `HYPOTHESIS` | full-star control shows target matches are non-distinct after look-elsewhere correction and cultural constraints |
| `G-H3-JOINT-GEOMETRY-ASTRONOMY` | Geometry and stellar targeting were jointly satisfied. | `HYPOTHESIS` | no common parameter set fits both architectural geometry and independent astronomical target constraints |
| `G-H4-PRECESSIONAL-TIMESTAMP` | Multiple shafts jointly encode a narrow epoch through precession-dependent alignments. | `HYPOTHESIS_STRONG / TOKEN_VAZIO_EVIDENCE` | independently surveyed shaft axes yield incompatible best-fit epochs or no excess fit over bright-star controls |
| `G-H5-EIGHT-RAY-PROJECTION` | Four physical shafts may be represented by eight mathematical rays under a declared bidirectional projection. | `MODEL_ONLY` | projection is used as if it created four additional physical shafts |

No hypothesis above is promoted by this intake.

## 4. Academic evidence ladder

### A. Physical survey / shaft evidence

- Richardson et al. (2013), *Journal of Field Robotics*, DOI `10.1002/rob.21451`: direct robotic exploration of the southern Queen's Chamber shaft; strongest source in this intake for instrumented shaft observation.
- Miatello (2020 issue; online 2021), *Journal of the American Research Center in Egypt* 56, DOI `10.5913/jarce.56.2020.a008`: geometric/interpretive analysis using robot-survey evidence; useful but interpretive claims remain contestable.
- Sakovich (2005/2006), *JARCE* 42, pp. 1–12, JSTOR stable `27651795`: competing explanation and explicit critique of prior shaft theories.
- Trimble (1964), *Mitteilungen des Instituts für Orientforschung* 10, pp. 183–187: foundational astronomical shaft argument.
- Badawy (1964), *Mitteilungen des Instituts für Orientforschung* 10, pp. 189–206: early stellar/religious interpretation.

### B. Orientation / chronology / precession

- Spence (2000), *Nature* 408, 320–324, DOI `10.1038/35042510`: explicit simultaneous-transit/precession chronology model.
- Rawlins & Pickering (2001), *Nature* 412, 699, DOI `10.1038/35089138`: direct mathematical critique and competing stellar-pair implications.
- Spence (2001), *Nature* 412, 699–700, DOI `10.1038/35089140`: author reply; preserves the controversy as a live model dispute, not a settled fact.
- Belmonte (2001), *Journal for the History of Astronomy* 32, S1–S20, DOI `10.1177/002182860103202601`: independent critique of Old Kingdom orientation models and achievable precision.
- Wall (2007), *Journal for the History of Astronomy* 38(2), 199–206, DOI `10.1177/002182860703800204`: explicit test of the star-alignment hypothesis for the shafts.

### C. Astrometric/precession machinery

- Capitaine, Wallace & Chapront (2003), *Astronomy & Astrophysics* 412, 567–586, DOI `10.1051/0004-6361:20031539`: IAU-2000-consistent precession quantities; appropriate for modern precession methodology near the standard epoch.
- Vondrák, Capitaine & Wallace (2011), *Astronomy & Astrophysics* 534, A22, DOI `10.1051/0004-6361/201117274`, plus corrigendum DOI `10.1051/0004-6361/201117274e`: long-term precession expressions suitable for millennial-scale reconstruction; the corrigendum must be applied.

### D. Preprints / secondary routes

- Magli (2003), arXiv `physics/0307100`: useful adversarial/re-analysis input, but retained as `PREPRINT`, not peer-reviewed validation.
- viXra material, when later ingested, must be labeled `PREPRINT_UNREFEREED` unless an independent peer-reviewed publication of the same work is source-bound.

## 5. Cross-hypothesis routing into existing RLL

The current RLL 48-unit program already contains mathematical units that are relevant as *methods*, not as evidence for Giza:

| RLL unit | Relation to this intake | Allowed transfer |
|---|---|---|
| `T01 scale-preserving rational geometry` | shaft ratios and cubit-scale states must retain scale, not only simplified fractions | methodological |
| `T02 integrated geometry of 14` | shares exact 30/45/60-degree geometry | exact-math reuse only; no historical transfer |
| `T03 planar→sphere renormalization` | can test spherical/geodesic projections of declared geometric models | mathematical model only |
| `T06 multiscale icospheres` | provides a controlled spherical triangulation tool | computational geometry only |
| `T12 typed repeated numbers 7/42/420` | directly guards against number-equality inflation (`42`, `121`, `14`, etc.) | epistemic control |
| `T14 Theory Hashing` | can bind every hypothesis, source and transformation to immutable provenance | provenance only |
| `T16 typed relation calculus` | classifies identity, correlation, causation, inverse and analogy | epistemic control |
| `H31 perturbed torus focal center` | uses torus geometry but has no demonstrated archaeological relation | `NO_PHYSICAL_TRANSFER` |
| DESI/cosmology hypotheses | domain-distinct | `NO_EVIDENCE_TRANSFER` |

Thus `same constant`, `same torus`, or `same number` never creates an evidence edge across domains.

## 6. Required computational experiment for G-H4

For each surveyed shaft polyline or defensible terminal axis, define

\[
D_i=(x_i,y_i,z_i,A_i,h_i,w_i,L_i,\Sigma_i).
\]

For each candidate celestial source `j`, propagate a catalog state

\[
S_j(t)=(\alpha_j(t),\delta_j(t),\mu_{\alpha,j},\mu_{\delta,j},\varpi_j,v_{r,j})
\]

through a documented precession/proper-motion model and transform to Giza-local altitude/azimuth.

Angular residual:

\[
\epsilon_{ij}(t)=\arccos(\hat D_i\cdot\hat S_j(t)).
\]

Joint epoch statistic:

\[
\chi^2(t)=\sum_i\frac{\epsilon_i(t)^2}{\sigma_{shaft,i}^2+\sigma_{survey,i}^2+\sigma_{astro,i}^2}.
\]

Required controls:

1. full or magnitude-limited bright-star control, not only Orion/Sirius/Thuban;
2. multiple-shaft convergence, not a single best match;
3. look-elsewhere correction;
4. sensitivity to shaft bends and alternate terminal-axis definitions;
5. chronology prior reported separately from astronomical fit;
6. independent replication;
7. no use of later Egyptian texts as automatic proof of Fourth-Dynasty intent.

A common epoch is evidence only if it survives these controls and the measurement uncertainties.

## 7. Anti-plagiarism and attribution contract

Every external claim in the paper package must be either:

- paraphrased with an adjacent citation key;
- quoted only when necessary and within copyright limits;
- marked `DERIVED_HERE` if it is an original algebraic consequence of declared definitions;
- marked `USER_HYPOTHESIS` for hypotheses originating in the session;
- marked `SOURCE_HYPOTHESIS` when reproducing a published author's hypothesis;
- marked `TOKEN_VAZIO_ORIGIN` if origin cannot be resolved.

No source prose is imported as project prose. Bibliographic metadata may be reproduced as factual citation data. DOI does not imply endorsement and citation count does not imply correctness.

## 8. Author-contact boundary

Machine-readable author/correspondence metadata may be stored when exposed by the publisher or persistent identifier. No automated email is sent by this intake.

```text
metadata present != permission to contact
corresponding-author route != endorsement
message drafted != message sent
```

The package includes an XML correspondence manifest with `status=NOT_SENT` and DOI/publisher routes. Direct outreach requires a separately reviewed message tied to a concrete scholarly question.

## 9. Preprint / viXra boundary

A preprint-ready package may later be exported to arXiv, viXra, Zenodo or another archive only with explicit version, authorship, reference list, claim ledger and provenance manifest. External upload/publication is not performed here.

viXra is treated as an e-print repository, not a peer-review gate. Any viXra item used as a source must be paired with independent verification or remain `PREPRINT_UNREFEREED`.

## 10. Closure

```text
F_ok:
- continuous mathematics preserved without discretization;
- RLL cross-hypothesis routes identified;
- primary measurement, archaeoastronomy, critique and precession literature separated;
- anti-plagiarism and author-contact boundaries defined.

F_gap:
- authoritative four-shaft 3D centerline dataset with uncertainty remains incomplete;
- full historical star-catalog reconstruction not yet executed;
- common-epoch fit and null distribution not yet computed;
- exact viXra object(s) intended by the user remain TOKEN_VAZIO until source-bound.

F_next:
shaft survey binding -> astrometric reconstruction -> full-star control -> joint epoch fit -> adversarial review -> independent replication -> claim gate.
```
