# QREL × RLL — conditional semiclassical horizon gate V1

Status: IMPLEMENTED_LOCAL_TESTED; REMOTE_CI_NOT_YET_VERIFIED; PHYSICS_CLAIM_BLOCKED.
Producer: instituto-Rafael/relativity-living-light; additive branch-only change.
Primary source: Philipp Dorau and Albert Much, From Quantum Relative Entropy to the Semiclassical Einstein Equations, Physical Review Letters 136, 091602 (2026), https://doi.org/10.1103/lmq8-nsty (CC BY 4.0).
Frozen base commit: 81b55362b2b5c62265aa07d9e35cc976ab5622f4.

## Defined states and boundaries

- omega_0: restricted quasifree Killing-flow invariant Hadamard/KMS vacuum on horizon algebra, as specified by the paper. NOT represented by the test program.
- omega_phi: Weyl-displaced coherent state for a real, minimally coupled Klein–Gordon field. Not reconstructed by the program.
- S_rel(omega_0 || omega_phi): Araki–Uhlmann relative entropy; distinct from Shannon, semantic compression, thermodynamic entropy and TOKEN_VAZIO.
- T_kk: null-null expectation of the normal-ordered coherent-state stress tensor; equals (partial_U phi)^2 under paper assumptions.
- delta A: approximate Rindler horizon cross-section area variation, conditional on paper's metric perturbation ansatz and external entropy–area assumption.
- g_ab, R_ab: metric and Ricci tensor. The program does not implement a curved-spacetime solution.
- epsilon_RLL: physical departure from GR/ΛCDM. TOKEN_VAZIO_NOT_SPECIFIED; no observational predictions were added.

## Paper relationships and epistemic classification

PRL Eq. 12 and 18, for U <= 0, in natural units c=G=hbar=k_B=1:

    S_rel(omega_0 || omega_phi) = -2*pi * integral_H U (partial_U phi)^2 dU dA
    < :T_ab: >_phi k^a k^b = (partial_U phi)^2

The paper derives the relative entropy using modular theory (Eq. 4–12). The identification with geometric area uses an ADDITIONAL perturbation ansatz (Eq. 19–20), local approximate Raychaudhuri geometry (Eq. 21–24), the null-contracted relation (Eq. 25), metric-proportional ambiguity (Eq. 26), and conservation/Bianchi reasoning (Eq. 27), giving its conditional semiclassical Einstein equations (Eq. 28). The Bekenstein–Hawking identification S_rel = delta A / 4 supplies alpha = 8*pi.

The phrase 'conditional semiclassical consistency gate' is deliberate: this code does NOT prove the Araki–Uhlmann identity or the field equations and does not establish emergent quantum gravity.

## Finite algebra witness

Choose a unit transverse area and finite null coordinate U in [-L, 0], with toy polynomial phi(U) = A U^2 (U+L)^2 inside and zero outside. The zero extension is C1 but not C-infinity; therefore it is NOT the smooth compactly supported coherent excitation required for the paper's algebraic proof. It is only a surrogate for the elementary null-flux integral.

    partial_U phi (A=L=1) = 4 U^3 + 6 U^2 + 2 U
    F = integral_-1^0 (-U) (partial_U phi)^2 dU = 1/105
    S_rel/pi = 2/105 (paper flux normalization, imported)
    delta A/pi = 8/105 (ONLY IF independent area law assumed)
    alpha/pi = 8 (ONLY IF area assumption and nonzero F)
    F(A,L) = A^2 * L^8 / 105

Fraction arithmetic computes exact rational moments. Midpoint quadrature separately verifies the magnitude and orientation. The 1+1 Lorentz-signature null contraction check establishes an elementary metric-kernel identity on two null vectors, not the 4D tensor theorem.

## Executable falsifiers

Run from repository root:

    python3 -m unittest discover -s tests -p 'test_qrel_horizon_gate.py' -v
    python3 -c 'from tools.qrel_horizon_gate import gate_witness; print(gate_witness())'

Nine deterministic local tests verify: independent rational moment, finite midpoint quadrature, amplitude/length scaling, area law absent means alpha undefined, conditional factor eight, zero flux means no alpha inference, rejection of noncoherent or negative flux, float/endpoints/length/degree rejection, 1+1 null identities and counterexamples, and claim_allowed=false.

Negative gates do NOT inspect or alter the RLL cosmology production model. No physical claim follows from passing software tests.

## Claims and remaining gaps

| Layer | State |
| --- | --- |
| Araki–Uhlmann QFT theorem | UPSTREAM_PUBLISHED_DERIVATION; not independently reproduced |
| Polynomial integral, scaling and negative tests | LOCAL_TEST_PASSED (local test command), provider CI pending |
| Relative entropy to horizon area | EXPLICIT_BH_ASSUMPTION / METRIC_ANSATZ |
| Four-dimensional semiclassical Einstein dynamics | UPSTREAM_CONDITIONAL_ARGUMENT; NOT_IMPLEMENTED |
| RLL deviation from GR, cosmic fit, quantum gravity | TOKEN_VAZIO_NOT_TESTED; claim_allowed=false |

To upgrade: establish a C-infinity smooth horizon test function and modular algebra; inspect stress tensor/area perturbation without circular field-equation assumptions; choose a covariantly conserved RLL source, explicit dimensional convention and 4D geometric model; predict a residual before observational fitting and compare against GR/ΛCDM under the existing falsification matrix. A valid negative result must remain visible.

Rollback: remove the three new files from the isolated branch or close the draft PR. No edits to existing source, datasets or CI workflow counts. No auto-merge, physical deployment or claim promotion.
