# μWRITE — RLL P0 C07/C08 Regular-Variable Preflight — 2026-09-22

State: CANONICAL_PR_INTAKE / CI_PENDING / CLAIM_BLOCKED

μID=RLL-PERTURB-C07-C08-REGULAR-20260922-V1

parent_candidate=A1_1_CONSERVED_CS2REST_1_Q0_SIGMA0
parent_evidence=A1.1 necessary gates 9/9 PASS

declared_primary_variables:
- delta_rho_s
- q_s=(rho_s+p_s)*theta_s

derived_only_when_conditioned:
- theta_s=q_s/(rho_s+p_s)

exact_background_identity:
rho_s+p_s=-(1/3)d rho_s/dln(a)

forbidden_regularization:
- naked unproved division by 1+w_s
- epsilon clipping that changes the mathematical model

open_tokens:
- TOKEN_VAZIO_C01_DELTA_RHO_EVOLUTION
- TOKEN_VAZIO_C02_Q_EVOLUTION
- TOKEN_VAZIO_CLASS_CAMB_GAUGE_MAPPING
- TOKEN_VAZIO_SUPERHORIZON_IC
- TOKEN_VAZIO_ENTHALPY_DEGENERACY_LIMIT
- TOKEN_VAZIO_PERTURBED_CONSTRAINT_GATE

external_governance:
- PR #955 remains blocked above lab maturity
- active default-branch ruleset observed
- branch-protection endpoint authority unavailable to integration (403)
- no bypass

claim_allowed=false
token_resolution=NOT_RESOLVED
class_camb_unlock=false

F_next: canonical CI -> derive C01/C02 in regular variables -> analytic limit -> IC -> gauge mappings -> Bianchi/constraint gates.


## Canonical CI R1 — preserved harness failure

run_id=35721226047
job_id=106724347532
focused_tests=15_PASS
A0=FALSIFIED_AS_GLOBAL_DEFAULT_0_OF_9
A1_1=NECESSARY_GATES_PASS_9_OF_9

C07_C08_workflow_conclusion=FAIL
failure_class=DIRECT_SCRIPT_IMPORT_PATH
failure=ModuleNotFoundError: No module named 'tools'

interpretation:
The failure occurred before the C07/C08 executable preflight could run as a direct script.
Pytest import-mode passed because the repository root was already importable.
The later missing CLASS/CAMB/CMB receipts were cascade failures after this abort, not new backend evidence.

correction:
- make the preflight insert the repository root into sys.path when executed directly;
- add a regression that invokes the exact CLI form used by the workflow.

scientific_state_after_R1:
TOKEN_VAZIO / NOT_RESOLVED
No C07/C08 PASS is claimed from R1.
