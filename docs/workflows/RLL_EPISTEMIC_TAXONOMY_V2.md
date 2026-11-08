# RLL epistemic taxonomy V2 — orthogonal six classes and evidence states

**Purpose:** integrate the six conceptual classes raised in project discussion, without
misrepresenting them as a universal academic ladder or deleting the V1 graph.
**Status:** LOCAL_TAXONOMY_PROPOSAL; structural only, claim_allowed=false.

## Two independent axes, one auditable map

**Six proposed types (nonordered):**
1. Proposition / conjecture — precise statement and assumptions, not proof.
2. Scientific hypothesis — falsifiable and measurable predictions under a stated mechanism.
3. Mathematical or physical model — mathematical representation, parameters, units and domain.
4. Formal theorem or identity — deductive proof relative to axioms, not an empirical measurement.
5. Empirical law — observed regularity, scope, uncertainty, independent replication.
6. Scientific theory — broad explanatory and predictive framework supported by independent tests.

**Evidence states (reused, not invented):** read exactly the seven values from
`data/contracts/rll_scientific_validation_orchestrator.v1.json`:
`TOKEN_VAZIO`, `DECLARED_BY_AUTHOR`, `OBSERVED_PENDING_REPLICATION`,
`VERIFIED_LIMITED`, `VERIFIED_REPRODUCIBLE`, `CONTRADICTION`, `FALSIFIED_IN_SCOPE`.
Classes are not a progress ranking. A law does not 'graduate' into a theory;
a theorem is not proven by observing the sky. Confidence is not journal prestige.

## Source mapping, no invented evidence

| Existing V1 node | Proposed type V2 | V2 evidence state | Caveat |
|---|---|---|---|
| EUCLIDEAN_DIAGONAL | Formal theorem / identity | DECLARED_BY_AUTHOR | standard mathematical relation; this CI does not certify a proof |
| MITO_ATP | UNCLASSIFIED_TOKEN_VAZIO | DECLARED_BY_AUTHOR | empirical reference is not itself necessarily a law or a theory |
| TRIBO_XRAY_CELL | Proposition / conjecture | TOKEN_VAZIO | physical mechanism and measurable observable missing |
| LCDM_BACKGROUND | Mathematical/physical model | DECLARED_BY_AUTHOR | well established externally; current RLL G4 fit not run in this gate |
| RLL_BACKGROUND | Mathematical/physical model | DECLARED_BY_AUTHOR | exploratory local model; no RLL physical validation inferred |

V2 maps V1 by exact Git blob SHA-1 and reuses official states by their governed
contract. On V1 changes, freeze/reconcile and supersede mapping rather than silently reinterpret.

## Relations as possibilities, not implications

`CAN_BE_REFORMULATED_AS`, `CAN_BE_PROVED_AS`, `CAN_BE_REPRESENTED_BY`,
`MAY_CONTRIBUTE_TO_REGULARITY`, `MAY_CONTRIBUTE_TO`, `MAY_CONSTRAIN`
all require named conditions and have `implies_validity=false`.

The validator rejects attempts to map an empirical reference directly to an
empirical law/theory, declare a bio-X-ray conjecture verified, or map a cosmological
model to a validated scientific theory without its independent evidence pathway.

## Exactly what code is executed

- `tools/ci/rll_epistemic_taxonomy_gate_v2.py`: standard-library validation and
  scoped five-node case matrix; no network, no inference, no secrets.
- `tests/test_rll_epistemic_taxonomy_gate_v2.py`: adversarial classification tests.
- `.github/workflows/rll-calibration-orchestrator.yml`: an extra PR/preflight stage,
  reusing the existing workflow; no new schedules, providers or secret access.
- The original V1 graph and the 12 scientific G0–G11 controls remain unchanged.

Review readiness is not promotion: even a full synthetic receipt can only output
`READY_FOR_HUMAN_REVIEW_NOT_A_CLAIM_OR_STATUS_MUTATION`. Scientific claims still
require real observations, Bayesian likelihood, independent checks and domain gates.

Reproduction: `python tools/ci/rll_epistemic_taxonomy_gate_v2.py --require-pass`,
`python -m unittest discover -s tests -p test_rll_epistemic_taxonomy_gate_v2.py -v`.

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`.
Rollback: close DRAFT PR or revert additive files/one workflow step. Never modify original V1 sources.
