# RLL Dual Observation Window — coherence and counter-coherence V1

Status: ACTIVE_GOVERNED_DRAFT  
claim_allowed=false

## Scientific purpose

Keep evidence that improves and worsens a candidate model in the same auditable object. Do not turn all unexplained structure into noise, and do not turn structured residuals into new physics.

Core rule:

RESIDUAL != NOISE != CAUSE != NEW_PHYSICS.

The numerical gate compares candidate and baseline losses. Positive and negative evidence are stored separately. A hard falsifier remains blocking even when other windows improve.

## Observation operator

A generic measurement is treated as a composition of typed operators rather than a single undifferentiated 'photonic logistics' term:

O_obs = M_instrument o T_atmosphere o T_heliosphere o L_gravity [O_source] + background + residual.

Each operator is included only when physically applicable and sourced.

## Multiscale context vector

Candidate context channels include source variability, transit/occultation geometry, gravitational lensing, interstellar medium, solar wind, IMF, geomagnetic state, ionospheric TEC, solar zenith angle, ozone column, pressure, temperature, humidity/cloud/aerosol, pointing and detector state.

Axial precession is a long-timescale variable and must not be treated as a rapidly varying cause in an hourly or seasonal window. Seasons are primarily set by obliquity plus orbital position; precession modulates orbital-season geometry on approximately 23,000-year scales.

## Atmospheric and heliophysical corrections locked into the gate

1. Stratospheric ozone is the primary absorber of solar UV-C; UV-C is not mainly filtered by the ionosphere.
2. The thermosphere/ionosphere absorbs solar EUV and X-rays, which heat and ionize the upper atmosphere.
3. Thermospheric infrared cooling is strongly associated with NO near 5.3 micrometers and CO2 near 15 micrometers. The main atmospheric thermal-IR window is around 8-14 micrometers, centered near 10 micrometers. A generic 900-micrometer dominant cooling channel is not adopted.
4. Aurora is produced by energized particles/electrons interacting with upper-atmosphere oxygen and nitrogen after magnetospheric acceleration. Helium-3 exists in the solar wind, but aurora is not treated as a process that generates helium-3.
5. Cyclones are low-pressure rotating systems whose sense reverses between hemispheres through the Coriolis effect. Pressure systems are not reduced to a single solstice rule.

## What 'blinking' means

Ground-based stellar twinkling is primarily atmospheric scintillation/seeing. Solar-system planets usually twinkle much less because their finite angular disks average atmospheric cells.

Exoplanet transits are a distinct deterministic geometry: a planet crossing the stellar disk produces a repeatable dip in a light curve. Gravitational lensing, stellar intrinsic variability, transit geometry, atmospheric scintillation and instrument systematics therefore remain separate competing hypotheses.

## Residual entropy

Spectral entropy is a structure diagnostic only. Lower or higher residual entropy does not by itself establish order, syntropy, causality or a new physical sector. RAFAELIA-local 'negative syntropy' may be retained as a semantic label only if it is explicitly defined as a project diagnostic and never substituted for thermodynamic/Shannon entropy.

## Source anchors

- NASA: Milankovitch (Orbital) Cycles and Their Role in Earth's Climate — https://science.nasa.gov/science-research/earth-science/milankovitch-orbital-cycles-and-their-role-in-earths-climate/
- NASA: What’s a transit? — https://science.nasa.gov/exoplanets/whats-a-transit/
- NASA: Climate and Earth’s Energy Budget — https://science.nasa.gov/earth/earth-observatory/climate-and-earths-energy-budget/
- NOAA: Ionosphere — https://www.swpc.noaa.gov/phenomena/ionosphere
- NOAA: Solar EUV Irradiance — https://www.swpc.noaa.gov/phenomena/solar-euv-irradiance
- NOAA: Aurora — https://www.swpc.noaa.gov/phenomena/aurora
- NOAA/NESDIS: What Is the Coriolis Effect? — https://www.nesdis.noaa.gov/about/k-12-education/atmosphere/what-the-coriolis-effect
- NASA NTRS: Infrared Radiation in the Thermosphere Near the End of Solar Cycle 24 — https://ntrs.nasa.gov/citations/20200005243

## Cross-repository bridge

Matem-tica- defines Delta loss/support/opposition and entropy diagnostics. ChipQuantum provides a Q16 deterministic gate. RLL binds sourced observables, units, time windows, environmental covariates and falsifiers.

## Next gate

Bind a real observation vector with covariance, preregistered context channels, negative controls, injection/recovery and leave-one-instrument/time-window-out tests. Until then the mechanism remains TOKEN_VAZIO_MECHANISM.