# RLL Multiphysics Filament Matrix

Status: `structural_and_scientific_custody_contract`  
Claim level: `claim_allowed=false`  
Dependency policy: **stdlib-only validation; no new workflow/YML**

## 1. Why this layer exists

The environmental route correctly separated diesel aerosol, Joule heating, spray electrification, acoustics and detector background. It still simplified the shower/human/environment problem too aggressively by treating coupled processes as isolated explanations.

The corrected model is not:

```text
ions -> singing
```

and it is not:

```text
acoustics alone -> complete explanation
```

It is a typed multiphysics graph:

```text
electrical source / coil / AC
    -> electric and magnetic fields
    -> water heating, spray and charge separation
    -> temperature, humidity, evaporation and vapor pressure
    -> skin, sweat and contact impedance
    -> respiration, autonomic state, heart rate and pressure
    -> voice, room acoustics, joy and relaxation reports
```

The arrows represent possible coupling routes. They do not automatically establish direct causality.

## 2. Invariant: filaments coexist without semantic collapse

Let the state be:

\[
\mathbf S(t)=
[
V,I,f,\mathbf E,\mathbf B,
T_w,T_a,T_{skin},T_{core},
p,RH,p_v,\dot m_{evap},
q_{drop},n_{ion},\sigma_w,pH_w,
G_{skin},Z_{skin},\dot m_{sweat},
HR,BP,Resp,EtCO_2,pH_{blood},
EDA,MCG,RT_{60},ST_v,Joy,Relaxation
]
\]

Each component requires a declared unit, method, timestamp, calibration state, validity mask, uncertainty, source, mechanism class and local evidence state.

A numerical value in one filament cannot silently replace another:

```text
60 Hz from mains
!= 60 bpm heart rate
!= an EEG band
!= acoustic pitch
```

Numeric coincidence is not mechanism identity.

## 3. Ten canonical filaments

### F1 — Electrical source, coil and AC

Tracks RMS voltage/current, frequency, coil/heater current, geometry, electric field, magnetic flux density, power, grounding and leakage.

A coil or AC source may generate fields, but appliance presence alone does not establish a brain or cardiac effect. Field magnitude, spectrum, distance, orientation and exposure must be measured.

### F2 — Water spray, charge and ions

Tracks droplet size, spray velocity, water conductivity, water pH, charge per droplet, ion number density and local electric field.

The Lenard effect and interfacial charge separation are real physical candidates. They remain distinct from the heater resistance and from neural ionic currents:

```text
ambient ion concentration
!= transmembrane neural ion current
```

### F3 — Thermal mass and phase transfer

Tracks water, air, skin and core temperature; pressure; humidity; vapor pressure; heat flux; evaporation; mass; thermal sensation and comfort.

Evaporation is phase and mass transfer, not ionization. Warmth can contribute to comfort, but `warmth -> relaxation` is context-dependent rather than universal.

### F4 — Skin, sweat and electrical contact

Sweat carries ions and changes skin conductance and impedance. Electrodermal activity can reflect sympathetic sudomotor activity, but it does not decode the semantic content of an emotion.

Wet skin may reduce contact resistance. It is a safety variable, not electrical protection.

### F5 — Neuroionic and autonomic state

Neural signaling is electrochemical and depends on ion gradients, membrane potentials and ion channels. This does not authorize:

```text
air ions -> brain ionic signaling
```

without a demonstrated transport, dose and physiological mechanism.

### F6 — Cardiac electricity, magnetism and pressure

The heart's electrical currents generate a weak measurable magnetic field recorded by magnetocardiography. The filament separates ECG, MCG, heart rate, arterial pressure and hemodynamic state.

A detectable field does not prove that it is the dominant heart-brain communication route and does not encode the semantic meaning of joy, love, fear or relaxation.

### F7 — Respiration, CO2 and acid-base state

Emotion and stress may alter breathing. Breathing may alter CO2, and CO2 can alter acid-base balance.

The mediated route is:

```text
context/emotion
-> breathing change
-> CO2 change
-> possible acid-base change
```

not:

```text
emotion has a pH
```

Blood or tissue pH requires a sample or validated measurement method. Mood cannot substitute for pH.

### F8 — Voice, acoustics, joy and relaxation

The singing state is decomposed into observed behavior, reflections/reverberation, vocal support, privacy, warmth, breathing, self-reported joy and self-reported relaxation.

The matrix allows:

```text
warmth + privacy + acoustics + voluntary singing
-> candidate context for joy/relaxation
```

while blocking:

```text
ionization -> singing
```

### F9 — Hair, static charge and point geometry

