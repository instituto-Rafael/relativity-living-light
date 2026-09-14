# Appendix B — Hexagonal Matrix Projection, Toroidal Attachment, Spherical Enclosure and Poincaré Section

**Status:** `appendix_v0.1 | analysis_run | claim_allowed=false`  
**Author:** Rafael Melo Reis (∆RafaelVerboΩ)  
**Scope:** exact Euclidean geometry, declared computational conventions and falsifiable model boundaries

> **Boundary.** This appendix formalizes a geometric projection layer for the arrays introduced in Section 5. It does not establish a physical vortex, a Venturi mechanism, a toroidal cosmology, a geodesic spacetime or a new result about the Poincaré conjecture.

## B.1 Motivation

The arrays

\[
A\in\mathcal S^{8\times5},
\qquad
B\in\mathcal S^{7\times3}
\]

were initially treated as indexed finite sets and as the domain of an \(8\times5\times7\times3\) relational tensor. The present construction adds a geometric interpretation without replacing those discrete addresses.

Each cell is represented by:

\[
\mathcal C_{r,c}=(r,c,x_{r,c},y_{r,c},s_{r,c}),
\]

where `(r,c)` is the discrete address, `(x,y)` is the projected coordinate and \(s_{r,c}\) is the stored state.

The construction is therefore a map from a discrete lattice to a Euclidean representation, followed optionally by periodic attachment to a torus.

## B.2 Triangular/hexagonal projection basis `[E,C]`

Let

\[
q=\begin{bmatrix}c\\r\end{bmatrix}.
\]

Define:

\[
\boxed{
p=H_{hex}q+o
}
\]

with:

\[
\boxed{
H_{hex}=
\begin{bmatrix}
1&1/2\\
0&\sqrt3/2
\end{bmatrix}
}.
\]

For zero origin:

\[
x=c+\frac r2,
\qquad
y=\frac{\sqrt3}{2}r.
\]

The determinant is:

\[
\boxed{
\det(H_{hex})=\frac{\sqrt3}{2}
}.
\]

Thus `sqrt(3)/2` has four exact roles in this declared geometry:

1. altitude of a unit equilateral triangle;
2. vertical spacing of the triangular lattice;
3. determinant of the unit projection basis;
4. area scale from index-basis coordinates to Euclidean coordinates.

These identities do not assign physical universality to the constant.

## B.3 Induced metric `[E]`

The metric in discrete coordinates is:

\[
G=H_{hex}^{T}H_{hex}
=
\begin{bmatrix}
1&1/2\\
1/2&1
\end{bmatrix}.
\]

For index differences:

\[
\Delta q=\begin{bmatrix}\Delta c\\\Delta r\end{bmatrix},
\]

the squared distance is:

\[
\boxed{
d^2=\Delta q^TG\Delta q
=(\Delta c)^2+\Delta c\Delta r+(\Delta r)^2
}.
\]

This allows Euclidean distances to be evaluated directly from array indices.

## B.4 Six-neighbor ring and elementary triangles `[E]`

The six axial directions are:

\[
(1,0),
(0,1),
(-1,1),
(-1,0),
(0,-1),
(1,-1).
\]

Each has unit metric distance from the origin. Their orbit forms a regular hexagonal ring.

The triples:

\[
(c,r),
(c+1,r),
(c,r+1)
\]

and:

\[
(c+1,r),
(c,r+1),
(c+1,r+1)
\]

form oppositely oriented unit equilateral cells.

Therefore the triangular tessellation is embedded in the adjacency structure rather than added as a separate graphic object.

## B.5 Geometric relational tensor `[E,C]`

The projected matrices contain:

\[
8\times5=40
\]

and:

\[
7\times3=21
\]

points.

For every cross-pair define:

\[
D_{r,c,u,v}=P_B(u,v)-P_A(r,c).
\]

Then:

\[
\boxed{
D\in\mathbb R^{8\times5\times7\times3\times2}
}
\]

contains `840` records and two spatial components per record.

Each record may expose:

- `dx`, `dy`;
- Euclidean distance;
- polar angle;
- radial unit vector;
- tangential unit vector.

