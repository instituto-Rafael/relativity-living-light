# RLL Bridge — Rotational Geometry, Elliptic Projection, and Electronic-Shell Control

Date: 2026-09-21  
Author: RAFAEL MELO REIS  
Repository role: scientific consumer / cross-domain falsification bridge  
State: FORMALIZED_UNTESTED  
claim_allowed=false

## Authority boundary

Mathematical authority for this round belongs to:
rafaelmeloreisnovo/Matem-tica-/docs/formal/ROTATIONAL_BASE_GEOMETRY_ARC_ELLIPSE_LAYERS_V1_2026-09-21.md

Research exposition belongs to:
rafaelmeloreisnovo/papers/research_notes/2026-09-21_ROTATIONAL_GEOMETRY_ARC_ELLIPSE_ELECTRON_SHELL_BRIDGE.md

RLL does not redefine the mathematics. It only records the minimum bridge needed for later falsification.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.

## G — geometry model

For a regular polygon layer:
G_(k+1)=G_k sec(pi/p_k)
for outward expansion, equivalently
G_(k+1)=G_k cos(pi/p_k)
for inward polygon->incircle contraction depending on orientation of the step.

Circular local relations:
s=R theta,
c=2R sin(theta/2),
d=R cos(theta/2),
A_seg=(R^2/2)(theta-sin theta).

Circle projected at inclination i:
b/a=|cos i|,
e=|sin i|,
A_e/A_c=|cos i|.

## Q — hydrogenic control

For hydrogenic Bohr-radius scaling:
Q_n=(a0/Z)n^2,
Q_(n+1)/Q_n=((n+1)/n)^2.

Principal-shell state count including spin:
N_n=2n^2.

These equations are controls from established atomic models; they are not outputs of G.

## Comparator

Define a dimensionless scale-ratio residual:
epsilon_n = sec(pi/p_n) - ((n+1)/n)^2.

Optional relative residual:
epsilon_n_rel = sec(pi/p_n)/[((n+1)/n)^2] - 1.

A candidate rule p_n must be fixed before fitting. Post-hoc p_n selection is not evidence.

Required null controls:
1. constant p;
2. random admissible p_n sequences;
3. simple monotone p_n baselines;
4. held-out n values;
5. complexity penalty for fitted p_n rules.

## Projection control

If an observed 2D ellipse is proposed as a projected circular layer, estimate:
i_hat = arccos(b/a).

Then verify independently:
e ?= sin(i_hat),
A_e/A_c ?= cos(i_hat).

This is a geometric consistency test only. It does not identify an orbital.

## Claim gates

GATE-RG-1 exact geometry verifier = NOT_RUN.
GATE-RG-2 deterministic n-gon table = NOT_RUN.
GATE-RG-3 square rotation sweep = NOT_RUN.
GATE-RG-4 ellipse projection recovery = NOT_RUN.
GATE-RG-5 electron-shell comparator with nulls = NOT_RUN.
GATE-RG-6 real physical observable mapping = TOKEN_VAZIO.
GATE-RG-7 independent reproduction = TOKEN_VAZIO.

Therefore:
GEOMETRIC_FORMALIZATION=AVAILABLE,
PHYSICAL_BINDING=TOKEN_VAZIO,
claim_allowed=false.

## R3

F_ok: a typed G-versus-Q bridge now exists without converting analogy into mechanism.
F_gap: no RLL runtime, dataset, fitted p_n rule, or physical observable binding has been executed.
F_next: consume a passed Mathematics verifier, then run null-controlled residual comparisons before any RLL scientific promotion.


## Successor control — generalized rotational sweep

The geometry producer now also defines for a regular p-gon:
core_fraction = cos^2(pi/p),
swept_annulus_fraction = sin^2(pi/p),
annulus_to_core = tan^2(pi/p).

For nested layers:
area_scale = product_k cos^2(pi/p_k).

After final circle projection at inclination i:
projected_area_scale = |cos i| * product_k cos^2(pi/p_k).

For half-step superposition, the central intersection is a regular 2p-gon with:
R_intersection/R = cos(pi/p)/cos(pi/(2p)).

RLL usage is diagnostic only. No physical observable is assigned by these identities.

Quantum control is strengthened by:
sum_(l=0)^(n-1)(2l+1)=n^2,
2*n^2 including spin.

New required falsifier:
compare any proposed p_n mapping against constant-p, monotone-p and random-p baselines, and require held-out predictive gain. Otherwise PHYSICAL_BINDING remains TOKEN_VAZIO.
