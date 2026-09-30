# Receipt — Full 251 Formula Import + Cosmology Geometry Crosswalk V1

Date: 2026-09-21  
Author: RAFAEL MELO REIS  
State: \`MATERIALIZED / FULL_IMPORT_PASS / EXECUTION_PARTIAL\`

## Provenance correction

Before this delta, RLL referenced the upstream range \`MF-0001..MF-0251\` but did not store every MF record verbatim in one RLL machine-readable registry.

This delta closes that gap.

## Full import

Artifact:

\`data/governance/RLL_SESSION_FORMULA_REGISTRY_MF0001_MF0251_V1.json\`

Observed import:

\`\`\`text
count=251
missing=[]
duplicates=[]
complete=true
\`\`\`

Commit:

\`2ee973e22233e4a9889f1979c8ad90fc33d04846\`

## Typed test matrix

Artifact:

\`data/governance/RLL_FORMULA_TEST_MATRIX_MF0001_MF0251_V1.json\`

Commit:

\`477d85b365ed98d7d40d2bbe55d30f3ef495a655\`

Routes:

\`\`\`text
144 DETERMINISTIC_NUMERIC_OR_SYMBOLIC
16  STRUCTURAL_ASSERTION
33  HYPOTHESIS_OR_MODEL_FALSIFIER
11  BOUNDARY_GUARD
47  PROVENANCE_CONTEXT_ONLY
total=251
\`\`\`

Cosmology routes:

\`\`\`text
130 GEOMETRY_DIAGNOSTIC_CANDIDATE
44  NEGATIVE_CONTROL_NO_COSMOLOGY
5   DOMAIN_SEPARATION_CONTROL
72  NO_DIRECT_COSMOLOGY_BINDING
total=251
\`\`\`

## Geometry expansion

- \`docs/invariants/circle_triangle_cone_annulus_v1.md\`
  commit \`5a7ff64a7acc7984527dcdc5593ecf74f09660a9\`
- \`docs/cosmology/RLL_FORMULA_GEOMETRY_CROSSWALK_DESI_PANTHEON_LCDM_RLL_V1.md\`
  commit \`6090a9519240d1c19f5ac3e0c1ab267657f2d33a\`
- \`data/contracts/rll_formula_cosmology_geometry_crosswalk.v1.json\`
  commit \`885ce66c27624fe428dac2459b687801b8651dd7\`

The extension distinguishes:
- Euclidean cone/frustum/annulus geometry;
- FLRW distance geometry;
- relativistic light-cone geometry.

No identity between these layers is assumed.

## Executable gate

- \`tools/test_formula_cosmology_geometry_crosswalk.py\`
  commit \`6a4fcd712f9d9e6db2e88b209b4c2485d71f4d92\`
- \`tests/test_formula_cosmology_geometry_crosswalk.py\`
  commit \`f7bbdd1cd03879617fdd2ff538324108b41c2ad4\`

The gate checks:
1. 251/251 coverage and routing;
2. DESI DR2 13-point covariance geometry;
3. six anisotropic \(D_M/D_H\) AP ratios;
4. circle/triangle/cone/annulus exact identities;
5. RLL \(\Omega_{s0}=0\) null geometry against flat LCDM.

## Execution boundary

This does **not** mean 251/251 mathematical identities have individually passed.

Current state:

- full storage coverage: \`PASS\`;
- full routing coverage: \`PASS\`;
- existing 10 GWI invariant families: local execution previously recorded;
- new 251 crosswalk test CI: \`PENDING\` at receipt time;
- 144 individual deterministic MF tests: \`PENDING\`;
- 16 individual structural MF tests: \`PENDING\`;
- 33 hypothesis falsifiers: \`PENDING\`;
- Pantheon+ full-covariance model comparison: delegated to existing G4 route and runtime readiness;
- physical interpretation: \`BLOCKED\`.

## μWRITE

\`\`\`text
μID=RLL-MF251-COSMO-GEOMETRY-20260921-V1
source/ref=Matem-tica- MF-0001..MF-0251 + DESI DR2 BAO + Pantheon+ routes + LCDM/RLL model family
parent=RLL-GEOMETRIC-WEAVE-INVARIANTS-20260921-V1
kind=full-formula-import-and-cosmology-crosswalk
Δsummary=materialize all 251 MF records; type all test routes; add DESI/Pantheon/LCDM/RLL geometry crosswalk; add circle-triangle-cone-annulus hierarchy; add executable aggregate gate
evidence=FULL_IMPORT_PASS + EXECUTION_PARTIAL
gap=144 deterministic individual tests + 16 structural individual tests + 33 hypothesis falsifiers + Pantheon runtime + prior-art + independent reproduction
next=execute formula-level registry in batches and bind outputs to DESI/Pantheon/LCDM/RLL only after dimensional/domain gates
rollback=revert this delta commits only; preserve prior RLL invariant atlas and upstream Matem-tica- ledger
\`\`\`

## R3

F_ok: all 251 expressions are physically materialized inside RLL with no missing/duplicate IDs and each has a typed test/cosmology route.

F_gap: coverage is complete, but individual execution is not; no claim should say 251/251 PASS yet.

F_next: execute the 144 deterministic expressions and 16 structural expressions in MF-ID batches, then feed only the 130 geometry-qualified candidates into covariance-aware DESI/Pantheon+/LCDM/RLL diagnostics.
