# RLL Canonical Environmental Signal Orchestrator

Status: `structural_and_scientific_custody_contract`  
Claim level: `claim_allowed=false`  
Workflow policy: **no new YML is required by this module**

## 1. Corrected origin sentence

The voice transcription is normalized as:

> The observatory must not silence the wind merely because the wind disturbed a measurement. It must first determine whether the wind moved the instrument, refracted or scattered the light, transported aerosols, changed the atmospheric layer, altered a particle background, or exposed a process missing from the model.

This sentence is an operational rule, not a claim that every disturbance is useful signal.

## 2. Invariant

```text
observed anomaly
-> semantic classification
-> source custody
-> reproduction attempt
-> mechanism assessment
-> decision
```

Only after **meaning + reproduction + mechanism** may an item be:

- discarded with a recorded reason;
- corrected as calibration/model/instrument error;
- promoted to a physical or environmental signal.

Unknown cause remains `TOKEN_VAZIO_CAUSE`.

## 3. Separation of responsibilities

```text
YML / CI
    orders commands and preserves exit status

shell
    invokes one typed module and returns its receipt

manifest
    preserves meaning, order, source, assumptions and claim boundary

physical module
    performs a declared transformation

validator
    checks structural invariants and blocks unsupported promotion

scientific review
    assesses the mechanism, data, uncertainty and reproducibility
```

Therefore:

```text
workflow success != physical validation
schema success   != mechanism confirmed
repetition       != independent replication
```

## 4. Canonical module order

1. `source_custody`
2. `medium_state`
3. `optical_transport`
4. `cloud_phase_microphysics`
5. `combustion_and_mineral_aerosol`
6. `spray_electrification`
7. `electrical_heating_shower`
8. `human_acoustic_context`
9. `detector_specific_background`
10. `noise_classification`
11. `reproduction_and_mechanism`
12. `decision_and_claim_gate`

No module may silently absorb another module's semantics.

## 5. Forgotten and previously collapsed physical pieces

### 5.1 Atmospheric state

The minimum state is not a scalar “atmospheric correction.” It must preserve, when relevant:

\[
A=[T,p,\rho,\mathbf u,q_v,q_l,q_i,n_\lambda,aerosol,charge,\mathbf E,turbulence]
\]

Absence is represented by a validity mask and a typed `TOKEN_VAZIO`, never by an invented zero.

### 5.2 Optical observatories

Atmospheric temperature, pressure, humidity, density, aerosol loading and turbulence can modify:

- refractive index;
- extinction;
- scattering;
- wavefront distortion;
- scintillation;
- instrumental pointing and stability.

“Calm wind” is still a measured state. It may coexist with shear aloft, inversion, weak unresolved motion or low turbulence.

### 5.3 Cloud and ice microphysics

The model must distinguish:

```text
VAPOR
LIQUID
SUPERCOOLED_LIQUID
ICE_CRYSTAL
GRAUPEL
HAIL
MELTING_MIXTURE
TOKEN_VAZIO_PHASE
```

Condensation, freezing, deposition, accretion, melting, evaporation and sublimation are separate operators. Vitrification is not an automatic synonym for atmospheric freezing.

### 5.4 Diesel exhaust and combustion pollution

The correct state is:

```text
DIESEL_EXHAUST = MIXED_PHASE_AEROSOL
```

A substantial and often dominant fraction of diesel particulate matter is a **solid carbonaceous soot/elemental-carbon core**. The total aerosol, however, is not “solid only.” It may also include:

- organic carbon and adsorbed/semi-volatile organics;
- condensable particulate matter;
- sulfate and nitrate;
- ash and trace metals;
- associated water;
- gaseous co-pollutants such as NOx, CO and hydrocarbons, which are tracked separately from PM.

The composition changes with fuel, engine load, temperature, dilution, lubricant and after-treatment. The manifest therefore forbids the global statement `diesel_pm_is_solid_only=true`.

### 5.5 Dust, smoke and biological material

Aerosol classes must remain distinct:

```text
MINERAL_DUST
SEA_SALT
SOOT_BLACK_CARBON
ORGANIC_AEROSOL
SULFATE_NITRATE
ASH_METALS
BIOAEROSOL
UNKNOWN_AEROSOL
```

Pollen, spores, fragments, microorganisms and other biological material are not interchangeable with soot or mineral dust.

### 5.6 Electric shower: corrected mechanism

An ordinary electric shower heats water primarily by **resistive/Joule heating**:

\[
P=VI=I^2R=\frac{V^2}{R}
\]

This does **not** establish that the resistance itself ionizes the surrounding water or air.

A different mechanism can occur in sprays: droplet breakup, collision and air-water contact can separate charge (`spray electrification`, also called the Lenard effect). Recent laboratory work has measured charged droplets and local gas ions under controlled spray conditions.

Therefore the canonical distinction is:

```text
electric resistance -> Joule heating
water spray         -> possible charge separation / ion production
resistance          -X-> proven cause of shower-air ionization
```

