# RLL Strong-Gravity Calibration Index — 2026-07-17

**Branch:** `agent/rll-operational-integration-house-20260717`  
**PR:** `#563`  
**Claim state:** `claim_allowed=false`

## Delivery order

1. `src/rll/strong_gravity_calibration.py`
2. `tests/test_strong_gravity_calibration.py`
3. `scripts/run_strong_gravity_calibration.py`
4. `results/strong_gravity_calibration/session_reference_sweep_20260717.json`
5. `data/registries/rll_strong_gravity_calibration_registry.json`
6. `docs/science/RLL_STRONG_GRAVITY_HEURISTIC_CALIBRATION_20260717.md`
7. `data/registries/rll_operational_integration_registry.json`
8. `.github/workflows/rll-structural-integration.yml`

## Implemented branch extension

```text
B08 strong-gravity magnetokinetic conversion
B09 gravitational-electrodissociative recurrent calibration
```

## Numerical anchors

```text
ideal-gas steam reference     1.6996519706 m³ per kg at 373.15 K / 1 atm
electron/proton FE/FG         2.2686614330e39
Q_T at Md/MBH=0.10            2.2360679775  (backreaction gate)
Q_T at Md/MBH=0.25            0.8944271910  (instability candidate)
T_orb at 20 rg, 10 Msun       0.0276813661 s
T_orb at 20 rg, 4.3e6 Msun    11902.9874443 s
```

## Verification

Local isolated execution:

```text
PYTHONPATH=src python -m pytest -q tests/test_strong_gravity_calibration.py
16 passed
```

GitHub Actions execution:

```text
Run structural and strong-gravity tests       success
Reproduce committed numeric calibration       success
```

The workflow runs the previous 16 structural tests plus the new 16 calibration tests and compares the regenerated JSON byte-for-byte with the committed result.

## Extension commit ledger

| Order | Commit | Function |
|---:|---|---|
| 1 | `c658d5f6bf3d909dc9892f2e207acd899ad8ea37` | unit-aware strong-gravity operators and recurrence |
| 2 | `5a86295df55f8a3797ff8029ac1fbe56dfe3449f` | 16 calibration and boundary tests |
| 3 | `f93b944ea3ebc8c79a99ab14c1e2bc1810d0e99d` | deterministic numerical runner |
| 4 | `7268680b96e7267f77cde528609b0f572f8a3905` | committed numerical sweep |
| 5 | `25d63be20e0348e0b56c94e5a7369fbfa72c91b9` | heuristic and artifact registry |
| 6 | `5fa2894d0c72734b08f4d3c8bcb3a4756cf84cb0` | scientific calibration documentation |
| 7 | `3aa1874dcfe3704317b3b24b1d81e8d99dc44a08` | initial delivery index |
| 8 | `c961e012e40dc7ebeba8cf79ae1b5ea5bb6a53fa` | B08/B09 operational integration |
| 9 | `9b8d31be943f7b73abd446bb8c14534902f5ba79` | combined tests and numerical reproduction CI |

This file is the final traceability commit for the extension.

## Epistemic boundary

The implementation formalizes and calibrates the session's analogies. It does not claim that atomic gravity dominates electromagnetic binding, that electrolysis literally occurs without an electrolyte/electrodes, that the reference ring is a GRMHD solution, or that an RLL-specific coupling has been detected.

`F_ok`: mechanisms, scales, recurrence, numerical anchors and CI are explicit.  
`F_gap`: source-specific fields, composition, cross sections, covariance and observational targets remain `TOKEN_VAZIO`.  
`F_next`: replace the reference ring with a declared self-gravitating GRMHD/GRPIC source manifest before fitting any physical parameter.

---

## Append-only successor — 2026-08-27

The historical B08/B09 calibration above is unchanged. A successor route is now registered instead of rewriting the July calibration:

```text
B10 black-hole thermodynamics + Mpemba-horizon falsifier
```

Canonical artifacts:

1. `data/pipelines/strong_gravity/mpemba_horizon_falsifier.py`
2. `data/contracts/mpemba_horizon_falsifier.v1.json`
3. `tests/strong_gravity/test_mpemba_horizon_falsifier.py`
4. `docs/RLL_MPEMBA_HORIZON_ATLAS.md`
5. `FALSIFIABILITY_PROTOCOL.md`
6. `provenance/receipts/rll_mpemba_horizon_atlas_20260827.json`
7. `provenance/receipts/rll_mpemba_horizon_drive_crosswalk_20260827.json`

Registry wiring:

- `data/registries/rll_operational_integration_registry.json` gains `B10_black_hole_thermodynamics_mpemba_falsifier` append-only.
- `data/registries/rll_strong_gravity_calibration_registry.json` retains H1–H8 and the committed July numeric result, and adds a `successor_extensions` entry.

Non-regression invariants:

```text
B00..B09 historical branch semantics remain present
H1..H8 historical strong-gravity heuristics remain present in order
results/strong_gravity_calibration/session_reference_sweep_20260717.json remains the committed July numeric result
raw_data_policy = immutable
claim_allowed = false
BH-MP-06 astrophysical Mpemba detection = TOKEN_VAZIO
BH-MP-08 direct astrophysical Hawking thermometry = TOKEN_VAZIO
```

The successor does not reinterpret the July numerical sweep as black-hole thermodynamics evidence. It adds a new falsification layer whose real-data promotion requires checksum-verified time series, preregistered distance/threshold, covariance, standard relaxation nulls, hold-out/look-elsewhere control and independent reproduction.
