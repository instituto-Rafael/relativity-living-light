# RLL Biophoton / Metabolic Transduction Gate — 2026-08-15

Status: `GOVERNED_PROXY_GATE`

Claim boundary:

- `claim_allowed_biophoton_dark_energy_literal=false`
- `claim_allowed_melanin_organelle_literal=false`
- `claim_allowed_tribo_xray_biological_default=false`

This note integrates the session expansion involving mitochondria, chlorophyll/chloroplast analogues, glucose, fructose, gases, sulfur/nutrients, radiation wavelengths, triboluminescence, melanized organisms and ultraweak photon emission.

## 1. Intuition preserved

Living systems are not only passive matter. They are transduction stacks:

```math
substrate + gas\ exchange + pigments + organelle\ channels + radiation/stress \to metabolic\ photon/energy\ bookkeeping
```

Session objects preserved:

- mitochondria / ATP-redox channel;
- chlorophyll and chloroplast-like light harvesting channel;
- glucose/fructose as carbon/sugar substrate channels;
- CO2/O2/CO as gas-exchange and stress bookkeeping channels;
- macro/micronutrients including sulfur as cofactor/provenance channels;
- melanized fungi/melanin as radiation-interaction pigment analogue, not literal organelle;
- triboluminescence/X-ray tape experiment as proof that mechanical charge separation can emit high-energy photons under specific physical conditions, not as default biology;
- ultraweak photon emission/biophotons as metabolic/oxidative photon emission, not dark energy.

## 2. Literature anchors

The gate is consistent with these evidence boundaries:

- biological ultraweak photon emission is reported as low-intensity photon emission related to metabolism/oxidative processes;
- peeling adhesive tape in moderate vacuum was reported to produce visible/radio emission and nanosecond X-ray pulses correlated with stick-slip events;
- melanized fungi exposed to ionizing radiation have shown changed melanin electronic properties and enhanced growth relative to non-melanized controls in published experiments.

These anchors support **transduction bookkeeping**, not cosmological identity claims.

## 3. Gate equation

The proxy model treats biological energy/light production as a bounded transduction score:

```math
T_{bio}(t)
=
W_s S_{sugar}(t)
+W_g G_{gas}(t)
+W_o O_{organelle/pigment}(t)
+W_r R_{radiation/tribo}(t)
+W_n N_{macro/micro}(t)
-W_x X_{stress}(t)
```

with:

```math
0 \le T_{bio}(t) \le 1
```

The route into RLL is:

```math
T_{bio}(t)
\to
\Phi_{bio\gamma}(t)
\to
\Phi_\gamma(t)_{usable}
\to
RLL\_HOMEOSTATIC\_FIELD\_GATE
```

## 4. Proxy variables

The script `scripts/rll_biophoton_metabolic_transduction_gate.py` accepts rows with:

- `glucose`, `fructose`
- `oxygen`, `co2`, `co`
- `chlorophyll_proxy`, `mitochondria_proxy`, `melanin_proxy`
- `radiation_proxy`, `tribo_proxy`
- `stress_proxy`
- `macro_micro_proxy`

These are dimensionless gate variables until real measurements are provided.

## 5. Classification

The gate reports:

- `FORTE_PROXY_ONLY` if the synthetic or supplied ledger shows strong transduction score, improvement over passive metabolism, and organelle/pigment correlation;
- `NEUTRO_ALTO_PROXY_ONLY` for coherent but not strong transduction;
- `FRACO_PROXY_ONLY` when the ledger does not support the transduction channel.

Any synthetic self-test is implementation-only.

## 6. RLL integrated stack

```math
stellar\ ledger
\to
observer/mirror/photon\ gate
\to
biophoton/metabolic\ transduction\ gate
\to
homeostatic\ field\ gate
```

This allows photon/organism/environment coupling to be tested without collapsing metaphors into claims.

## 7. Invariants

- `biophoton != dark_energy_literal`
- `melanin != organelle_literal`
- `melanin/chlorophyll/mitochondria are transduction analogues only`
- `triboluminescent_xray != biological_default_mechanism`
- `macronutrients/micronutrients/gases are bookkeeping channels, not proof of new physics`
- `TOKEN_VAZIO` is mandatory for unmeasured biochemical provenance

## 8. Next gates

1. Replace synthetic rows with measured UPE/metabolic/radiation data.
2. Separate ROS/oxidative stress, ATP/redox, pigments and gas exchange.
3. Add controls for dark current, thermal emission, detector noise and delayed luminescence.
4. Compare against passive metabolic baselines and shuffled radiation channels.
5. Only after lab-grade evidence consider RLL cosmology bridges.

## 9. Live/dead mouse UPE benchmark — 2025 primary experiment

Primary anchor:

- V. Salari et al., *Imaging Ultraweak Photon Emission from Living and Dead Mice and from Plants under Stress*, J. Phys. Chem. Lett. 16 (2025) 4354–4362.
- DOI: `10.1021/acs.jpclett.4c03546`.
- The paper reports a significant contrast between ultraweak photon emission (UPE) from living and dead mice using EMCCD/CCD imaging.
- The paper's abstract defines the measured UPE regime as approximately `10–10^3 photons cm^-2 s^-1` over `200–1000 nm`.

An official NRC research summary additionally reports residual faint postmortem emission in some organs for up to about one hour. This is contextual/secondary evidence and does not replace the primary paper.

### 9.1 Measurement boundary

```text
photon flux != lumen
living > dead UPE contrast != instantaneous zero at death
UPE != consciousness marker
UPE != life-force measurement
UPE != proof of dedicated photon communication
```

A conversion to lumens remains `TOKEN_VAZIO` unless the spectral distribution, collection geometry and photopic weighting are supplied.

### 9.2 Mechanistic bridge allowed by current evidence

The physically conservative route is:

```math
J_e^{mito}
\to
\mathrm{redox/ROS}
\to
E^*_{molecular}
\to
\gamma
```

with membrane lipid peroxidation as an additional photon-producing channel.

This supports a measurable transduction layer:

```math
\mathbf{x}_{bio}(t)=
[
O_2,
CO_2,
pH,
ATP,
\Delta\mu_{Na},
\Delta\mu_{K},
\Delta\mu_{Ca},
ROS,
T
]^\top
```

and:

```math
y_{\gamma}(t)=h_\gamma(\mathbf{x}_{bio}(t))+\epsilon_{det}(t)
```

where `y_gamma` is observed photon flux and `epsilon_det` includes detector/background terms.

This is a candidate state-observation model, not a demonstrated causal decomposition of the mouse experiment.

### 9.3 Controls required before promotion

- body/tissue temperature trajectory;
- detector dark current and read noise;
- thermal radiation and spectral leakage;
- delayed luminescence / prior illumination history;
- tissue-specific postmortem kinetics;
- ROS/redox markers;
- oxygenation, pH and ATP measurements;
- acquisition geometry and quantum efficiency;
- blinded live/dead classification;
- independent replication.

### 9.4 RLL claim boundary

```text
claim_allowed_mouse_upe_as_metabolic_state_observable = exploratory_only
claim_allowed_upe_as_neural_communication = false
claim_allowed_upe_as_consciousness_signal = false
claim_allowed_upe_as_cosmological_bridge = false
```

The productive next experiment is not to ask whether the organism "has light", but whether a preregistered multivariate model predicts the temporal UPE decay from independently measured redox, oxygenation, ATP, pH and temperature without overfitting.

