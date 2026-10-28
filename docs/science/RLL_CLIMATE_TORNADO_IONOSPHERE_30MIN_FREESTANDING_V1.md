# RLL Climate × ionosphere × tornado: 30-minute freestanding falsifier V1

State: **EXPERIMENTAL / SYNTHETIC_ONLY / NO_OPERATIONAL_ALERT / claim_allowed=false**.
Producer: `native/climate_tornado_ionosphere/`; C11 source, no malloc, libc,
syscall, network access, floating-point math or dynamic allocations.

## Predecessors, no replacement
- `docs/science/RLL_CLIMATE_MULTIPHYSICS_CYCLE_V1.md` owns the 8×8 registry: column 2 atmospheric dynamics, column 6 ionosphere, column 7 extremes and verification.
- `data/climate/rll_climate_multiphysics_registry.v1.json` has the corresponding validity masks and seven normalised variables per sector.
- `scripts/rll_climate_engine_bridge.py` is the hosted HTTPS **external compute** adapter. It is NOT moved into C or treated as primary observation authority.
- `scripts/rll_climate_fibonacci_scheduler.py` is a cadence selector; it does not establish forecast skill.
- NOAA SWPC GloTEC, Kp, F10.7 and atmosphere data must be acquired and audited upstream; this C module only receives already-normalised timestamps and values.

## Scope and units
The evaluator accepts at most eight samples within a 30-minute *observation* window, in chronological order, with declared per-sample validity masks. No future observations are permitted. Radar rotation is a dimensionless pre-normalised 0–1000 diagnostic, **not** measured Doppler shear. TEC is a residual in 0.01 TECU units and must have a separate baseline. Kp is in 0.1 index units. All normalisation, time-zone reconciliation, source provenance, receipt, sensor delays and actual tornado labels belong to a separate hosted ingestion boundary.

The frozen exploratory decisions are: latest radar >=600 and previous >=400 for radar diagnostic; latest TEC >=0.30 TECU and TEC step >=0.20 TECU for a candidate ionospheric perturbation, vetoed when Kp>=5.0. **These are arbitrary software fixtures, not scientifically calibrated alert thresholds.** Combined diagnostic = logical AND, and `is_operational_warning` is always zero. `RLL30_OK` means input contract accepted; never `tornado detected`.

Missing data is not zero, invalid data is not missing, and a late TEC measurement is not a legitimate precursor. Missing Kp causes a data-gap state rather than a positive TEC inference. This does not remove confounding by F10.7, latitude, receiver mapping, solar terminator, season, thunderstorm gravity waves or GNSS geometry; those remain external scientific gates.

## Scientific context (research questions, not validated RLL results)
- Nishioka et al. (2013), DOI 10.1002/2013GL057963, reported ionospheric waves **1–2 hours after** the 20 May 2013 Moore tornado and attributed them primarily to supercells. Do not mistake a post-event disturbance for a pre-event tornado warning.
- Lu et al. (2024), DOI 10.1029/2024JA032854, modelled thunderstorm gravity-wave coupling to GNSS TEC; reported period ranges include roughly 15–30 minutes.
- Farges, Princelle and Astafyeva (2026), DOI 10.3389/fspas.2026.1893553, observed storm-related TIDs with periods approximately 13–39 minutes. This does NOT establish tornado-specific 30-minute predictive skill.
- NOAA SWPC explains that TEC responds to solar, geomagnetic and lower-atmosphere forcings: https://www.spaceweather.gov/phenomena/total-electron-content.

**Thirty-minute wave period != thirty-minute prediction lead != tornado lifetime.**