The original fourth-order relation tensor remains valid; the additional final axis stores geometric components rather than changing the number of A×B relations. This is an indexing/feature construction, not a CP or Tucker decomposition [@kolda2009tensor].

## B.6 Toroidal attachment of the matrix `[E,C]`

Let \(R>r>0\). A ring torus is:

\[
X(u,v)=
\left(
(R+r\cos v)\cos u,
(R+r\cos v)\sin u,
r\sin v
\right).
\]

A periodic matrix is attached by:

\[
u_i=2\pi\frac{i}{N_u},
\qquad
v_j=2\pi\frac{j}{N_v}.
\]

Thus:

\[
(i+N_u,j+N_v)\equiv(i,j).
\]

Rows and columns become two independent angular coordinates. The discrete state identity remains separate from the embedding coordinate.

## B.7 Spherical radial enclosure `[E]`

The norm of the torus point satisfies:

\[
\|X(u,v)\|^2=R^2+r^2+2Rr\cos v.
\]

Therefore:

\[
\boxed{R-r\le\|X(u,v)\|\le R+r}.
\]

The torus is contained in the closed sphere of radius \(R+r\) and is disjoint from the open sphere of radius \(R-r\).

The values:

\[
d_{min}=R-r,
\qquad
d_{median}=R,
\qquad
d_{max}=R+r
\]

are Euclidean radial quantities. They are not geodesic distances measured along the torus.

## B.8 Meridian section and its two branches `[E]`

A plane through the rotational axis produces the meridian circle:

\[
(\rho-R)^2+z^2=r^2.
\]

The two branches are:

\[
z_+(\rho)=+\sqrt{r^2-(\rho-R)^2},
\]

\[
z_-(\rho)=-\sqrt{r^2-(\rho-R)^2}.
\]

They are upper and lower semicircular branches. Calling them “parabolas” would be geometrically incorrect.

The notable points are:

\[
(R-r,0),
(R,0),
(R+r,0),
(R,r),
(R,-r).
\]

## B.9 Maximum equilateral triangle in the meridian circle `[E]`

Three points separated by \(2\pi/3\) around the meridian circle form an inscribed equilateral triangle.

Its side is the chord:

\[
\boxed{a=2r\sin60^\circ=\sqrt3r}.
\]

Its altitude is:

\[
\boxed{h=\frac{\sqrt3}{2}a=\frac{3r}{2}}.
\]

Its circumradius is \(r\) and its inradius is \(r/2\).

This is the maximum-area equilateral triangle inscribed in that circular section. It is a planar cross-sectional result, not a geodesic triangle on the torus surface.

## B.10 Rotating square envelope `[E]`

For a centered square of side \(s\):

\[
r_{in}=\frac{s}{2},
\qquad
r_{out}=\frac{s}{\sqrt2}.
\]

The intersection common to every rotational orientation contains the disk of radius \(s/2\). The union over all orientations is the disk of radius \(s/\sqrt2\).

The orientation-dependent annular width is:

\[
\boxed{
\Delta r=s\left(\frac1{\sqrt2}-\frac12\right)
}.
\]

Accordingly, the square does not become a circle as a static object. The continuous orbit of its orientations defines circular inner and outer envelopes.

## B.11 Quadratic intersection and tangency `[E]`

Let a line in the meridian plane be:

\[
z=m\rho+b.
\]

Substitution into the circular section gives:

\[
(\rho-R)^2+(m\rho+b)^2=r^2,
\]

or:

\[
A\rho^2+B\rho+C=0
\]

with:

\[
A=1+m^2,
\]

\[
B=2(mb-R),
\]

\[
C=R^2+b^2-r^2.
\]

The discriminant:

\[
\Delta=B^2-4AC
\]

classifies two intersections, tangency or no real intersection.

This is the precise role of the quadratic formula (“Bhaskara” in common Brazilian terminology): it solves the line–circle intersection generated by substitution.

## B.12 Tangents constrained to 30 degrees `[E,C]`

A line forming \(30^\circ\) with the radial axis has:

\[
|m|=\tan30^\circ=\frac1{\sqrt3}.
\]

For a fixed slope, the two parallel tangents to the meridian circle have:

