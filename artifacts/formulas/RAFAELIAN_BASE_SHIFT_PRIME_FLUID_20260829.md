# RAFAELIAN Base-Shift, Prime Coordinates and Modular Information Fluid

Date: 2026-08-29
State: FORMAL_RESEARCH_NOTE
claim_allowed: false

## 1. Positional shift invariant
For integer base b>=2, define S_b(N)=bN. Multiplication by the maximal digit is

(b-1)N = S_b(N)-N.

Thus in base 10: 9N=10N-N. This is a positional shift plus subtraction, not a change of numeric value.

## 2. Internal presence layer
The user-declared notion "base one = ter/não ter + próximo dígito" is represented only as an internal boolean/unary occupancy layer, not as conventional positional base 1. A base-b digit d may be represented by occupancy states s_j in {0,1}, d=sum_{j=1}^{b-1}s_j where an ordered thermometer encoding is desired.

## 3. Prime support of bases 7, 14, 10
Prime factorizations:
7=7; 14=2*7; 10=2*5.
Therefore the prime support is {2,5,7} and

lcm(7,14,10)=70.

gcd(14,10)=2; 70/2=35=5*7.

## 4. Rooted residue convention
Standard modulo is never redefined. For geometric display only define

rho_m(n) = m if n mod m = 0, otherwise n mod m.

Hence rho_7(35)=7 and rho_10(35)=5, producing display coordinate P_35=(7,5) while the arithmetic invariant 7*5=35 is preserved.

## 5. Prime valuation coordinates
Use standard p-adic valuations as an exact factor-coordinate layer:

V_P(n)=(v_2(n),v_5(n),v_7(n),...).

For 70: (1,1,1) on axes (2,5,7). For 35: (0,1,1). The transition 70->35 removes one factor 2.

## 6. Modular information fluid
Let R_m(n)=n mod m. A visualization family may curve the coordinate without changing n:

N -> R_m(N) -> theta=2*pi*R_m/m -> (cos theta,sin theta) -> G_lambda.

G_lambda is a display lens/deformation parameter. Arithmetic invariants remain anchored in the exact source object.

Core boundary:

curved visualization != changed number.

A repeating expansion may likewise be represented by its exact remainder orbit and circular embedding. The geometry encodes the orbit; it does not alter p/q.

## 7. Candidate prime-geometry experiment
For n in a finite range, calculate exact residue signatures over selected prime moduli, retain standard gcd/lcm/valuation data, then compare linear, circular and curved projections. Test whether composites exhibit repeatable intersections or orbit structures and whether primes are visually separable.

No efficiency or new primality/factorization claim is allowed without benchmark and proof.

## 8. Invariants
- exact object precedes decimal display;
- standard modulo remains authoritative;
- rho_m is display-only closure labeling;
- deformation changes coordinates, not arithmetic value;
- raw ratio/provenance survives reduction where relevant;
- source chronology/evidence cannot be permuted;
- unverified performance/novelty remains TOKEN_VAZIO.

F_ok: base shift, lcm/gcd structure, prime valuations, rooted-display residue and modular deformation are formalized.
F_gap: no demonstrated advantage over established primality/factorization methods; optimal G_lambda is TOKEN_VAZIO.
F_next: test n=1..70 under moduli 7,10,14 and prime-modulus signatures, comparing linear/circular/curved views with exact invariants.