For a real domestic shower, local ion concentration, ozone, droplet-size distribution, voltage leakage, grounding and water chemistry remain `TOKEN_VAZIO_LOCAL_MEASUREMENT` until measured safely with appropriate instrumentation.

### 5.7 Why people may sing in the shower

The supported physical route is acoustic:

- hard surfaces create reflections and reverberation;
- room response changes perceived vocal support, clarity and timbre;
- warm water and privacy may improve comfort, but the psychological contribution is context-dependent.

The system must not claim:

```text
air ionization causes a person to sing
```

That causal link is not established. It remains blocked rather than converted into a pleasing explanation.

### 5.8 IceCube and detector-specific backgrounds

Instrument adapters must not mix optical-telescope atmosphere with IceCube physics.

For an optical observatory:

```text
atmosphere -> optical transport -> telescope/detector
```

For IceCube:

```text
cosmic ray
-> atmospheric air shower
-> atmospheric muons/neutrinos
-> interaction in or near ice
-> Cherenkov light in ice
-> DOM response
-> event reconstruction
-> background classification
```

Atmospheric muons and neutrinos are physical backgrounds for astrophysical-neutrino searches. Cherenkov propagation in Antarctic ice and DOM response are separate from atmospheric optical refraction.

## 6. Noise states

```text
NOISE_UNCLASSIFIED
BACKGROUND_PHYSICAL
BACKGROUND_INSTRUMENTAL
MODEL_DISCREPANCY
CALIBRATION_DRIFT
ENVIRONMENTAL_SIGNAL
CANDIDATE_PHYSICS
TOKEN_VAZIO_CAUSE
DISCARDED_WITH_REASON
CORRECTED_WITH_RECEIPT
PROMOTED_TO_SIGNAL
```

The last three states require a receipt containing:

- literal observation;
- source and hashes;
- semantic meaning;
- reproduction result;
- mechanism result;
- uncertainty;
- alternative explanations;
- falsifier;
- authority and decision;
- rollback or reversal path.

## 7. Promotion rule

\[
Decision(x)=
\begin{cases}
DISCARD, & M\land R\land K\land reason\\
CORRECT, & M\land R\land K\land correction\_receipt\\
PROMOTE, & M\land R\land K\land evidence\land falsifier\\
BLOCKED, & \text{otherwise}
\end{cases}
\]

Where:

- \(M\): semantic meaning fixed;
- \(R\): reproduction attempted and recorded;
- \(K\): mechanism classified with alternatives.

## 8. Academic anchors

1. U.S. EPA. PM2.5 species and diesel-PM accounting: elemental carbon, organic carbon, sulfate, nitrate, remainder, filterable and condensable PM.  
   `https://www.epa.gov/air-emissions-inventories/how-does-pm25-relate-pm-species-such-ec-oc-so4-no3-pmfine-and-diesel-pm25`

2. U.S. EPA. *Health Assessment Document for Diesel Engine Exhaust*. Carbonaceous core with adsorbed organic/sulfate material and trace components.  
   `https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=300055PV.TXT`

3. Xia Y. et al. “Visualization of the Charging of Water Droplets Sprayed into Air.” *J. Phys. Chem. A* 2024;128:5684–5690.  
   DOI: `10.1021/acs.jpca.4c02981`

4. Naspolini H.F.; Rüther R. “The effect of measurement time resolution on the peak time power demand reduction potential of domestic solar hot water systems.” *Renewable Energy* 2016;88:325–332.  
   DOI: `10.1016/j.renene.2015.11.046`

5. Redman Y.G. et al. “Singing in different performance spaces: The effect of room acoustics on singers' perception.” *J. Acoust. Soc. Am.* 2023;154:2256–2264.  
   DOI: `10.1121/10.0021331`

6. IceCube Collaboration. Detector and Cherenkov-light description.  
   `https://icecube.wisc.edu/science/icecube/`

7. IceCube Collaboration. Atmospheric muons and neutrinos as backgrounds in southern-sky searches.  
   `https://icecube.wisc.edu/news/research/2025/01/icecube-search-for-neutrino-sources-from-the-southern-sky-using-neutrinos-at-medium-energies/`

## 9. Executable artifacts

```text
schemas/rll_environmental_signal_manifest.schema.json
data/manifests/rll_environmental_signal_manifest.v1.json
scripts/validate_rll_environmental_signal_manifest.py
tests/test_rll_environmental_signal_manifest.py
```

Validation:

```bash
python3 scripts/validate_rll_environmental_signal_manifest.py --strict
python3 -m unittest tests/test_rll_environmental_signal_manifest.py
```

## 10. Closure

`F_ok`: environmental, aerosol, shower, acoustic and detector-specific semantics are separated and ordered.  
`F_gap`: no local shower-ion measurement and no full atmospheric coupling to the RLL likelihood exist yet.  
`F_next`: connect measured datasets to each typed module without adding another workflow and preserve `claim_allowed=false`.
