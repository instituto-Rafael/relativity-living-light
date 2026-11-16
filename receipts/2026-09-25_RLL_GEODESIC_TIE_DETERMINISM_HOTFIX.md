# μWRITE — deterministic geodesic tie hotfix — 2026-09-25

μID: MU-RLL-GEODESIC-TIE-DETERMINISM-20260925  
parent: PR#987 merged into rll/lab  
kind: INHERITED_TEST_FAILURE+NUMERICAL_DETERMINISM_HOTFIX  
claim_allowed: false

## Observed failure

PR #987 inherited the same Python-suite failure already observed on PR #985:

```
tests/test_unified_shape_toroidal_transport.py::test_144_cells_project_to_42_vertex_lattice_and_measure_stability_concentration
assert 22 == 21
```

Provider evidence:
- PR #985 Python run 36090721954: 1 failed / 1986 passed / 42 subtests.
- PR #987 Python run 36107227849: 1 failed / 1992 passed / 42 subtests.
- both failures are the same occupied-vertex assertion.
- the failing test and projection implementation were unchanged by PR #987.

The committed reference fixture records 21 occupied vertices, 144 total cells and 126 stable cells.

## Root cause hypothesis and bounded repair

Symmetric source states can be exactly/effectively equidistant from multiple f=2 icosphere vertices. Raw `acos` distances can differ by a few ulps across runners/libm implementations. Exact float ordering can therefore split a canonical tie into two bins.

Repair:
- treat geodesic distances within `max(1,|S|)*1e-12` as the same geometric tie;
- resolve equal-distance ties by lower vertex index;
- apply the same policy in both nearest-vertex implementations.

Changed files:
- `rx/unified_shape_toroidal_transport.py`
- `rx/toroidal_geodesic_stability.py`

Commits:
- `5c887c6fa27bf9065dfbe30fc8686b74792ec0ff`
- `568a0ee28e6899283b45039fe963cdfbe807913b`

## Boundary

This changes only deterministic mesh bin assignment on numerical ties. It does not alter:
- source torus states;
- HETE stability calculation;
- physical parameters;
- cosmological likelihoods;
- claim state.

F_gap: exact-head provider CI after hotfix.  
F_next: run full Python suite and all topology/governance gates; merge only if terminal evidence is clean.  
rollback: revert the two hotfix commits; preserve the inherited-failure receipts.
