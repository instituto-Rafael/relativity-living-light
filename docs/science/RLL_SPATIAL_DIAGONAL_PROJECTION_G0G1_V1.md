# RLL G0/G1 — 3D diagonals, projected geometry and ellipse-plane gates (V1)

Date: 2026-11-18. State: SOURCE_CANDIDATE / LOCAL_SYNTHETIC_TEST_SCOPED / claim_allowed=false.

## Authority and boundaries

Drive global START HERE Ω V2.2 -> RLL local START HERE Ω V2.1 -> RLL code.
Mathematical producer (reference only, never copied): `rafaelmeloreisnovo/Matem-tica-`, especially
`docs/formal/GEODESIC_NUMERAL_RELATIONS_V1.md` and `docs/research/2026-10-26_CROQUI_RAZOES_INVARIANTES_PROJECOES_V2.md`.
Consumer: RLL `rx/spatial_diagonal_geometry.py`; no changes to H(z), priors, likelihood, DESI data, or cosmological interpretation.

### Spatial diagnostics

- Unit Cartesian projection: `u=(cos δ cos α, cos δ sin α, sin δ)`. **No distance estimate from angles alone**; unknown line-of-sight distance remains `TOKEN_VAZIO`.
- Local east/north/LOS basis from RA/Dec; `D3²=E²+N²+LOS²`, `D2²=E²+N²`; all vector components must share units and reference frame/epoch.
- Square, cube and n-hypercube length indices `s√2`, `s√3`, `s√n` require orthogonal Euclidean axes. A 60° hexagonal basis has `d²=a²+ab+b²`, **not** the orthogonal diagonal rule.
- Four **spatial** positions produce a dimensionless scalar triple-product index; nonzero exact value implies not coplanar. Three points are always coplanar. Near-zero observational results require uncertainty/covariance before classification.
- An ellipse `center+a cos θ U+b sin θ V` can be embedded in any orthonormal 3D plane; orientation may change between epochs. This is kinematic geometry only. Comparing vertices between epochs does not identify a material trajectory.
- No raw coordinate Euclidean curvature is allowed to be carried into G2/G3 spacetime without an explicit tetrad/metric adapter.

### Typed gaps

- Sky-only data / parallax missing / radial distance unknown => `TOKEN_VAZIO_LINE_OF_SIGHT_DISTANCE`.
- Degenerate 3D chords => `TOKEN_VAZIO_DEGENERATE_CHORD`.
- Full Gaia astrometric covariance, observation epoch, perspective acceleration, instrument/observer motion, stellar/light-motion decomposition, gravitational lensing, GW strain, and physical dynamics => `NOT_TESTED`.
- All outputs are `claim_allowed=false`.

### Falsifiers / rollback

9 synthetic `unittest` methods in `tests/test_spatial_diagonal_geometry.py`; test XYZ, angle poles, NaN/Inf, zero/missing depth, 3D/projection Pythagoras, signed tetrahedron index ±1, exact coplanar 0, hex basis √3, tilted ellipse and scale.
Review-only child of `974f0cb5f7c88ed6a44389fb48fb4267645d2421`. No merge, no overwrite of main; rollback by leaving branch isolated, preserving predecessor.

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`; `claim_allowed=false`.