## Falsifier contract for independent real-data trials
1. Freeze upstream data versions (radar storm object, tornado ground truth, GNSS/TEC series, Kp, solar weather, observation and arrival timestamps) with SHA-256, spatial tiles and sampling cadence. Neither live provider compute result nor coarse metadata is ground truth.
2. Declare a forecast *issue* time; define outcome `0 < tornado_onset - issue <= 30 minutes`; no sensor with observation **or publication/availability** after issue time may enter predictors. Label event onset from independent verified events.
3. Compare radar-only weather baseline, radar+TEC, simple radar+noise, and matched non-tornadic supercells. Match Kp and non-tornadic thunderstorm gravity waves.
4. Split by storm/day/season/geography **before** selecting thresholds. Evaluate the same frozen test set and fixed acquisition budget. No random per-frame split from the same storm.
5. Quantify precision, recall, PR-AUC, calibration, missed tornadoes, false alarms per 100 observation hours, lead time conditional on true positives, and confidence intervals. Account for event rarity and multiple hypotheses.
6. Falsify with shuffled TEC by geomagnetic/local-time strata, offsets of +/-60 minutes, time reversal, ionosphere ablation, sensor dropout, delayed ingestion, geomagnetic storms, and counterexamples where TEC changes after tornado onset.
7. Promotion is denied absent incremental out-of-sample skill and independent replication; negative evidence is retained.

## Reproducible local checks
From repository root:

```sh
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic \
  native/climate_tornado_ionosphere/rll_climate_30min.c \
  tests/c/test_rll_climate_30min_native.c -o /tmp/rll30test && /tmp/rll30test
python3 -m unittest -v tests.test_rll_climate_30min_freestanding
```

The Python wrapper uses only stdlib plus an installed C compiler, and automatically participates in existing `python-tests.yml` pytest discovery (no new YML). On ARM32/AArch64 it compiles freestanding objects and checks undefined symbols; **cross-compilation does not constitute execution on a real Android device**.

Receipt class: `SYNTHETIC_CODE_VALIDATION`. All historical/out-of-sample tornado prediction skill, real TEC/cross-planet correlation, latency and independent validation are `TOKEN_VAZIO_UNMEASURED`. `PROMOTION=HOLD`, `claim_allowed=false`, `ROLLBACK=delete candidate branch; original climate patch unchanged`. Do not issue safety alerts from this experiment.

## S1: 8×8 freestanding structural adapter

The separate `rll_climate_8x8.h/.c` core preserves the full 64-cell storage contract (eight sector gates + 56 physical coordinates) as signed Q16.16 values with an eight-bit gate mask and seven-bit physical mask per sector. It returns explicit `RLL8_INCOMPLETE` if any gate or physical coordinate is absent; zero is a valid measured value only if its bit is valid. Outputs include counts of valid and missing coordinates and the number of normalized |z|≥3 candidates. No physiological/meteorological alarm is inferred, and `is_operational_warning=0` is forced.

**Scope boundary:** this is a structural/validity port of the registry matrix; it is NOT a port of the full Python H7/Poincaré lift, Fibonacci scheduling policy, network ingest, physical sensor models, or event-by-event tornado classifier. No data-level performance is claimed.

Test entrypoints: `tests/c/test_rll_climate_8x8_native.c` and the existing `tests/test_rll_climate_30min_freestanding.py`. Host native ABI and both ARM freestanding objects are included in the same CI wrapper; no additional YAML.

## S2: apparent movement of ionospheric TEC disturbances

`rll_tec_phase.h/.c` estimates an integer *apparent* phase speed from two **already-projected** GNSS station observations, if separation (1–500 km) and positive arrival lag (1–60 min) are independently measured and provenance-validated. The test vector 100 km / 10 min gives integer 166 m/s; 60 km / 10 min gives 100 m/s. The 32-step unsigned division avoids hidden ARM32 `__aeabi_uidiv` dependencies, with deliberately bounded input.

This is not an estimate of tornado position, vortex motion, wave direction or causality. Two stations cannot uniquely reconstruct a 2-D wavefront direction; at least three geometrically suitable receivers and propagation analysis are required. A 30-min TID period, observation window and forecast lead time remain separate. The code returns a diagnostic with `is_tornado_predictor=0` and `direction_identifiable=0`. Case-driven observational phase-speed inference remains `TOKEN_VAZIO_REAL_GNSS_TEC`.
