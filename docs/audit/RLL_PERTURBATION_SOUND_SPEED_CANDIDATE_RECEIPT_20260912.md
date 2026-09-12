# RLL Perturbation Rest-Frame Sound-Speed Candidate V1 — append-only receipt

Date: 2026-09-12  
Authority: `instituto-Rafael/relativity-living-light`  
Gap: `GROWTH-CS2-001`  
Claim allowed: **false**

## SOURCE

Repository negative evidence:
- `tools/rll_perturbation_barotropic_candidate_v1.py`;
- exact-head CLASS/CAMB run #49 preserved the result `FALSIFIED_AS_GLOBAL_DEFAULT`;
- 0/9 swept cases passed the minimal background-derived barotropic/adiabatic closure gate.

Primary literature used only to justify an **independent comparator parameterization**:
- Wayne Hu, *Structure Formation with Generalized Dark Matter*, astro-ph/9801234;
- Weller & Lewis, *Large Scale Cosmic Microwave Background Anisotropies and Dark Energy*, astro-ph/0307104.

Comparison precedent:
- Rapetti et al., astro-ph/0409574, uses `c_s^2=1` as a smooth dark-energy-fluid comparison.

No third-party code was copied.

## CONFIGURATION

V1 candidate:

`SMOOTH_REST_FRAME_CS2_ONE_COMPARATOR`

with:

`c_s,rest^2 = 1`.

This is explicitly:
- dimensionless;
- constant;
- in the causal comparator interval `[0,1]`;
- independent of `c_a^2`;
- **not derived from the RLL background**;
- **not effective in a perturbation solver yet**.

Therefore:

`CONFIG_ACCEPTED != CONFIG_EFFECTIVE`.

## WHY THIS FILLS THE TOKEN WITHOUT OVERCLAIMING

Before this delta:
`TOKEN_VAZIO_REST_FRAME_SOUND_SPEED_POLICY`.

After this delta:
`CONFIGURED_CANDIDATE_NOT_EFFECTIVE`.

The unknown theory is not replaced by certainty. Only one bounded comparator choice is frozen so the remaining perturbation-policy gaps can be tested independently.

## STILL OPEN

- `GROWTH-QMU-001`;
- `GROWTH-SIGMA-001`;
- `GROWTH-GAUGE-001`;
- `GROWTH-IC-001`;
- `GROWTH-CONSERVATION-001`.

In particular, the gauge-dependent pressure mapping remains:
`TOKEN_VAZIO_GAUGE_POLICY`.

## FALSIFIERS

Reject or roll back this candidate if:
- `c_s,rest^2` leaves `[0,1]`;
- it is represented as background-derived;
- it is silently equated to `c_a^2`;
- it is marked effective before solver/conservation execution;
- downstream conservation/regularity/gauge/stability gates fail.

## NON-REGRESSION

- background/CMB evidence unchanged;
- 0/9 negative barotropic evidence preserved;
- no growth likelihood changed;
- no `D(z)` implementation added;
- no historical outputs rewritten;
- `claim_allowed=false`.

## F_ok

- sound-speed policy token reduced to an explicit versioned comparator;
- provenance and falsifiers attached;
- configuration/effectiveness boundary explicit.

## F_gap

- interaction current, shear, gauge and initial conditions remain open;
- conservation/regularity execution remains blocked.

## F_next

`GROWTH-QMU-001`: freeze the interaction-current policy without inferring `Q_mu=0` solely from the background notation.

SOURCE != CONFIG != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
