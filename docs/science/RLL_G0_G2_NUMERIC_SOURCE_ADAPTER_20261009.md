# RLL: G0/G1/G2 numeric successor (2026-10-09)

State: `IMPLEMENTED_UNTESTED_CI`, `claim_allowed=false`. Parent: merged PR #1086.

**No scientific model, priors, archive or NOVOexport raw conversations have been changed.** This change adds a source-bound *diagnostic only*. Source mismatch returns `TOKEN_VAZIO_SOURCE_DRIFT`.

## Questions under test

- **G0:** evaluate `joint.hz_from_e2(z=0)` using archived model fit parameters. `H(z=0) / fitted_H0 != 1` is a physical-convention question, not automatically a code defect.
- **G1:** compare the joint's drag-horizon acoustic scale with a fiducial smooth-background acoustic integral to `z*=1089.92`. This is *not* a full recombination calculation. Boltzmann/Planck prior verification remains `TOKEN_VAZIO_NOT_RUN`.
- **G2:** compare `joint.fsigma8_prediction` against the repository's existing `check_rll_growth.integrate_growth` smooth-ΛCDM GR ODE control, using a matched fiducial matter fraction and explicit radiation difference. This is not an RLL perturbation solver.
- **G3/G4:** preserve the null `Os0=0` boundary and BIC-versus-historical-label contradiction as observations rather than silently rewriting history.

## Execution

```sh
python -m pytest -q tests/test_rll_joint_g0_g2_adapter.py
python scripts/rll_joint_g0_g2_adapter.py --output /tmp/rll_joint_g0_g2_diagnostic.json
```

The optional receipt includes source and archived-file SHA-256 and never overwrites those inputs. If the source formula moves, the guard blocks until a new reviewed contract is published. The code uses existing NumPy/SciPy already required by the joint likelihood; this adapter is *not* a new freestanding L0 core. RafPolimata Geometry21 remains a separate zero-runtime numerical study.

Scope remains `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`. Local independent control (six tests in a separate stdlib-only probe) is context, not proof that this exact repository test was run.

F_ok: repository G0/G1/G2 adapter authored on a governed feature branch. F_gap: exact-head CI, independent CLASS/CAMB recombination and growth, refit with matching priors, physical interpretability and P0 rights review. F_next: exact HEAD tests + compare with existing growth/CAMB scripts. Rollback: revert three new files only. No provider settings modified.
