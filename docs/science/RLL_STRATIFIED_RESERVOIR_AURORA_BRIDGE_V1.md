# RLL — Stratified Reservoir → Threshold → Observable Bridge V1

**State:** governed research bridge; not a claim of shared physical mechanism.  
**Parent:** Climate Engine × Juno comparative shadow.  
**claim_allowed:** `false`.

## Why this bridge exists

This successor captures one useful topology without collapsing domains:

`SOURCE → RESERVOIR → CONFINEMENT → THRESHOLD → TRANSPORT/RUNAWAY → OBSERVABLE`.

It is instantiated twice.

### A. Deep-lake CO₂ system

A defensible Lake-Nyos-like description is **not** “heavy gaseous CO₂ sits on the bottom.” CO₂ is predominantly dissolved in dense deep water. Hydrostatic pressure suppresses exsolution and stable density stratification/meromixis inhibits overturn. When gas-rich water is displaced upward, the lower pressure can cross a saturation boundary; bubbles form, lower mixture density, increase buoyancy, and can amplify ascent and further exsolution.

A landslide/rockfall, internal wave or seismic disturbance is a candidate perturbation. The exact 1986 Nyos trigger is not promoted as proven here, and gas-saturated lakes can also approach spontaneous instability.

Reference diagnostics:

`P(z)=P0+rho*g*z`

`Sigma_CO2=C_CO2/C_sat(T,P,chemistry)`

with exsolution candidate state when `Sigma_CO2 > 1`, subject to nucleation and solution chemistry.

With `z` positive upward, a local stratification diagnostic is:

`N2=-(g/rho)*d(rho)/dz`, with `N2>0` stable.

### B. Planetary auroral system

Auroral light is a different mechanism. Charged particles and electromagnetic energy are stored/transported through a magnetosphere. Electric and magnetic fields guide or accelerate particles; precipitating particles collide with atmospheric species, excite or ionize them, and radiative relaxation produces wavelength-resolved photons.

The minimal particle kernel is `m*dv/dt=q*(E+v×B)`, while an optically thin spontaneous-emission limiting form is `j_lambda=n_u*A_ul*h*c/(4*pi*lambda)`.

Real auroral forward models require species, cross sections, collisional quenching, altitude profiles, optical transfer and instrument response.

On Earth, common oxygen emissions include ~557.7 nm green and ~630.0 nm red. Jupiter is not an Earth copy: its aurora is driven by its own magnetospheric system, with major internal plasma supply from Io and strong rotational/current-system effects, plus solar-wind coupling. Juno/JIRAM/UVS/Waves therefore remain the planetary evidence authority, not Climate Engine.

## What may be compared

Only typed quantities or dimensionless diagnostics after declaring units, scale and source:

- accumulation time / release time;
- stability or confinement margin;
- threshold distance;
- forcing-to-barrier ratio;
- normalized energy/particle/gas flux;
- observable latency and relaxation time;
- spectral/temporal signatures after instrument response.

A shared event-graph topology is allowed. Equal mechanism is not.

## Seven guardians

1. **Provenance** — lake facts remain bound to lake literature; Juno facts to NASA/instrument teams; RLL composition is authorial modeling.
2. **Context** — aqueous solubility/stratification and plasma electrodynamics remain different constitutive regimes.
3. **Evidence** — this V1 contains only literature anchors plus deterministic reference mathematics; no new lake profile or Juno particle dataset is ingested.
4. **Contradiction** — the tempting statement “one reservoir law explains lake eruption and aurora” is rejected by mechanism mismatch.
5. **Uncertainty** — exact Nyos trigger, source-specific saturation function, auroral distribution functions and any cross-domain fit remain open.
6. **Reproduction** — standard-library reference evaluator and unit tests provide finite mathematical witnesses only.
7. **Rollback** — the bridge is additive; removing it restores the Climate×Juno parent unchanged.

## Gates

```text
LAKE_PROFILE_DATA                 = TOKEN_VAZIO_NOT_INGESTED
AURORAL_PARTICLE_FIELD_DATA       = TOKEN_VAZIO_NOT_INGESTED_IN_THIS_BRIDGE
CROSS_DOMAIN_PARAMETER_FIT        = BLOCKED_UNTIL_TYPED_DATA_AND_UNITS
MECHANISM_EQUIVALENCE             = REFUTED_AS_DEFAULT
INDEPENDENT_REPRODUCTION          = TOKEN_VAZIO
RLL_COSMOLOGICAL_VALIDATION       = NOT_ESTABLISHED
claim_allowed                     = false
```

## Next falsifiable work

1. Add a source-bound deep-lake vertical profile (`z,T,rho,C_CO2,total pressure`) and calculate a saturation/stability margin with uncertainties.
2. Add a Juno auroral particle/field/spectral snapshot with instrument/epoch/units.
3. Fit **separate** forward models first.
4. Only then compare dimensionless event topology under null models; morphology alone must lose against a mechanism-aware baseline if it adds no predictive value.

## Primary comparison anchors

- U.S. Geological Survey volcanic-lake monitoring summaries and Lake Nyos literature.
- Y. Zhang, *Dynamics of CO2-driven lake eruptions*, Nature 379, 57–59 (1996), DOI: 10.1038/379057a0.
- NASA/Juno mission and instrument references already captured by `rll_juno_atmospheric_reference.v1.json`.
- RLL Photonic Matrix Logistics for source → propagation → interaction → detector → observable custody.
