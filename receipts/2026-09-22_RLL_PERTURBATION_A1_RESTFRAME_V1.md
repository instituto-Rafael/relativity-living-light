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

## Canonical execution closure — rll/lab intake

evidence_head=c5e1271f515e651b6915e1da532a24dd2d1f6fa4
canonical_lab_merge=bc5c51efeba992e232148b65b3695a94cf5bbcd5

CLASS_CAMB_A1_RUN=35698287683
CLASS_CAMB_A1_CONCLUSION=SUCCESS
A1_1_STATE=A1_1_NECESSARY_GATES_PASS_GAUGE_IC_OPEN
A1_1_PASSING_CASES=9/9
token_resolution=NOT_RESOLVED
class_camb_unlock=false
claim_allowed=false

CLASS_CAMB_A1_ARTIFACT=10681302686
CLASS_CAMB_A1_ARTIFACT_SHA256=f67bc37621243394f58291dd6ac8798138eba5da726e9508af817616aaa661b9

PYTHON_FULL_SUITE_RUN=35698287778
PYTHON_FULL_SUITE_CONCLUSION=SUCCESS
PYTHON_ARTIFACT=10680928751
PYTHON_ARTIFACT_SHA256=42ee709732982e2dde3328606a92c55e616ddc696004e588c653bd7afc1efdb5

governance:
- Branch Maturity run 35698287695: SUCCESS
- Transit Tower run 35698287696: SUCCESS
- YAML Deep Audit run 35698287707: SUCCESS
- Workflow Architecture run 35698287823: SUCCESS
- Workflow Contract run 35698287734: SUCCESS
- Workflow Contract V2 run 35698288033: SUCCESS
- Platform Assurance run 35698287678: SUCCESS
- Platform Assurance V2 run 35698287755: SUCCESS

preserved_negative_evidence:
- A0 remains FALSIFIED_AS_GLOBAL_DEFAULT with 0/9 passing cases.

remaining_hard_blockers:
- C01_DELTA_S_FULL_EVOLUTION
- C02_THETA_S_FULL_EVOLUTION
- C07_GAUGE_AND_INITIAL_CONDITIONS
- C08_PERTURBATION_TRANSITION_REGULARITY
- CONSTRAINT_BIANCHI_RESIDUAL
- TOKEN_VAZIO_RLL_CLASS_CAMB_IMPLEMENTATION

interpretation:
A1.1 survives the declared necessary-condition sweep only. This execution does not resolve the full perturbation closure, does not validate c_s,rest^2=1 as an RLL property, and does not authorize RLL CLASS/CAMB outputs or observational claims.

next_gate:
regularize the momentum variable near 1+w -> 0 without arbitrary epsilon; freeze a gauge convention; derive C01/C02 plus super-horizon initial conditions; then execute constraint/Bianchi and transition-regularity gates.