Hair and skin can provide superficial perception of sufficiently strong static electric fields. Sharp or small-radius conductive geometry can enhance a local field.

This “power of points” is a geometric electromagnetic principle, but a person must not be described as a safe or beneficial lightning rod. Hair movement or tingling can be warning context, does not prove an internal physiological effect, and is not a reliable prerequisite for lightning.

### F10 — Fault current and lightning safety

Tracks grounding, leakage current, touch voltage, plumbing, thunderstorm state and shutdown/avoidance action.

Safety outranks exploratory physiology:

```text
hazard detected
-> stop exposure
-> preserve receipt
-> do not reinterpret as beneficial signal
```

During thunderstorms, showering and plumbing contact are blocked by official safety guidance because lightning can travel through plumbing and electrical systems.

## 4. Typed cross-filament edges

Each edge is typed as:

```text
MECHANISTIC
PHYSIOLOGICAL_MEDIATED
SAFETY_RELEVANT
WARNING_CONTEXT
CANDIDATE_COUPLING
POSSIBLE_MEDIATED
CORRELATION_CANDIDATE_ONLY
```

A correlation-only edge remains `TOKEN_VAZIO_CAUSAL` until mechanism, confounders, reproduction and falsifier exist.

## 5. What the previous answer passed over

The previous answer was correct to reject direct claims that the resistance proves ionization, ionization causes singing, or the heart's magnetic field transmits semantic emotion. It passed over the larger coupled state:

1. AC frequency and coil geometry;
2. electric and magnetic field magnitude;
3. water chemistry and conductivity;
4. spray charge and ion density;
5. heat, humidity and evaporation;
6. skin temperature, sweat and impedance;
7. autonomic and electrodermal state;
8. breathing, CO2 and acid-base mediation;
9. cardiac electrical, magnetic and pressure variables;
10. acoustic support, joy and relaxation;
11. hair/static perception and point geometry;
12. fault-current and lightning safety.

The correction is not to promote every relation. It is to preserve all as separate filaments measurable under one synchronized clock.

## 6. Minimal synchronized receipt

A local experiment must generate:

```text
receipt_id
source_hash
device_ids
calibration_ids
timestamp_start
timestamp_end

electrical:
  V_rms
  I_rms
  frequency
  leakage
  E_field
  B_field

environment:
  water_temperature
  air_temperature
  humidity
  pressure
  water_conductivity
  water_pH

spray:
  droplet_distribution
  charge_or_ion_measurement

human_noninvasive:
  skin_temperature
  skin_conductance
  heart_rate
  blood_pressure
  respiration
  voice_metadata
  joy_self_report
  relaxation_self_report

safety:
  grounding
  plumbing
  thunderstorm
  stop_reason

validity_masks
uncertainties
confounders
falsifier
claim_allowed=false
```

No invasive neural, blood-pH or clinical measurement belongs in a casual shower test. Those fields remain not applicable or require an approved protocol and qualified professionals.

## 7. Safe first experiment

### Stage A — instrument-only

- verified grounding;
- no human contact;
- measure temperature, humidity, conductivity, electric field, magnetic field, charge/ion signal and leakage.

### Stage B — acoustic and thermal context

- measure room impulse response;
- measure temperature and humidity;
- preserve voice/acoustic output and self-reported comfort separately.

### Stage C — non-invasive synchronized observation

Only after electrical safety passes:

- skin temperature;
- electrodermal activity;
- heart rate;
- respiration;
- subjective joy/relaxation.

The experiment must not infer blood pH, brain ion currents or semantic magnetic transmission.

## 8. Promotion rule

\[
Promotion =
Source \land Units \land Calibration \land LocalMeasurement
\land Confounders \land Mechanism \land Reproduction
\land Safety \land Falsifier
\]

Otherwise:

```text
BLOCKED_PENDING_LOCAL_MULTIPHYSICS_RECEIPT
```

## 9. Executable artifacts

```text
data/manifests/rll_multiphysics_filament_matrix.v1.json
scripts/validate_rll_multiphysics_filament_matrix.py
tests/test_rll_multiphysics_filament_matrix.py
```

Validation:

```bash
python3 scripts/validate_rll_multiphysics_filament_matrix.py --strict --write-report
python3 -m unittest tests/test_rll_multiphysics_filament_matrix.py
```

## 10. Closure

`F_ok`: ten coupled filaments are preserved without treating frequency coincidence, ambient ions, pH, biomagnetism, emotion or lightning geometry as equivalent mechanisms.  
`F_gap`: no synchronized local multiphysics receipt exists.  
`F_next`: instrument-only measurement with electrical-safety priority, then acoustic/thermal context, then non-invasive human observation.
