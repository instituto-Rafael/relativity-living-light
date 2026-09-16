# RLL METAR Earth Field V1

**Status:** governed diagnostic field.  
**claim_allowed:** `false`

## Purpose

Create the first Earth-surface meteorological vector field in the RLL climate path from bounded, geolocated METAR point observations.

The source route is:

```text
NOAA/NWS Aviation Weather Center METAR
        ↓
latest observation per ICAO station
        ↓
typed T / pressure / wind
        ↓
wind direction+speed → eastward u / northward v
        ↓
IDW spatial interpolation
        ↓
finite-difference diagnostics
        ↓
JSON + CSV + SVG + SHA-256 receipt
```

## What it is

The field materializes:

- temperature [°C];
- pressure [hPa];
- eastward and northward wind components [m/s];
- wind speed [m/s];
- horizontal pressure-gradient components [Pa/m];
- horizontal divergence [1/s];
- vertical component of relative vorticity [1/s].

The wind convention is meteorological: the reported direction is where wind comes **from**.

## What it is not

```text
METAR_POINT_OBSERVATIONS
!= COMPLETE_ATMOSPHERIC_STATE
!= DATA_ASSIMILATION
!= CFD
!= NUMERICAL_WEATHER_PREDICTION
```

Inverse-distance weighting is deliberately simple and auditable. Its purpose is a physical visualization surface and a diagnostic bridge, not a claim that sparse airport observations reproduce the full terrestrial flow.

## Provider provenance

The live workflow uses the public NOAA/NWS Aviation Weather Center Data API:

```text
https://aviationweather.gov/api/data/metar
```

with bounded station IDs, `format=json`, and a short hour window. No API secret is required.

Provider documentation states that METAR terminal observations are worldwide and that the API is rate limited. The workflow uses one bounded request.

## Physical diagnostics

For a local horizontal field `u(x,y), v(x,y)`:

```text
divergence = du/dx + dv/dy
vorticity_z = dv/dx - du/dy
grad(P) = (dP/dx, dP/dy)
```

Distances use a local equirectangular Earth approximation. Derivatives are finite differences on the interpolated grid.

## Artifacts

A successful run writes:

```text
metar_observations.normalized.json
earth_surface_field.json
earth_surface_field.csv
earth_surface_field.svg
receipt.json
```

The SVG is a wind-vector diagnostic. The JSON/CSV preserve the numerical field. The receipt binds source mode, station set, observation-time range, grid geometry, method, and SHA-256 for every derived artifact.

## Climate Engine relation

Climate Engine stays a separate provider path. This METAR field is not silently fused with GRIDMET or another raster product.

The controlled next step is:

```text
METAR field
        +
Climate Engine field with declared dataset/variable/time/units
        ↓
co-registration
        ↓
same-quantity residuals / normalized diagnostics
        ↓
comparison receipt
```

Only after source, time, unit, scale, and uncertainty alignment may a comparison be interpreted. A residual is not a cause.

## Jupiter / Juno relation

The METAR field can contribute Earth-side descriptors such as vorticity, divergence, gradients, characteristic speed, length and time scales. Juno observations remain an independent planetary source.

```text
similar morphology != identical mechanism
```

Cross-planet work therefore remains a comparison shadow until explicit dimensionless scales, uncertainties, alternative mechanisms, and falsifiers are declared.
