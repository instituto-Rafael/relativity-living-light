# Appendix C — Four opposed axes and axial/diagonal matrix ports

**Status:** `exact geometry + exact mathematical operators = PASS`  
**Empirical fluid/material interpretation:** `NOT_APPLICABLE`  
**Author:** Rafael Melo Reis (∆RafaelVerboΩ)  
**Canonical context:** *From the Observed Void to Recurrence*

## C.1 Scope

The model contains four opposed axes through one center:

1. vertical;
2. horizontal;
3. rising diagonal;
4. falling diagonal.

Each axis has two mouths:

\[
4\text{ axes}\times2\text{ mouths}=8\text{ ports}.
\]

The term *port* denotes a geometric/computational gate.

## C.2 Meridian positions

For center

\[
C=(R,0)
\]

and minor radius `r>0`, define

\[
P(\theta)=C+r(\cos\theta,\sin\theta).
\]

| Port | Axis | Angle |
|---|---|---:|
| upper | vertical | `90°` |
| lower | vertical | `270°` |
| right | horizontal | `0°` |
| left | horizontal | `180°` |
| upper-right | rising diagonal | `45°` |
| lower-left | rising diagonal | `225°` |
| upper-left | falling diagonal | `135°` |
| lower-right | falling diagonal | `315°` |

## C.3 Opposed-pair invariants

For every axis:

\[
\frac{P_++P_-}{2}=C,
\qquad
\|P_+-P_-\|=2r.
\]

All four channels therefore share the same center and diameter.

## C.4 Matrix projection

\[
\mathcal N_8=\{(0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,-1),(-1,1),(1,-1)\}.
\]

Diagonal steps use

\[
\widehat d_{\mathrm{diag}}=\frac1{\sqrt2}(\pm1,\pm1).
\]

Thus axial and diagonal directions have equal unit Euclidean length.

## C.5 Radial and tangential bases

At `P(theta)`:

\[
\widehat n=(\cos\theta,\sin\theta),
\qquad
\widehat t=(-\sin\theta,\cos\theta),
\]

with

\[
\widehat n\cdot\widehat t=0.
\]

The tangent aperture is

\[
\widehat n\cdot X=\widehat n\cdot P.
\]

## C.6 Relation to the quadratic layer

For nonvertical candidate lines

\[
z=m\rho+b,
\]

substitution into

\[
(\rho-R)^2+z^2=r^2
\]

produces a quadratic equation. Tangency is identified by

\[
\Delta=0.
\]

The earlier `30°` family and the present `45°` diagonal family are distinct:

- `30°`: triangular/tangent construction;
- `45°`: square-diagonal/matrix construction.

## C.7 Toroidal sweep

For meridian coordinates `P=(rho_P,z_P)`:

\[
X_P(u)=(\rho_P\cos u,\rho_P\sin u,z_P).
\]

Each port generates one projected ring. The sweep preserves

\[
\sqrt{(\sqrt{x^2+y^2}-R)^2+z^2}=r.
\]

## C.8 Venturi and vortex as mathematical operators

In this paper the terms do not denote fluid phenomena.

### Base Venturi

\[
\boxed{\mathcal V_b(n)=(q,r),\quad n=bq+r}.
\]

It folds a linear address into a finite base aperture while retaining carry.

### Cyclic vortex

\[
\boxed{\mathcal W_b(n,\delta)=E_b(n+\delta)},\qquad\delta\ge0.
\]

It advances through a cyclic phase by addition while retaining cycle and winding.

The complete formalism is given in [`appendix_d_cyclic_base_curvature.md`](./appendix_d_cyclic_base_curvature.md).

## C.9 Base-seven seam

Ordinary positional notation gives

\[
7_{10}=10_7.
\]

Euclidean division gives

\[
7=1\cdot7+0
\Rightarrow
E_7(7)=(1,0).
\]

One-based cyclic phase gives

\[
p_7(7)=1+((7-1)\bmod7)=7.
\]

Therefore `7 mod 7 = 0` is only the remainder projection; it does not erase the complete state.

## C.10 Zero and additive transitions

Zero may be a valid value, placeholder, seam, remainder or all-off word. It is not equivalent to missing information.

In fixed-width unsigned arithmetic:

\[
a-b\equiv a+(\sim b+1)\pmod{2^w}.
\]

The RAFAELIA operator restricts state transitions to non-negative addition, carry and wrap.

## C.11 Reproduction

```bash
python3 PapersPub/08_multiscale_validation_methods/scripts/validate_four_axis_flow_ports.py
```

Expected:

```text
21/21 checks PASS
axis_count = 4
port_count = 8
exact_geometry_state = PASS
operator_state = PASS
claim_allowed = true
empirical_fluid_interpretation = NOT_APPLICABLE
```

## C.12 Canonical invariant

\[
\boxed{
\text{one center}
+\text{four opposed axes}
+\text{eight ports}
+\text{base carry}
+\text{cyclic phase}
=\text{non-extinguished projected state}
}.
\]
