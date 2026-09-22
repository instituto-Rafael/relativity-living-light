# μWRITE — RLL A1.2 Gauge Regularization — 2026-09-22

State: CANONICAL_PR_INTAKE / CI_PENDING / CLAIM_BLOCKED

μID=RLL-PERTURB-A1-GAUGE-REG-20260922-V1

parent:
- A1.1 necessary-condition candidate
- RLL_PERTURBATION_CLOSURE_SUCCESSOR_20260922_V2

delta:
- conformal-Newtonian analytic reference frozen
- U_s=(1+w_s)theta_s introduced
- C01 delta equation candidate materialized
- C02 momentum equation candidate materialized in U_s
- q_w and c_a^2 regularity diagnostics executable
- stiffness preserved instead of hidden by epsilon clipping

forbidden:
- treating gauge choice as unique physical law
- inventing super-horizon initial conditions
- unlocking CLASS/CAMB from algebra alone
- classifying numerical stiffness as physical refutation without solver evidence

expected_ci_state:
A1_2_GAUGE_VARIABLE_REGULARIZATION_PASS_IC_OPEN

token_resolution:
NOT_RESOLVED

rollback:
revert only A1.2 successor; A1.1 9/9 evidence remains.

F_next:
CI -> IC derivation -> independent CLASS/CAMB maps -> Bianchi/constraints -> full integration.
