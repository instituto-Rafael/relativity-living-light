# Appendix D — Non-extinguishing cyclic-base curvature

**Status:** `exact mathematical-computational formalism = PASS`  
**Empirical fluid/material interpretation:** `NOT_APPLICABLE`  
**Author:** Rafael Melo Reis (∆RafaelVerboΩ)

## D.1 Scope

The terms *Venturi* and *vortex* in this formalism name mathematical operators:

- **base Venturi:** folding a linear abscissa into a finite base aperture while retaining carry;
- **cyclic vortex:** additive return through a one-based phase cycle while retaining cycle and winding.

They are not claims about pressure, density, viscosity, nozzles or material vortices.

## D.2 Euclidean division as complete state

For `n>=0` and `b>=2`, Euclidean division gives

\[
n=bq+r,
\qquad
0\le r<b.
\]

Ordinary modulo projects the complete state onto the remainder:

\[
\pi_r(n)=n\bmod b=r.
\]

The non-extinguishing state is

\[
\boxed{E_b(n)=(q,r)}.
\]

It is exactly reversible:

\[
\boxed{n=bq+r}.
\]

Therefore a zero remainder does not imply a zero state.

## D.3 Decimal seven and base seven

In ordinary positional notation,

\[
\boxed{7_{10}=10_7}.
\]

Indeed,

\[
7=1\cdot7+0.
\]

Hence

\[
7\bmod7=0
\]

is correct only as the remainder projection, while

\[
\boxed{E_7(7)=(1,0)}
\]

retains the carry.

The digit `7` is not a positional digit in base seven. It can, however, label the seventh phase in a one-based cyclic alphabet.

## D.4 One-based cyclic phase

For positive `n`, define

\[
\boxed{p_b(n)=1+((n-1)\bmod b)}.
\]

Then

\[
p_7(7)=7,
\qquad
p_7(8)=1.
\]

This yields three compatible descriptions:

```text
ordinary positional:  7 decimal -> 10 base 7
Euclidean state:      7 decimal -> quotient 1, remainder 0
one-based cycle:      7 decimal -> cycle index 0, phase 7
```

## D.5 Base Venturi operator

Define

\[
\boxed{\mathcal V_b(n)=E_b(n)=(q,r)}.
\]

The visible coordinate is narrowed to the finite aperture

\[
r\in\{0,1,\ldots,b-1\},
\]

while `q` stores the overflow/carry. The operator is lossless when both components are retained.

Calling this a *Venturi* describes address contraction and redistribution, not fluid acceleration.

## D.6 Curvature of the abscissa

Lift the abscissa to angular coordinate

\[
\Theta_b(n)=\frac{2\pi n}{b}.
\]

Its circular projection is

\[
\gamma_b(n)=
\left(
R\cos\Theta_b(n),
R\sin\Theta_b(n)
\right).
\]

At `n=b`,

\[
\Theta_b(b)=2\pi,
\]

so the circular coordinate reaches the same seam as `n=0`. The path is not identical: it has completed one turn.

A lifted curve preserves this history:

\[
\boxed{
\Gamma_b(n)=
\left(
R\cos\Theta_b(n),
R\sin\Theta_b(n),
\lambda\frac{\Theta_b(n)}{2\pi}
\right)
}.
\]

`n=0` and `n=b` may share `(x,y)` but have different lifted coordinate `z`.

## D.7 Additive vortex-return operator

For a non-negative increment `delta`, define

\[
\boxed{\mathcal W_b(n,\delta)=E_b(n+\delta)}.
\]

Examples for `b=7`:

```text
6 + 1 -> phase 7
7 + 1 -> phase 1 with increased carry/cycle
```

The phase returns; the total state does not lose its path history.

## D.8 Zero as state, seam and placeholder

The formalism distinguishes

\[
0\text{ as value}
\]

from

\[
\text{missing information}.
\]

Zero can be a valid word, remainder, placeholder, address, seam or all-off bit pattern. Thus

\[
\boxed{0\ne\text{absence}}.
\]

## D.9 Addition-only unsigned transition

In fixed-width unsigned arithmetic, subtraction can be implemented through addition of the two's complement:

\[
\boxed{a-b\equiv a+(\sim b+1)\pmod{2^w}}.
\]

For eight bits,

\[
0-1\equiv255\pmod{256}.
\]

This does not deny that instruction sets may expose subtraction opcodes. It states the implementation invariant used here: state transitions are encoded through addition, complement, carry and wrap; no signed-negative state is required in the unsigned channel.

## D.10 Relation to the eight ports

The four-axis/eight-port geometry supplies directional gates. The cyclic-base operators supply address evolution through those gates:

\[
\boxed{
\text{gate}
+\text{base aperture}
+\text{carry}
+\text{phase}
+\text{winding}
=\text{non-extinguished curved state}
}.
\]

## D.11 Exact claims

```text
7_10 = 10_7                         PASS
7 mod 7 = 0 as remainder            PASS
E_7(7) = (1,0)                      PASS
p_7(7) = 7                          PASS
reconstruction n=bq+r               PASS
curved seam preserves winding       PASS
additive unsigned wrap              PASS
empirical_fluid_interpretation      NOT_APPLICABLE
```

## D.12 Reproduction

Runtime source and unit tests are routed to `rafaelmeloreisnovo/ChipQuantum`:

```text
src/geometry/sqrt3_geometry_matrix/cyclic_base_curvature.py
tests/test_cyclic_base_curvature.py
```

Recorded local result:

```text
11/11 unit tests PASS
12/12 aggregate invariants PASS
```
