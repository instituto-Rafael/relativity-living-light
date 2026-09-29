# RLL — Non-null Blind Recovery Q16 Freestanding V1

**Date:** 2026-09-28  
**State:** \`IMPLEMENTED_UNTESTED\`  
**Author/proponent:** Rafael Melo Reis  
**claim_allowed:** \`false\`

## 1. Intent

Create the smallest executable gate that can answer one question before any
Poincaré/Venturi/geodesic/calendar extension:

> can the canonical RLL background kernel recover a deliberately injected,
> non-null \(\Omega_{s0}\) profile under a frozen low-level numerical surface?

This is not a real-data fit and not independent replication. It is a
deterministic identifiability/recovery gate.

## 2. Runtime form

The runtime is one C translation unit:

\`core/lowlevel_runtime/c/rll_nonnull_blind_q16_freestanding.c\`

It intentionally uses:

- no headers;
- no libc/stdlib/stdio/string/math;
- no heap, \`malloc\`, \`free\` or garbage collector;
- no structs/classes;
- no function pointers;
- no runtime filesystem;
- no parser;
- no external runtime library;
- no floating point;
- no hosted \`main\`;
- one \`_start\` entry;
- direct Linux \`write\`/\`exit\` syscalls only at the observable boundary;
- Q16.16 arithmetic implemented in the translation unit;
- flat arrays addressed by integer offsets.

The numerical core is therefore independent of Python/NumPy/SciPy at runtime.

## 3. Frozen source profile

The profile is not newly selected after looking at this gate. It is the
pre-existing nominal non-null profile already documented in
\`docs/science/RLL_HZ_REAL_FREESTANDING_MODEL.md\`:

\`\`\`text
H0       = 67.4
Omega_m  = 0.315
Omega_s0 = 0.02
z_t      = 1.0
w_t      = 0.3
\`\`\`

Q16 materialization:

\`\`\`text
H0       = 4417126
Omega_m  = 20644
Omega_s0 = 1311
z_t      = 65536
w_t      = 19661
\`\`\`

The 33 \(z\) and \(\sigma_H\) entries come from the existing canonical
Q16 materialization of \`data/real/Hz_data_real.csv\`.

## 4. Model

The gate implements the existing late-time phenomenological RLL background:

\[
f(z)=\frac{1}{1+\exp((z-z_t)/w_t)}
\]

\[
E^2(z)=
\Omega_m(1+z)^3+
(1-\Omega_m-\Omega_{s0})+
\Omega_{s0}\left[f+(1-f)(1+z)^3\right]
\]

\[
H(z)=H_0\sqrt{E^2(z)}.
\]

Square root, exponential and division are implemented locally with integer
algorithms. No \`math.h\` or compiler-visible hosted math call is permitted.

## 5. Matrix/address model

There are no runtime objects.

\`\`\`text
D[row*2 + 0] = z_q16
D[row*2 + 1] = sigma_q16

Y[row]        = injected synthetic observation

B[0]          = recovered Omega_s0
B[1]          = recovered z_t
B[2]          = recovered w_t
B[3:4]        = chi2 accumulator
B[5]          = evaluated grid cells
\`\`\`

The recovery manifold is discrete and frozen before execution.

### Omega_s0

\`\`\`text
0
1 + k*131, k=0..20
\`\`\`

The nominal injection \`1311\` is an exact cell.

### z_t

\`\`\`text
39322 45875 52429 58982 65536 72090 78643 85197 91750
\`\`\`

### w_t

\`\`\`text
13107 14746 16384 18022 19661 21299 22938 24576 26214
\`\`\`

Cells per scan:

\[
22\times9\times9=1782.
\]

Each cell consumes all 33 frozen redshift/error coordinates.

## 6. Three execution arms

### A — exact non-null

Generate \(Y\) from the non-null injected profile and recover the minimum
without perturbation.

Required:

\`\`\`text
Omega_s0=1311
z_t=65536
w_t=19661
chi2_q16=0
\`\`\`

### B — deterministic perturbation

Apply the fixed repeating code

\`\`\`text
-2,-1,0,1,2
\`\`\`

as

\[
\Delta H_i = \sigma_i\,c_i/32.
\]

There is no RNG, seed, clock or entropy source.

Required recovery remains the same frozen non-null cell.

### C — null boundary

Generate the same surface with \(\Omega_{s0}=0\).

Only

\`\`\`text
recovered Omega_s0 = 0
\`\`\`

is asserted. \(z_t\) and \(w_t\) are deliberately **not** asserted because
they are non-identifiable when the sector amplitude is zero.

## 7. Evidence gate

The dedicated CI must prove:

1. no hosted \`#include\`;
2. no external declaration;
3. static x86_64 ELF;
4. no undefined symbols;
5. no \`INTERP\`;
6. no \`NEEDED\`;
7. exact non-null recovery PASS;
8. perturbed recovery PASS;
9. null-boundary recovery PASS;
10. static ARMv7 cross-link;
11. no unresolved \`__aeabi_*\`;
12. ARM ELF32 identity.

ARMv7 cross-build is not physical ARM execution.

## 8. Boundary

\`\`\`text
SYNTHETIC_RECOVERY != REAL_DATA_MODEL_SELECTION
SAME_BINARY_RECOVERY != INDEPENDENT_REPLICATION
CROSS_BUILD != PHYSICAL_EXECUTION
LOWLEVEL_PASS != PHYSICAL_COSMOLOGY_CLAIM
OMEGA_S0=0 => Z_T/W_T_NON_IDENTIFIABLE
\`\`\`

The term "blind" here means that the grid scanner receives only the synthetic
matrix and does not use the injection parameter variables in its scoring
operation. Because generator and scanner are compiled into the same binary,
this is **not** an independent or double-blind experiment.

## R3

\`\`\`text
F_ok =
single-unit low-level kernel materialized
+ source profile provenance fixed
+ exact/stress/null arms encoded
+ no-heap/no-libc runtime contract encoded

F_gap =
provider execution
+ physical ARMv7 execution
+ independent binary/reimplementation
+ held-out real-data discrimination

F_next =
run provider gate
-> if PASS, record immutable receipt
-> then run the exact source on physical ARMv7
-> only after that separate the generator and recovery executables for
   materially independent replication
\`\`\`


## Routing receipt pointer

Draft PR: `instituto-Rafael/relativity-living-light#1007`.
Provider result remains `PENDING` until the exact-head gate terminates.
