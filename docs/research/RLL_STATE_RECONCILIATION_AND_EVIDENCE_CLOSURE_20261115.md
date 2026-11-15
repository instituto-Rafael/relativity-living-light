# RLL state reconciliation and evidence closure — 2026-11-15

State: `IMPLEMENTED_UNTESTED` until CI. `claim_allowed=false`.

## Corrected operational fact

Live GitHub readback shows PR 1172 and PR 1173 are merged. Earlier `DRAFT/HOLD` descriptions are retained as historical observations and superseded only for current PR state. Merge establishes code integration, not scientific validity.

## Fail-closed boundary

The machine-readable contract binds PR numbers, head SHAs, merge SHAs and source URLs. The gate rejects state drift, hash drift, source drift, missing falsifiers and any unsupported promotion of a scientific gate.

Open gates remain typed: same-likelihood reconciliation; official covariance validation; independent reproduction; full CMB TT/TE/EE/lensing; nonlinear P(k); physical-model validation. Missing evidence is not zero and is not inferred from a successful merge.

## Execution

```sh
python3 -m unittest discover -s tests -p 'test_rll_state_reconciliation_gate_v1.py' -v
python3 tools/ci/rll_state_reconciliation_gate_v1.py --output artifacts/python-tests/rll_state_reconciliation_gate_v1.json
```

Expected local scope: seven tests and `PASS_SCOPED_STATE_RECONCILIATION`. This does not authorize a global RLL claim, release or merge.

## Academic falsifier order

1. Freeze one dataset/release/selection/covariance/likelihood/prior contract for all models.
2. Hash every input and bind executable, environment, seed and parameter count.
3. Run ΛCDM, wCDM, CPL and RLL under the same likelihood and nuisance treatment.
4. Reject preference claims if matched reruns reverse the claimed direction, fail calibration or reveal leakage/post-hoc tuning.
5. Require independent reproduction before cross-host promotion.

Rollback: revert only this additive package. Preserve historical receipts.
