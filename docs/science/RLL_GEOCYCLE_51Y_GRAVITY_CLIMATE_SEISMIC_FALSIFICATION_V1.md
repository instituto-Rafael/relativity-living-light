# RLL Ω — Solar-System Gravity / Climate / Seismic 51-Year Falsifiability V1

**State:** source catalog + freestanding negative-screen implementation; real-series ingestion **NOT EXECUTED**. `claim_allowed=false`, `PROMOTION=HOLD`. Scope: 1975-01-01 through 2025-12-31 is a complete **51 civil-year observation window**, not proof of a 51-year cycle. 2026 partial observations must remain a separately frozen holdout.

## Source inheritance and the competing 52-year hypothesis

- Existing RLL `docs/science/RLL_CLIMATE_MULTIPHYSICS_CYCLE_V1.md`: 8x8, sector 0 ephemeris/tides/geodetic, 1 barometric/thermodynamics, 2 atmosphere/dynamics, 6 ionosphere, 7 extreme exposure/verification. No parent file modified.
- Existing `docs/hipoteses/HIPOTESES_GEOFISICAS_RAFAELIA.md` already proposes a *different* ~52-year hypothesis associated with the Mesoamerican Calendar Round: Tzolk'in 260 days and Haab' 365 days have common multiple 18,980 days = 52 Haab' cycles. A calendrical 52-year cycle does NOT establish a 51- or 52-year planetary gravitational recurrence. Original materials and cultural provenance are preserved; cross-cultural historical transmission is not inferred.
- Existing `data/contracts/rll_climate_juno_shadow.v1.json` separates Juno imagery from Earth atmospheric datasets and explicitly forbids direct physical equivalence.

## Physical model and falsification gate

1. NASA JPL Horizons should supply 3D position and velocity vectors with correct center/frame/time scale; independently check barycenter/geocenter conventions, light-time corrections, TT/TDB vs UTC and leap seconds. Earth's gravity is not one field held fixed for 51 years.
2. Each mass creates an acceleration at the receiver of order `G*M/r²`. For geophysical differential deformation/earth/ocean tide tests, compute the **tidal tensor** `T_ij=Σ GM(3 r_i r_j/r⁵ - δ_ij/r³)` from source positions **relative to Earth**, not the direct scalar acceleration. Require physical units, error bars, distance and mass provenance; Moon/Sun are principal Earth tides, planetary tide contributions must be reported on their actual tiny scale.
3. Physical cycles to compare against any proposed 51y residual: daily/annual seasonal harmonics, 8.85y lunar apsidal, 18.6y lunar nodal, 11.86y Jupiter, ~29.45y Saturn, ~19.86y Jupiter-Saturn synodic conjunction, interannual ocean/atmospheric oscillations (NAO/ENSO), solar activity ~11y, anthropogenic and instrument trends. Earth's axial obliquity ~23.4°; precession period ~26,000 years, not 51.
4. **Do not compute one grand correlation across everything**. Maintain source → observation → physical response → testable target. Atmospheric thermodynamic variability can dominate a rainfall hazard independently of tiny planetary tidal terms. Japan earthquake timing is dominated by plate/fault stresses; the existence of tidal modulation in selected settings is not a reliable earthquake prediction.
5. The phrase “syntropy” is user exploratory vocabulary, not a numerically established thermodynamic observable. Operational information metrics must be declared (Shannon entropy of binned state transitions, permutation entropy, autocorrelation, forecast residual predictability or physical entropy production as different dimensional quantities). Bin choices, sensors and missingness may create an artificial entropy cycle.

## Historical case families (different mechanisms)

**Japan, Kanto/Tokyo:** JMA earthquake catalog since 1919; magnitude, depth, fault mechanism, latitude/longitude, origin time and precision. Separate historic maps, tectonic changes, subsidence, land reclamation, earthquake shaking damage, and the administrative history of Edo/Tokyo. A city moving by reclamation is not plate displacement. Background comparisons include season, plate class, magnitude completeness and chance alignments with lunar phase. Do not invent a causal 51-year period.

**UK/North Sea:** The Icelandic Low/Azores High and NAO change storm trajectories. Model storm surge as astronomical tide + wind setup + inverse-barometer response + coastal morphology + river runoff + observed residual, with time-aligned gauge datum. A near-static -1 hPa pressure anomaly gives approximately +1 cm of local sea-surface elevation, not a universal flooding rule. The 1953 North Sea flood is a well-known *external historic case* outside the 1975–2025 estimation window. BODC/NTSLF records are station-dependent and may require registration.

