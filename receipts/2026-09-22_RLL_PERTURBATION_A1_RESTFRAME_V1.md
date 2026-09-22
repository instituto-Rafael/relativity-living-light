# μWRITE — RLL P0 Perturbation A1.1 — 2026-09-22

State: CANONICAL_PR_INTAKE / CI_PENDING / CLAIM_BLOCKED

μID=RLL-PERTURB-A1-RESTFRAME-20260922-V1

parent:
- data/science/perturbations/RLL_PERTURBATION_CLOSURE_CONTRACT_20260808_V1.json
- data/governance/RLL_GROWTH_SEMANTICS_FINAL_CONSOLIDATION_V1.json
- docs/audit/RLL_GAP_RETROFEEDBACK_RECEIPT_20260912.md

negative_evidence_preserved:
A0 conserved+barotropic/adiabatic+Q0+sigma0 = 0/9 PASS, FALSIFIED_AS_GLOBAL_DEFAULT.

new_candidate:
A1.1 = separately conserved + independent rest-frame closure
cs2_rest=1
Q_mu=0
sigma_s=0

boundary:
cs2_rest=1 is a versioned research-candidate assumption, not a derived property of RLL.

materialized:
- candidate contract
- closure successor V2
- CLASS/CAMB successor V2
- executable gate
- regression tests
- CLASS/CAMB workflow integration
- equation-registry entries
- P0 status and documentation

expected_pass_state:
A1_1_NECESSARY_GATES_PASS_GAUGE_IC_OPEN

forbidden_promotion:
PERTURBATION_CLOSURE_RESOLVED
RLL_CLASS_CAMB_IMPLEMENTED
RLL_PHYSICAL_MODEL_CONFIRMED

rollback:
revert only this successor; preserve all predecessor and negative evidence.

F_next:
canonical CI -> gauge contract -> C01/C02 -> IC -> Bianchi/constraints -> transition regularity -> independent CLASS/CAMB.
