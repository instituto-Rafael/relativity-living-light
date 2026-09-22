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
