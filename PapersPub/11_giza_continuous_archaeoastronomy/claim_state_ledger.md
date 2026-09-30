# Claim State Ledger — Giza Continuous Archaeoastronomy

**Version:** `v0.1`  
**Date:** `2026-09-06`  
**Global:** `claim_allowed=false / novelty_allowed=false / publication_allowed=false`

| Claim ID | Statement | Type | Evidence state | Main adversary/falsifier | Promotion gate |
|---|---|---|---|---|---|
| `C-EXACT-001` | `sin(30°)=1/2`, `cos(30°)=sqrt(3)/2`, `sin(45°)=cos(45°)=sqrt(2)/2` | exact mathematics | `PASS_EXACT` | direct algebraic/trigonometric verification | none for identity |
| `C-EXACT-002` | `cos(30°)*sqrt(pi/12)=sqrt(pi)/4` | exact mathematics | `PASS_EXACT` | symbolic simplification | none for identity |
| `C-EXACT-003` | for declared phases, `v'/u'=sqrt(5)/2` | derived exact mathematics | `PASS_EXACT` | differentiate the declared functions | preserve function definitions |
| `C-MODEL-001` | standard ring-torus embedding is a valid continuous model space | mathematical model | `PASS_STANDARD_MODEL` | direct differential-geometry definition | no physical transfer |
| `C-GIZA-001` | four physical chamber shafts are the architectural objects under study | archaeological object statement | `SUPPORTED_GENERAL` | authoritative survey reconciliation | source-bound centerlines |
| `C-GIZA-002` | eight rays may be produced from four axes by explicit bidirectional extension | declared model | `PASS_BY_DEFINITION` | any text treating them as eight physical shafts invalidates the model use | preserve `4 physical != 8 projected` |
| `C-GIZA-H1` | internal geometric constraints dominate shaft placement | hypothesis | `TOKEN_VAZIO_EVIDENCE` | measured paths resist declared geometry within uncertainty | full shaft survey fit |
| `C-GIZA-H2` | culturally relevant stellar targets dominate shaft placement | hypothesis | `TOKEN_VAZIO_EVIDENCE` | magnitude-limited control produces non-distinct matches | full-star control + cultural prior |
| `C-GIZA-H3` | geometry and astronomy were jointly optimized | hypothesis | `TOKEN_VAZIO_EVIDENCE` | no shared parameter region satisfies both constraint families | joint model comparison |
| `C-GIZA-H4` | multiple shafts jointly encode a narrow epoch through precession | strong hypothesis | `TOKEN_VAZIO_EVIDENCE` | incompatible shaft epoch minima, look-elsewhere failure, or chronology-prior domination | multi-shaft historical sky reconstruction + null distribution + independent replication |
| `C-GIZA-INTENT` | Khufu's builders intended an exact precessional timestamp | historical-intent claim | `CLAIM_BLOCKED` | absence of independent contemporaneous evidence; viable competing functional models | astronomical fit plus independent archaeological/cultural evidence |
| `C-42-BRIDGE` | numerical `42` in RLL/icosphere/Giza-like constructions identifies one common object | semantic identity claim | `REJECTED_AS_STATED` | typed relation calculus: same integer does not transfer semantics | explicit structure-preserving map required |
| `C-TORUS-PHYSICAL` | torus mathematics proves toroidal Egyptian architecture/cosmology | physical/historical claim | `REJECTED_AS_STATED` | model-space use is not object identity | independent physical/archaeological evidence required |

## Mandatory adversarial literature

Any future text that cites `Spence 2000` for chronology must also route to at least one direct/independent critical source among `Rawlins & Pickering 2001`, `Belmonte 2001`, and the relevant shaft critique literature. Any text that cites stellar-shaft support must route to `Wall 2007` and `Sakovich 2005/2006` as competing evaluations.

## Cross-hypothesis firewall

RLL cosmology, DESI, toroidal plasma, icosphere and modular-number hypotheses can contribute **methods**, validators or counterexamples. They do not provide archaeological evidence for Giza unless a source-bound, domain-valid bridge is separately demonstrated.

```text
same_formula != same_mechanism
same_number != same_object
same_embedding != same_physics
same_hypothesis_family != shared_evidence
```
