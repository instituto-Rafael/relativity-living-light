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

## S3: air-mass stability, vapor density and convection — primary investigation axis

**Research axis revised:** the target is the evolving stability/mass transport of the *lower atmosphere*: pressure, temperature, moisture, density, buoyancy, vertical profile and wind-vector shear. Ionopheric TEC is an *optional cross-layer consequence/control* and must not be called the mechanism that creates tornadoes. The 8x8 registry already contains sectors 1 (thermodynamics), 2 (dynamics), 6 (ionosphere), 7 (extremes).

The freestanding `rll_air_mass.{h,c}` is a gas-phase Q-format/integer **equation-of-state and dry-screen building block**, not a numerical weather prediction model. It includes:
- validated pressure (Pa), temperature (centikelvin), water vapor mole/volume fraction (parts per million, 0..40000), phase state and validity mask (missing is not zero);
- moist-air and dry-air density (mg/m³), virtual temperature and water vapor mass fraction (parts per million by **mass**);
- same-pressure parcel buoyancy (milli-m/s²), including the density effect of vapor;
- approximate unsaturated screening of environmental vertical thermal stratification relative to the dry adiabatic lapse (~9.8 K/km); NOT full moist static stability, Brunt-Väisälä N², CAPE or CIN.

For a gas-only ideal mixture under equal pressure and temperature:

```text
x_v = e / P                             water vapor mole fraction (volume fraction)
rho = (P - e)/(R_d T) + e/(R_v T)
rho/rho_dry ≈ 1 - 0.378 x_v
T_virtual = T/(1 - 0.378 x_v)
q_mass ≈ (0.622 x_v)/(1 - 0.378 x_v)
buoyancy = g*(rho_environment - rho_parcel)/rho_environment
hydrostatic: dp/dz = -rho*g              NOT solved in this kernel
mass transport: rho * wind_velocity     NOT solved in this kernel
```

At `P=101325 Pa`, `T=303.15 K`, `x_v=0.04`, the fixed-point kernel yields dry 1.164398 kg/m³, moist 1.146792 kg/m³, virtual temperature 307.80 K and vapor mass fraction 0.025261. The density reduction is ~1.512% relative to the same-P,T dry mixture. **4% is an approximate high tropical atmospheric water-vapor fraction by volume, not a global constant and not 4% by mass.** Moist air is lighter *as a gas mixture* at fixed P/T. Cloud droplets, ice and rain add condensate loading; condensation also releases latent heat. The current kernel refuses those phase states rather than silently giving a wrong result.

The simple two-layer dry-screen assumes input height separation ≥100 m, vapor-only ideal air, and compares a finite-difference virtual temperature lapse to 9.8 K/km. It is a **diagnostic under restricted assumptions**, not a cloud-bearing-layer stability classification. Never infer tornado occurrence from its sign.

Upstream credible measurements must be station/radiosonde/sounding P,T,Td/RH plus height, radar reflectivity/velocity, wind u/v at multiple heights, Kp/F10.7 and optional GNSS TEC; each sample requires observation timestamp, *available-as-of* timestamp, location, altitude, units, calibration and source hash. Without vapor observed and time-aligned, use `RLLA_MISSING`, not assumed 4%.

Future falsifiers: vapor density monotonic at fixed P/T; mass-vs-volume fraction confusion; condensate rejection; wrong-pressure buoyancy comparisons; dry/mixed/fully saturated vertical-profile counterexamples; CAPE/CIN and vertical shear comparisons against Skew-T and conventional nowcast; sensitivity to terrain, boundary-layer entrainment, pressure gradients and downward precipitation loading. If full thermodynamic equations and moisture transport do not improve held-out storm reconstruction, reject the RLL-specific add-on for that test set.

Authorities: NOAA JetStream *The Atmosphere* (water vapor up to ~4% by volume, not constant) https://www.noaa.gov/jetstream/atmosphere ; NOAA *Parcel Theory* https://www.noaa.gov/jetstream/upperair/parcel-theory ; AMS Glossary *Virtual Temperature* https://glossary.ametsoc.org/wiki/virtual-temperature/ ; NOAA *Severe Weather* https://www.noaa.gov/jetstream/upperair/severe-weather . No dataset from these references was ingested as sensor observations.

Local pure-C tests: `tests/c/test_rll_air_mass_native.c` includes 40,001 vapor-volume levels, fixed dry/moist density vectors, parcel sign reversal, phase/missing-data checks, and stable/neutral/unstable *dry screens*. GCC/Clang+ASan/UBSan host tested, Clang ARMv7/AArch64 object undefined symbols=0. The existing Python tests/CI are responsible for exact head reproducibility. Still missing the actual physical wind/continuity/momentum solver, latent heat/rain, true moist stability, storm-wise historical dataset, and real tornado forecast validation.

**PROMOTION=HOLD, claim_allowed=false, is_weather_warning=0**. No authority for public warnings.