**Global climate:** ERA5 from 1940 (hourly global model/reanalysis 3D winds T dewpoint/specific humidity P clouds/upper air); pressure solar S2 tide near ~10/22 local solar time in tropical average, typically lower near ~4/16; do not confuse with tides due Moon alone. Environmental lapse near ~6.5 K/km in a standard atmosphere, dry adiabatic ~9.8 K/km, moist variable; solar incidence varies with latitude/season, cannot be reduced to a timezone. Ocean heats/cools differently due heat capacity and mixing; evaporation cools when latent heat is removed from the local surface, but cooling/evaporation are not equivalent identities.

**Jupiter/Juno:** Jupiter's Great Red Spot/cloud bands are independent studies of rotating/fluid convection and observations from Juno since the 2010s. Jupiter cloud photographs do not provide an Earth's gravitational tidal tensor or 51 years of Juno data. Juno Earth's-climate comparison only through typed nondimensional dynamics, no direct physical transfer without matched quantities.

## Source contract

`data/climate/rll_gravity_climate_51y_source_registry.v1.json` lists authorities and **only pointers**. No JPL, ERA5, JMA, BODC, NASA Landsat, or Juno dataset bytes have been downloaded in this delta. Source records are `TOKEN_VAZIO_RAW_*`. Do not issue a source SHA-256 receipt without actual bytes.

The 1975–2025 window cannot exhibit two independent observations separated by 51 years within the closed bounds: minimum pair difference requires >51 years. Even 102 years is at best 2 period lengths. A three-period screening interval requires at least 153 years of consistent sampling; **this is necessary for the software's conservative screen, not sufficient for statistical inference**. JMA and ERA5 archives do not individually span three 51-year cycles. The correct state is `TOKEN_VAZIO_UNIDENTIFIABLE` for the cross-domain 51y claim.

## Freestanding C11 screening, no oracle

`native/geocycle_51y/rll_geocycle_falsifier.{h,c}` operates on a fixed capacity of 256 **annual normalized** values and explicit validity mask. It checks candidate lags 2–70y. Rejects malformed data, under-three-period windows, absent paired coverage >=20%, and constant signals. Returns an **arithmetic mean lag difference** for diagnostic comparisons only; does not estimate significance or classify earthquakes/weather. No libc, heap, syscalls, FPU, dynamic memory. 4096 mutation vectors and negative 50/51/52 years in `tests/c/test_rll_geocycle_51y_native.c`. Python stdlib wrapper compiles host executable and ARM32/ARM64 freestanding objects in existing `python-tests.yml`, no new workflow. ARM cross-compile ≠ physical Android execution.

## Next experiment and preregistered falsifiers

- Freeze period discovery set; compare 51 against 50,52 and known physical periods with a red-noise/AR(1), block-bootstrap and time-shuffled null, control false discovery rate across domains, regions and parameter scans.
- Pre-register observational response variables (e.g., monthly pressure residual after solar S1/S2 + synoptic subtraction, tide gauge non-astronomical residual, wind gradients and storm reports; quake log rate stratified by magnitude completeness and plate regime).
- Use all 51y earth-weather data *for descriptive baseline only*, and long ephemeris reconstruction (multiple centuries) separately to test whether the **celestial state itself** nearly repeats after 51y. Then test a restricted physically justified tide predictor in independent events.
- Decompose secular change, autocorrelation, instrument drift, urban land reclamation, calendar reforms and sampling gaps. Limit “repeated pattern” to preregistered confidence interval and replication across time, not image resemblances.
- For each result retain `F_ok`, `F_gap`, `F_next`, hashes, UTC issue timestamps, geographic coordinates/data datum and rollback path.
- Safety: study does not constitute earthquake, flood, tornado or storm warnings.

## Authoritative source documentation

JPL Horizons https://ssd-api.jpl.nasa.gov/doc/horizons.html
ERA5 https://www.ecmwf.int/en/forecasts/datasets/complete-era5-global-atmospheric-reanalysis
Japan JMA https://www.data.jma.go.jp/eqev/data/index.html
UK BODC https://www.bodc.ac.uk/data/hosted_data_systems/sea_level/uk_tide_gauge_network/
UK Met Office NAO https://www.metoffice.gov.uk/research/climate/seasonal-to-decadal/gpc-outlooks/ens-mean/nao-description
NASA Landsat https://science.nasa.gov/mission/landsat/data-overview/
NASA Juno https://science.nasa.gov/gallery/junocam-images/
NASA lunar tides https://science.nasa.gov/moon/tides/
NASA axial precession https://science.nasa.gov/learn/basics-of-space-flight/chapter2-1/
NOAA pressure tide https://prod-01-alb-www-noaa.woc.noaa.gov/jetstream/atmosphere/air-pressure

**F_ok:** source/terminology mapping, fail-closed C screening and tests specified. **F_gap:** real ephemeris vectors, century-scale comparable atmospheric/tectonic series, density/phase calibration, statistical significance, fieldwork, test-arm hardware. **F_next:** ingest one modest verifiable authoritative period and hash bytes first, then compare against pre-registered null hypotheses. **PROMOTION=HOLD**.