\[
\boxed{
b=-mR\pm r\sqrt{1+m^2}}.
\]

For these lines:

\[
\Delta=0.
\]

The angle is therefore an imposed geometric constraint verified by the tangency discriminant. It is not a universal angle produced by every torus.

## B.13 Triangular geodesic-sphere approximation `[E,C]`

A sphere enclosing the torus may be approximated by subdividing an icosahedron and radially projecting the new vertices to a sphere.

For subdivision frequency \(f\ge1\):

\[
V=10f^2+2,
\]

\[
E=30f^2,
\]

\[
F=20f^2.
\]

Hence:

\[
V-E+F=2.
\]

The base icosahedron has equilateral planar faces. After subdivision and radial projection, the resulting spherical triangles form a geodesic approximation; they are not generally an exact tiling by congruent planar equilateral triangles.

## B.14 Linear torus flow and Poincaré section `[E,C]`

Consider the declared linear flow:

\[
u(t)=u_0+\omega_ut\pmod{2\pi},
\]

\[
v(t)=v_0+\omega_vt\pmod{2\pi}.
\]

On the section:

\[
u=0\pmod{2\pi},
\]

one complete \(u\)-turn yields:

\[
\boxed{
P(v)=v+2\pi\frac{\omega_v}{\omega_u}\pmod{2\pi}
}
\]

for \(\omega_u\neq0\).

This is a Poincaré return map for the specified linear flow on \(T^2=S^1\times S^1\). It is conceptually related to return-map methods in dynamical systems [@poincare1890], but it is neither the Poincaré recurrence theorem in full generality nor the Poincaré conjecture.

If \(\omega_v/\omega_u\) is rational, the ideal angular orbit is periodic. If the ratio is irrational, the linear orbit is dense on the ideal torus.

## B.15 Discrete matrix return `[C]`

For \(N_v\) periodic columns:

\[
v_j=2\pi\frac{j}{N_v}.
\]

After one return:

\[
j'=\operatorname{round}
\left(
\frac{N_vP(v_j)}{2\pi}
\right)
\pmod{N_v}.
\]

This defines a discrete circular update of the toroidally attached matrix. Rounding is a modeling choice and must be versioned if replaced by interpolation or probabilistic assignment.

## B.16 Evidence states

| Object | State |
|---|---|
| Projection basis and determinant | `[E] PASS` |
| Induced metric | `[E] PASS` |
| Six-neighbor ring | `[E] PASS` |
| Elementary equilateral cells | `[E] PASS` |
| A×B relation count | `[E] PASS` |
| Geometric tensor feature axis | `[C] PASS` |
| Standard torus embedding | `[E] PASS` |
| Spherical radial bounds | `[E] PASS` |
| Meridian branches | `[E] PASS` |
| Inscribed equilateral triangle | `[E] PASS` |
| Rotating-square envelopes | `[E] PASS` |
| Quadratic intersections | `[E] PASS` |
| 30-degree tangent constraint | `[E,C] PASS` |
| Icosphere combinatorics | `[E,C] PASS` |
| Linear Poincaré return | `[E,C] PASS` |
| Physical vortex | `[H] TOKEN_VAZIO` |
| Venturi mechanism | `[H] TOKEN_VAZIO` |
| Cosmological interpretation | `PROHIBITED_BY_SCOPE` |

## B.17 Reproduction

```bash
python3 PapersPub/08_multiscale_validation_methods/scripts/validate_hex_matrix_projection.py
```

Recorded result:

```text
15/15 deterministic checks PASS
exact_geometry_state = PASS
physical_claims_state = TOKEN_VAZIO
claim_allowed = false
```

The global claim gate remains false because passing finite geometry does not validate physical extrapolations.

## B.18 Final invariant

\[
\boxed{
\text{matrix address}
\rightarrow
\text{hexagonal projection}
\rightarrow
\text{toroidal periodicity}
\rightarrow
\text{meridian section}
\rightarrow
\text{return map}
}
\]

The sphere supplies an external radial bound, the torus supplies two periodic coordinates, the equilateral triangle supplies the \(\sqrt3\) chord relation, the quadratic formula resolves line–section intersections, and the Poincaré map organizes repeated crossings of a declared section.
