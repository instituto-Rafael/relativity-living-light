# RLL Multilayer Circle–Polygon Geometry V1 — Local Validation Report

**Date:** 2026-09-22  
**Execution state:** `LOCAL_EXECUTION_PASS`  
**Repository provider CI:** `NOT_RUN`  
**Physical/cosmological binding:** `TOKEN_VAZIO_EVIDENCE`

## Summary

- Scenarios: **20**
- Tests: **120**
- PASS: **120**
- FAIL: **0**

## Scenario results

| Scenario | Passed | Total | State |
|---|---:|---:|---|
| S01 regular polygon | 40 | 40 | PASS |
| S02 chord classes | 16 | 16 | PASS |
| S03 equilateral triangle | 5 | 5 | PASS |
| S04 triangle/circle area ratios | 2 | 2 | PASS |
| S05 hexagon/six triangles | 2 | 2 | PASS |
| S06 concentric layers | 9 | 9 | PASS |
| S07 radial projection | 2 | 2 | PASS |
| S08 homothety | 2 | 2 | PASS |
| S09 rotation | 2 | 2 | PASS |
| S10 reflection | 3 | 3 | PASS |
| S11 circle inversion | 2 | 2 | PASS |
| S12 polygon→circle limit | 3 | 3 | PASS |
| S13 K8 planar no-loss | 6 | 6 | PASS |
| S14 rotated triangle overlays | 2 | 2 | PASS |
| S15 Snell refraction formula | 2 | 2 | PASS |
| S16 octagonal prism/K16 | 6 | 6 | PASS |
| S17 spherical shell | 3 | 3 | PASS |
| S18 multilayer complete graph | 2 | 2 | PASS |
| S19 index family | 5 | 5 | PASS |
| S20 D8 orbit-stabilizer | 6 | 6 | PASS |

## Key reproduced invariants

- K8: 28 segments; 49 internal intersections; concurrency 40/8/1; planarization V=57,E=136,F=81; 56 triangular + 24 quadrilateral elementary bounded faces; cycle rank 80.
- Equilateral triangle: R=2r plus exact height/area and in-/circumcircle ratios.
- Six center-based equilateral triangles tile a regular hexagon exactly.
- Six equilateral-triangle rotations by 60° yield 6 distinct angular vertices; by 30° yield 12.
- Octagonal prism: 16 vertices; K16 has 120 edges = 56 intralayer + 64 interlayer.
- Spherical-shell checks reproduce radial projection, chord/arc relation, and octant spherical-triangle area.
- Snell checks are classical-formula tests only.

## Evidence boundary

PASS means the declared mathematical/numerical relations were reproduced in the local execution environment using the validator committed with this package. It does not establish a new physical law, cosmological mechanism, or universal interpretation.

## Hashes

- spec SHA-256: `e356d4e983fc474120362ab7e4f5979cc3251b98097fe0db514bdcb107a82aaa`
- validator SHA-256: `9dd4259f7ee9eada79e90e721ff25d80171250219c09e15d3003c2f9658caa5b`
- local result SHA-256: `9d5c7ac4a3e39b7dadd2a2e4e365a1d0de70e2303b0249491ed1b087c3f2c0f1`

## R3

F_ok: 20 scenarios / 120 tests PASS.  
F_gap: provider CI NOT_RUN; exhaustive simple-cycle/orbit enumeration for larger generated families remains open.  
F_next: run CI, then stream generated forms into typed weight/orbit ledgers.
