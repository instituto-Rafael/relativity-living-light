# Ω Mathematics Explorer V1 — YAML → Gates → Artifacts → Retrofeedback

**Date:** 2026-09-22  
**Author/proponent:** RAFAEL MELO REIS  
**State:** FORMAL_SHADOW / CANONICAL_CI_PENDING  
**claim_allowed:** false  
**publication_effect:** NONE

## Purpose

Create one bounded, reproducible mathematical execution surface that can:

1. read a declarative YAML contract;
2. evaluate exact/derived mathematical gates;
3. preserve hypotheses independently from theorems;
4. generate geometric candidate relations without promoting them automatically;
5. expose anomalies, contradictions and TOKEN_VAZIO states;
6. write reconstructible artifacts and checksums;
7. feed the next Ω cycle append-only.

The architecture follows the existing RLL workflow invariant:

INPUT
→ CONTRACT
→ VALIDATE
→ EXECUTE
→ RECEIPT
→ RESIDUAL
→ DECIDE
→ FEEDBACK.

## YAML boundary

The YAML declares:
- constants and their semantic roles;
- allowed operations;
- theorem/identity gates;
- hypotheses and falsifiers;
- relation edges;
- exploration families;
- anomaly policy;
- paradox boundaries;
- an operational ideal target;
- artifact contract.

It does not execute arbitrary expressions and does not contain the scientific algorithm.

The executable mathematics remains in:

tools/run_omega_math_explorer.py

The contract is:

data/contracts/omega_math_explorer.v1.yml

and is validated by:

schemas/omega_math_explorer.schema.json

## Initial mathematical spine

The first execution surface binds:

- pi as circumference / diameter;
- sqrt(2) as the unit-square diagonal ratio;
- sqrt(3)/2 as the equilateral height ratio and hexagonal apothem ratio;
- sqrt(5) and phi in the pentagonal family;
- Pythagoras;
- Bhaskara/discriminant line-circle classification;
- oriented area;
- affine area scaling;
- polygon triangulation;
- half-step n→2n angular doubling;
- gcd/lcm root-of-unity relations;
- the 5/6/7/8 840 grid;
- 22 distinct common-phase rays;
- 16 antipodal line orientations;
- torus/crown ratio;
- annular sweep fractions;
- quotient/remainder reconstruction;
- recursive polygon nesting;
- the sphere/torus Euler-characteristic boundary.

## Exploration, not automatic theorem generation

For polygon families n in the YAML, the explorer computes:

- central angle;
- side/circumradius ratio;
- apothem/circumradius ratio;
- normalized area;
- annulus fraction;
- chord-distance spectrum;
- step-2 diagonal/side ratio where defined;
- pairwise gcd/lcm and microangles;
- shared root counts;
- mixed nested radial scales;
- cross-family equal-distance candidates;
- constant matches;
- repeated scale products.

Every emergent relation is emitted as a candidate/known match record.

No candidate can become PROVADO merely because it appears numerically.

## Semantics and paradox control

The contract explicitly separates:

OBJECT != REPRESENTATION
EXACT != APPROXIMATE
METRIC != ORIENTATION
REAL_BRANCH != COMPLEX_BRANCH
FINITE != LIMIT
GEOMETRIC_IDENTITY != PHYSICAL_MECHANISM
SAME_NUMERIC_ORDER != SAME_SEMANTICS

Examples:

- same area does not imply same shape;
- the two occurrences of order 840 do not imply identical semantics;
- zero positional coefficient is not TOKEN_VAZIO;
- mathematical recursive infinity is not a physical-infinity observation.

## Operational ideal

The YAML defines an objective J with penalties for:

- failed gates;
- unresolved contradictions;
- untracked lossy operations;
- TOKEN_VAZIO without next gate;
- anomalies.

J=0 is only the ideal state of this bounded execution contract.

It does not mean mathematical completeness, universal truth or physical confirmation.

## Artifacts

A successful bounded run emits:

- resolved_manifest.json
- constants.json
- gate_results.json
- hypothesis_results.json
- exploration.json
- candidates.csv
- anomalies.json
- semantic_graph.json
- report.md
- receipt.json
- CHECKSUMS.sha256

The GitHub workflow also appends:

- junit.xml
- Python version;
- pip freeze;
- workflow-level checksums;
- explicit claim boundary.

## Discovery examples expected from the seed contract

The explorer should recover, among other relations:

- n=4 side/R = sqrt(2);
- n=6 apothem/R = sqrt(3)/2;
- n=5 step-2 diagonal/side = phi;
- lcm(5,6,7,8)=840;
- 22 distinct common-phase rays for 5/6/7/8;
- 16 full-line orientations modulo pi;
- permutation invariance of nested-scale products.

If a different-multiset scale collision appears at the declared numerical tolerance,
it is emitted as CANDIDATE_NONTRIVIAL_SCALE_IDENTITY and is not silently treated as exact.

## Reproduction

Local:

python tools/run_omega_math_explorer.py --strict
pytest -q tests/test_omega_math_explorer.py

Canonical GitHub execution:

.github/workflows/omega-math-explorer.yml

## Rollback

All outputs are derived views. The reconstructible authorities are:

1. YAML contract;
2. schema;
3. tested runner;
4. commit SHA;
5. receipt/checksums.

Rollback is Git history plus the prior contract version. Negative results and candidate relations remain append-only evidence.

## R3

F_ok:
- declarative multidimensional mathematics contract exists;
- algorithm is externalized and tested;
- artifact/receipt format is explicit;
- candidate discovery is separated from proof;
- semantic, anomaly, paradox and ideal-target layers are typed.

F_gap:
- canonical workflow execution is pending at document creation time;
- explorer does not yet planarize arbitrary chord graphs;
- symbolic exact-field recognition of numerical candidates is not yet implemented;
- automatic proof synthesis is forbidden/not implemented.

F_next:
- consume the canonical CI artifact;
- add exact symbolic candidate recognizers;
- add planarization and cycle/orbit enumeration;
- add recursive simplex/polygon embedding graph;
- route every new candidate through proof/falsifier/prior-art gates.


## First canonical run and Ω feedback

Canonical run:

- workflow run: 35693370128
- job: omega-math-shadow
- conclusion: success
- artifact id: 10679383755
- artifact digest: sha256:1a85dde723f058ce6e3a8379a7cd26c982a0a6cbef4808e0a69752861a864daa
- artifact size: 27912 bytes
- focused tests: 3 passed
- decision: PASS_FORMAL_SHADOW
- failed gates: 0
- candidate relations: 146
- anomalies: 9
- TOKEN_VAZIO hypotheses: H-840-SEMANTIC, H-FRACTAL-DIMENSION
- operational objective: J=9, target 0

The 9 scale anomalies were then inspected rather than suppressed.

All nine reduce to the exact radial-scale rewrite:

cos(pi/3) = cos(pi/4)^2 = 1/2.

Therefore one n=3 inradius contraction has the same radial factor as two consecutive n=4 contractions:

R -> R cos(pi/3) = R/2

and

R -> R cos(pi/4) -> R cos^2(pi/4) = R/2.

The nine observed collisions are instances of this single rewrite combined with other commuting scale factors.

This result was fed back into the next contract revision as:

DERIVED_REWRITE_IDENTITY_COS60_EQ_COS45_SQUARED.

The successor test requires these collisions to stop being classified as anomalies and requires the bounded ideal objective to reach J=0 if no other anomaly is present.

This is the intended Ω cycle:

candidate/anomaly
-> inspect
-> derive/falsify
-> encode exact gate
-> rerun
-> preserve both receipts.
