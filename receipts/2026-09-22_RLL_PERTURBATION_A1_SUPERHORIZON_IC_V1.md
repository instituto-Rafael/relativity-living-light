# μWRITE — RLL A1.2 PASS → A1.3 Superhorizon IC Intake — 2026-09-22

State: A1_2_MERGED / A1_3_CANDIDATE_CI_PENDING / CLAIM_BLOCKED

μID=RLL-PERTURB-A1-SUPERHORIZON-20260922-V1

A1_2_authority:
- PR #957
- merge_commit: 6c451eedc704fdd54beee2e13e954473eee7c074
- canonical_run: 35721844002
- state: A1_2_GAUGE_VARIABLE_REGULARIZATION_PASS_IC_OPEN
- passing_cases: 9/9
- stiffness: LOW=5 MODERATE=3 HIGH=1
- high_case: zt=10, wt=0.05
- token_resolution: NOT_RESOLVED
- class_camb_unlock: false

preserved_negative_history:
- first A1.2 workflow run failed before execution due direct-CLI import path
- failure receipt remains: receipts/2026-09-22_RLL_PERTURBATION_A1_GAUGE_CLI_FIX_V1.md
- equations were not changed by that repair

A1_3_delta:
- asymptotic w_s,q_w,c_a^2 -> 0 typed
- x=k tau reduced reference system frozen
- exact rational recurrence materialized
- leading local IC coefficients d0=-3/2 and v1=1/2
- higher-order frozen-potential coefficients explicitly conditional
- direct CLI regression included

forbidden:
- calling the local frozen-potential series a full cosmological IC
- ignoring neutrino anisotropic stress
- assuming CLASS/CAMB gauge maps
- unlocking the perturbation backend from A1.3 alone

expected_state:
A1_3_COMPONENT_LOCAL_SUPERHORIZON_SERIES_PASS_COUPLED_IC_OPEN

rollback:
revert only A1.3 intake; A1.2 merged evidence remains immutable.

F_next:
CI -> coupled radiation/neutrino metric IC -> independent solver maps -> constraints -> integration.
