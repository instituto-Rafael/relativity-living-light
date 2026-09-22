# RLL Climate Engine × Juno — Comparative Shadow V1

**Status:** implementation/observation routing; **not** a physical equivalence claim.  
**claim_allowed:** `false`

## Purpose

Place the already-authorized Climate Engine path inside the governed RLL real-data orchestration and prepare a second, independent observational surface for NASA Juno/Jupiter.

The comparison is:

```text
Climate Engine (Earth external compute product)
        |
        v
typed quantities + units + uncertainty
        |
        +------------------+
                           |
NASA/Juno observations ---+--> comparison shadow --> model competition
                                |
                                +--> claim_allowed=false
```

The Earth provider is never relabeled as a Jovian sensor.

## Existing credential boundary

The RLL workflow binds:

```text
GitHub Actions secret: CLIMA
        -> runtime only
CLIMATE_ENGINE_API_KEY
```

The secret value, length and hash are forbidden from receipts and artifacts. SHA-256 applies to provider responses and receipts, not to the API key.

## Why Jupiter is scientifically useful here

Juno gives multiple non-equivalent observation channels:

1. **Visible morphology and cyclone tracking — JunoCam.**
2. **Infrared thermal and auroral output — JIRAM.**
3. **Microwave emission and storm depth — MWR.**
4. **Radio occultation — temperature/density structure.**
5. **Particle/field and auroral measurements.**
6. **Optical/electrical lightning observations.**

Therefore "light leaving Jupiter" is not one mechanism:

```text
thermal IR != auroral emission != lightning != microwave emission
```

NASA/JIRAM explicitly maps thermal emission near 4.8 um and auroral emission near 3.45 um. Juno also detected shallow lightning associated with ammonia-water clouds. The 2025 polar-cyclone analysis reports beta drift, mutual cyclone interaction, oscillation and slow westward drift.

## Metallic hydrogen boundary

The deep interior is modeled as containing electrically conducting liquid metallic hydrogen under extreme pressure, associated with Jupiter's magnetic dynamo. This is scientifically relevant to the magnetic environment, but this project must not jump directly from:

```text
metallic hydrogen -> magnetic field -> polar cyclone geometry
```

without an explicit coupled interior/magnetosphere/atmosphere model and observables.

## First comparison axes

The safe first pass is not "Earth hurricane = Jupiter cyclone." It is to compare typed descriptors:

- temperature gradients;
- wind/vortex tracking;
- vertical structure;
- radiative channels;
- electrical-discharge observations;
- characteristic length/time scales;
- dimensionless diagnostics only after scales are declared.

Potential future diagnostics include Rossby-number-like, vorticity and spectral/temporal measures, but only when each input has units, source, scale and uncertainty.

## Sources

- NASA/JPL, Juno polar cyclones and radio occultation (2025): https://www.nasa.gov/missions/juno/nasas-juno-mission-gets-under-jupiters-and-ios-surface/
- NASA Science, JIRAM infrared glow: https://science.nasa.gov/photojournal/juno-captures-jupiters-glow-in-infrared-light/
- NASA Science, polar cyclone multi-instrument view: https://science.nasa.gov/photojournal/nasas-juno-catches-3-waves-of-jupiters-polar-cyclones/
- NASA/JPL, shallow lightning: https://www.nasa.gov/missions/juno/shallow-lightning-and-mushballs-reveal-ammonia-to-nasas-juno-scientists/
- NASA Jupiter facts / metallic hydrogen: https://science.nasa.gov/jupiter/jupiter-facts/
- JPL Juno science overview / aurora: https://www.jpl.nasa.gov/news/press_kits/juno/science/

## Gate

```text
SOURCE
-> UNIT/SEMANTIC ALIGNMENT
-> SCALE DECLARATION
-> NORMALIZED DIAGNOSTIC
-> ALTERNATIVE MECHANISMS
-> FALSIFIER
-> RECEIPT
-> CLAIM GATE
```

No similarity of spiral, cyclone shape or emitted light is sufficient by itself to identify a common mechanism.
