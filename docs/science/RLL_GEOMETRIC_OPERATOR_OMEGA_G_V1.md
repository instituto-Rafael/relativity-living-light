# RLL Geometric Operator Omega_G V1

State: `TYPED_MATHEMATICAL_CONSUMER`  
Scientific claim: `BLOCKED`

The canonical mathematical semantics live in `rafaelmeloreisnovo/Matem-tica-`:

- `operators/omega_g_geometric_operator.v1.yaml`
- `operators/OMEGA_G_GEOMETRIC_OPERATOR_V1.md`

The RLL repository consumes that mathematics but does not redefine it.

## Operator

[
\boxed{\Omega_G(X;\Theta,k,\Gamma)=\mathcal I\left[\Pi_\Gamma\circ T_\Theta\circ B^k(X)\right]}
]

The stages are:

1. (B^k): midpoint/centroid/barycentric subdivision;
2. (T_\Theta): rotation/scale/reflection/translation/affine/inversion;
3. (\Pi_\Gamma): projection or embedding in a declared target geometry;
4. (\mathcal I): invariant extraction.

The operator is project-defined. It is not claimed as a new universal mathematical primitive merely because the composition is compact.

## Family reduction

The RLL consumer recognizes the canonical families:

[
\Delta_d,\;Q_d,\;P_n,\;S^{d-1},\;\mathcal Q,\;T^d,\;G(V,E,W).
]

Examples include equilateral triangle/tetrahedron as simplex reductions, square/cube as hypercube reductions, circle/sphere as hypersphere reductions, and geodesic-sphere construction through subdivision plus radial projection.

## Median boundary

[
\mathrm{MEDIAN}_{geom}\ne\mathrm{MEDIAN}_{stat}\ne B.
]

This prevents the geometric median segment, statistical order median, and barycentric subdivision operator from sharing one untyped token.

## Scientific binding

No invariant enters a cosmological likelihood directly. The required bridge is

[
\boxed{BIND(I_j,O_k,mechanism,units,covariance,falsifier)}.
]

Until all required fields exist, the binding remains `TOKEN_VAZIO`.

This is particularly important for compressed observables such as H(z), BAO, (f\sigma_8), CMB shift parameters and SN summaries, because a propagation/geometric term may already be included upstream. The applicability matrix must prevent double counting.

## Omega naming boundary

This `Omega_G` is distinct from the existing operational Omega/Ω7 governance artifact. The former is mathematical geometry composition; the latter is evidence/governance architecture.

## Backend plan

The same canonical mathematical source should generate or validate:

- float64 reference;
- Python oracle;
- Q16.16;
- C freestanding;
- property tests;
- receipts.

The backend is not allowed to silently change the family semantics.

## Promotion rule

A shorter expression is valuable only when the original formulas remain reconstructible. Formula compression is therefore accepted as a representation improvement, not as evidence for new physics.

R3=<F_ok: canonical math source linked and RLL consumer boundary formalized; F_gap: generated backends, observable-effect applicability matrix and real likelihood binding; F_next: validate contract, implement generators, then bind one observable at a time under units/covariance/falsifier gates>.
