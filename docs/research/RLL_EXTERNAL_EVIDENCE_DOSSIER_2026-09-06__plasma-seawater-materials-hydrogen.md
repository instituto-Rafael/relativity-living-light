# RLL External Evidence Dossier — Plasma, Seawater, Materials, Hydrogen and Resource Recovery

**Date:** 2026-09-06  
**Repository:** `rafaelmeloreisnovo/relativity-living-light`  
**Status:** `EXTERNAL_ADJACENT_EVIDENCE`  
**Integration mode:** additive / append-only  
**Epistemic boundary:** related literature is **not** validation of RLL. A result is promotable only through the repository's own validation/evidence gates.

---

## 0. Scope and evidence grammar

This dossier consolidates the research thread spanning:

1. magnetized plasma and gravity-adjacent physics;
2. marine corrosion, coatings and rotor materials;
3. direct vs pretreated seawater electrolysis;
4. micro/nanoplastic and heavy-metal removal;
5. hydrogen/oxygen production and closed-loop life-support scaling;
6. falsifiable RLL-adjacent experiments.

Evidence labels used here:

- **E0 — established framework:** standard physics/chemistry/engineering relation.
- **E1 — peer-reviewed related evidence:** published result adjacent to the hypothesis space.
- **E2 — engineering/agency reference:** DOE, IEA, NASA or standards-oriented evidence.
- **H — hypothesis/transfer candidate:** coherent extrapolation requiring its own test.
- **TV — TOKEN_VAZIO:** evidence insufficient; preserve the question without promoting a claim.

Invariant:

> `analogy != mechanism != experimental evidence != RLL validation`

---

## 1. Magnetized plasma × gravity boundary

### 1.1 Plasma magnetization — E0

The useful baseline is Lorentz-force/MHD physics:

`F = q(E + v × B)`

A magnetic field can impose anisotropy, gyromotion, current structure, helicity, vorticity and MHD modes in a plasma. This justifies the working phrase **"plasma vectorized by magnetism"** as an engineering metaphor for a magnetized, directionally structured plasma.

### 1.2 Magnetic suppression/structuring of Jeans instability — E1

**Nakanotani, Lazcano Torres, Zank & Thomas Jr. (2025), Physical Review E**  
*Nonlinear kinetic simulations of Jeans instability in a magnetized dusty plasma*  
Phys. Rev. E 112, 015208.  
DOI: `10.1103/wpmj-ks1j`

Key result: kinetic PIC simulations show that when the dust cyclotron frequency magnitude exceeds the Jeans frequency, the modeled Jeans instability is stabilized; increasing magnetic field reduces unstable growth and changes nonlinear structure.

**RLL relevance:** strong evidence that magnetic geometry can reorganize a self-gravitating plasma system.

**Do not infer:** this does **not** demonstrate laboratory generation or amplification of gravity by a magnetic field.

### 1.3 Solar plasma as a gravitational-wave source — E1

**García-Cely & Ringwald (2025), Physical Review Letters**  
*Complete Gravitational-Wave Spectrum of the Sun*  
Phys. Rev. Lett. 135, 061001.  
DOI: `10.1103/gtwg-pr41`

High-temperature solar plasma fluctuations contribute to a stochastic gravitational-wave spectrum. This is consistent with the GR statement that time-dependent stress-energy, including plasma/EM contributions, gravitates.

Useful causal chain:

`plasma dynamics -> T_{mu nu}(t,x) -> metric perturbation / GW`

**Boundary:** the predicted signal is extremely small relative to present laboratory-scale aspirations.

### 1.4 Chiral magnetovortical instability — E1

**Wang & Huang (2024), Physical Review D**  
*Chiral magnetovortical instability*  
Phys. Rev. D 109, L121302.  
DOI: `10.1103/PhysRevD.109.L121302`

The work predicts a magnetohydrodynamic instability in chiral plasma arising from mutual evolution of magnetic and vortical fields.

RLL-adjacent graph:

`B <-> vorticity <-> current <-> flow`

This is relevant to helically structured plasma experiments, but it is **not gravitational evidence**.

### 1.5 Analogue gravity — E1 / boundary reference

**Barceló, Liberati & Visser (2026), Living Reviews in Relativity**  
*Analogue gravity*  
Living Rev. Relativ. 29, 2 (2026).  
DOI: `10.1007/s41114-026-00064-9`

Analogue-gravity systems can exhibit an effective metric for excitations. This provides mathematical and experimental analogues of curved-spacetime phenomena.

Critical invariant:

`g_eff != demonstrated Einstein spacetime curvature`

unless an independent gravitational observable establishes the latter.

### 1.6 Null experimental boundary for anomalous EM–gravity coupling — E1

**Tajmar, Kößling & Neunzig (2024), Scientific Reports**  
*In-depth experimental search for a coupling between gravity and electromagnetism with steady fields*  
Sci. Rep. 14, 19427.  
DOI: `10.1038/s41598-024-70286-w`

The authors tested capacitors, solenoids, crossed-field configurations, helical magnetic fields, toroidal coils and related arrangements with nano-newton/nano-newton-meter sensitivity and found no anomalous force or torque within the tested static-field regime.

**RLL gate:** any proposed anomalous EM/gravity effect must explicitly survive this null-result class or identify a genuinely distinct regime (e.g. frequency, plasma state, geometry) and predict an observable above artifacts/noise.

### 1.7 Current state

- Magnetically structured plasma: **SUPPORTED**.
- Gravity acting on / coupling through ordinary GR stress-energy of plasma: **SUPPORTED**.
- Analogue gravity in effective media: **SUPPORTED AS ANALOGUE**.
- Strong/useful laboratory gravity generated by magnetized plasma: **TOKEN_VAZIO / NOT DEMONSTRATED**.

---

## 2. Marine materials, coatings and rotor architecture

### 2.1 NdFeB rotor — H grounded in established materials behavior

High-grade NdFeB such as N55/N55M is attractive for compact high-flux rotors but should not be treated as a seawater-compatible exposed material. The design principle is:

`marine environment !-> bare NdFeB`

Use multiple barriers rather than a single sacrificial coating.

Candidate stack:

`NdFeB -> Ni/Cu/Ni or qualified base coating -> sealed barrier -> structural sleeve -> dry enclosure`

Gold can be useful as a chemically noble electrical/contact surface, but a thin noble coating with pinholes can concentrate galvanic attack at an exposed less-noble substrate. Therefore continuity, edge sealing, adhesion and porosity are more important than the label "gold plated" alone.

### 2.2 Au / Ag / Cu functional separation — H/E0

For chloride-rich marine exposure:

- **Au:** strong candidate for selected external electrical/contact interfaces because of high nobility.
- **Ag:** excellent conductor but chloride/sulfur surface chemistry makes it less attractive as the final exposed marine surface.
- **Cu:** excellent bulk conductor, but marine chloride environments promote patina/corrosion products and it should normally be protected when electrical stability matters.

Preferred functional architecture:

`substrate/insulator -> adhesion/barrier -> Cu bulk conductor -> Au interface`

rather than forcing Au, Ag and Cu into one homogeneous alloy when their functions can be separated geometrically.

### 2.3 Titanium: purity is not the same as aerospace grade — E1

**Corrosion of commercial pure titanium and two titanium alloys in extremely high-chloride and high-alkali seawater electrolysis environment**  
Journal of Alloys and Compounds 1020 (2025) 179431.  
DOI: `10.1016/j.jallcom.2025.179431`

The study compares CP Ti Grade 2, Ti-6Al-4V and another Ti alloy under very aggressive high-chloride/high-alkali conditions. CP Ti Grade 2 showed superior corrosion resistance in that test environment relative to the tested Ti alloys, with micro-galvanic effects associated with dual-phase alloy microstructures contributing to pitting.

Implication:

`"aerospace" != "more pure" != automatically "more corrosion resistant"`

Ti-6Al-4V (Grade 5) is an aerospace-strength alloy; CP Grade 2 is commercially pure titanium and may be the better wet-side choice in specific aggressive electrochemical environments.

### 2.4 Sleeve electromagnetic losses — E0/H

A conductive metallic rotor sleeve in time-varying magnetic fields can host eddy currents:

`dB/dt -> J_eddy -> Joule loss -> rotor heating`

Candidate sleeve materials therefore require simultaneous mechanical, corrosion, thermal and electromagnetic evaluation. Nonconductive high-strength composites are a useful comparison baseline where mechanically appropriate.

---

## 3. Seawater electrolysis × hydrogen

### 3.1 State-of-the-art review — E1

**Yu et al. (2025), Nature Reviews Materials**  
*Direct seawater electrolysis for hydrogen production*  
Nature Reviews Materials 10, 857–873 (2025).  
DOI: `10.1038/s41578-025-00826-x`

Major direct-seawater-electrolysis challenges include chloride chemistry/corrosion, competing chlorine evolution, inorganic precipitation/fouling, catalyst selectivity and long-duration stability.

RLL engineering consequence:

For an MVP, the defensible baseline remains:

`seawater -> pretreatment/desalination -> purified water -> commercial electrolyzer`

and direct seawater electrolysis should be compared as an experimental branch, not assumed superior.

### 3.2 Decoupled chlorine-suppression architecture — E1

**Liu et al. (2024), Nature Communications**  
*Redox-mediated decoupled seawater direct splitting for H2 production*  
Nat. Commun. 15, 8874 (2024).  
DOI: `10.1038/s41467-024-53335-w`

A redox-mediated decoupled architecture separates the oxygen-evolution process and suppresses chlorine-containing byproducts in the demonstrated system.

RLL transfer candidate:

`separate functions spatially/temporally instead of forcing all reactions onto one interface`

This matches the general architectural principle used elsewhere in the dossier: functional decomposition lowers cross-coupled failure modes.

### 3.3 Long-duration alkaline seawater electrolysis — E1

**Sha et al. (2025), Nature**  
*10,000-h-stable intermittent alkaline seawater electrolysis*  
Nature 639, 360–367 (2025).  
DOI: `10.1038/s41586-025-08610-1`

This is strong evidence that long-duration seawater-electrolysis architectures can be engineered substantially beyond simple two-electrode immersion. It does **not** erase site-specific requirements for brine chemistry, chlorine selectivity, maintenance, balance of plant and economics.

### 3.4 Electrolyzer engineering benchmark — E2

**U.S. DOE — Technical Targets for Liquid Alkaline Electrolysis**

Reference values include a 2022 system energy figure of about 55 kWh/kg-H2 and DOE targets progressing lower; stack and system targets must be interpreted separately.

For quick scaling, a transparent engineering range is preferable to a single magic number:

`~48–55 kWh/kg-H2` for scenario analysis, with the actual vendor/system value measured.

Stoichiometric relations:

- about 9 kg of reacted water per 1 kg H2;
- about 8 kg O2 coproduct per 1 kg H2.

### 3.5 400 kW thought-experiment baseline — H / engineering estimate

Using 400 kW, 90% utilization and approximately 50 kWh/kg-H2:

- electrical energy: ~8.64 MWh/day;
- hydrogen: ~173 kg/day;
- oxygen: ~1.38 t/day.

These are **scenario numbers**, not a procurement guarantee. Balance-of-plant, compression, purity, degradation, downtime, water treatment and safety must be separately budgeted.

### 3.6 Market boundary — E2

**IEA, Global Hydrogen Review 2026** (published 18 June 2026) reports that installed electrolysis capacity exceeded 4 GW in 2025 and emphasizes that low-emissions hydrogen economics remain highly sensitive to electricity prices, CAPEX, infrastructure, demand/offtake and policy.

RLL implication: optimization should use **system-level kWh/kg + delivered cost**, not cell voltage alone.

---

## 4. Micro/nanoplastics, heavy metals and brine resource recovery

### 4.1 Separation-first architecture — E0/H

Preferred process invariant:

`separate -> concentrate -> destroy/polish`

rather than applying plasma or microwave energy to the full bulk-water flow.

Candidate train:

`screening -> coagulation/flotation (where appropriate) -> MF/UF -> RO/NF as required -> clean-water stream + concentrated reject`

Then process the reject separately for plastics, metals and mineral recovery.

### 4.2 Membrane removal of micro/nanoplastics — E1

**Pressure-Driven Membrane Processes for Removing Microplastics** (2025 review; PubMed PMID 40137033) reports that MF, UF, NF and RO can achieve high removal efficiencies, in some reviewed cases approaching 100%, while emphasizing fouling, matrix dependence and nanoplastic challenges.

Additional review reference:

**A review of microplastic removal from water and wastewater by membrane technologies** (PubMed PMID 37452543).

A 2025 critical review of adsorption-based remediation also treats coagulation, filtration, membranes and adsorption as complementary rather than a single universal solution:

**Environmental Pollution (2025), DOI `10.1016/j.envpol.2025.126658`.**

### 4.3 Cold plasma degradation of microplastics — E1

**Atmospheric cold plasma as a novel approach to remediating microplastics pollution in water**  
Environmental Pollution 356 (2024) 124390.  
DOI: `10.1016/j.envpol.2024.124390`

The reported experiment reduced microplastic mass by up to 11.3% after 30 min plasma treatment, with oxidation/hydrolysis implicated.

Interpretation:

- useful proof that plasma can chemically attack microplastics;
- insufficient evidence for plasma as the primary bulk-water treatment step;
- fragmentation must not be mistaken for complete mineralization;
- energy intensity and byproduct analysis are mandatory.

### 4.4 Microwave treatment — H / process principle

Microwave energy is more rational after dewatering/concentration when targeting plastic-rich residues, because bulk water itself strongly absorbs microwave energy. Candidate uses include thermal conversion/pyrolysis or catalyst-assisted treatment of a concentrated solid/slurry stream.

Gate:

`melted plastic != destroyed plastic`

Track carbon balance, VOCs, halogenated species, residual micro/nanoparticles and net energy.

### 4.5 Heavy metals — E0/H

Dissolved metal ions are not reliably removed by a simple particle filter. Depending on speciation, candidates include:

- RO/NF;
- adsorption;
- ion exchange;
- precipitation/co-precipitation;
- electrochemical recovery.

Critical mass-balance invariant:

`removed from product water != destroyed`

The metal load migrates into a concentrate, sorbent, precipitate or electrode and needs a custody/disposal/recovery path.

### 4.6 Mineral recovery from brine — H

Instead of redissolving all residual solids indiscriminately, investigate controlled fractional separation/recovery of major/minor ions (e.g. Mg, Ca, NaCl, K-bearing fractions) while keeping toxic metals and organic contaminants segregated.

For potable remineralization, add only qualified species at controlled concentrations. For electrolyzer feed, preserve high purity.

---

## 5. Closed-loop life-support scaling — contextual engineering, not RLL validation

A 400 kW / ~173 kg-H2-day scenario produces roughly ~1.38 t O2/day by stoichiometry. Using a NASA human metabolic oxygen requirement on the order of ~0.84 kg O2/person/day gives an oxygen-only theoretical ceiling around 1,600 person-equivalents.

This is **not** a statement that a 400 kW electrolyzer supports 1,600 people by itself. A habitat also needs:

- CO2 removal/reduction;
- water recovery;
- food/nutrients;
- thermal rejection;
- pressure/atmosphere management;
- trace-contaminant control;
- redundancy and maintenance;
- primary energy.

NASA ISS water-recovery work demonstrates the value of highly regenerative loops; the correct systems view is therefore material cycling, not one-pass consumption.

---

## 6. Falsifiable experiment matrix for RLL-adjacent research

| ID | Experiment | Baseline | Perturbation | Primary observable | Promotion gate |
|---|---|---|---|---|---|
| RLL-X01 | Magnetized plasma geometry | plasma, B=0 | controlled B topology | density/current/vorticity spectra | reproducible change vs controls |
| RLL-X02 | Dynamic EM–force residual | instrument dummy / static-field controls | pulsed/high-frequency B/E/plasma | force/torque phase-locked to drive | survives EM, thermal, acoustic, vibration artifacts |
| RLL-X03 | Gravity-model consistency | GR stress-energy prediction | measured plasma/EM T_mu_nu | predicted h/g signal | no anomalous claim unless residual exceeds modeled uncertainty |
| RLL-X04 | Direct seawater electrolysis | RO + conventional electrolysis | direct/decoupled seawater cell | kWh/kg-H2, Cl2/HOCl, degradation | beats baseline on system-level metric |
| RLL-X05 | Plasma microplastic treatment | MF/UF/RO separation | plasma on concentrate | total organic carbon, polymer MW, particle count | demonstrates destruction, not fragmentation only |
| RLL-X06 | Microwave residue treatment | conventional thermal treatment | microwave/catalyst route | energy/kg destroyed + product speciation | lower net energy or higher controlled recovery |
| RLL-X07 | Marine coating stack | qualified reference coating | Au/Ag/Cu/barrier variants | salt-fog/immersion EIS, pitting, adhesion | no hidden galvanic acceleration at defects |
| RLL-X08 | Ti wet-side materials | CP Ti Grade 2 | Grade 5 / other alloys | corrosion rate, pitting, EIS | environment-specific superiority established |
| RLL-X09 | Rotor sleeve | reference sleeve | metallic vs composite sleeve | eddy loss, temperature, stress margin | electromagnetic + mechanical + corrosion gates pass |

---

## 7. TOKEN_VAZIO ledger

1. **TV-GRAV-PLASMA-LAB-GAIN** — no demonstrated strong/useful laboratory gravity generation from magnetized plasma.
2. **TV-GRAV-DYNAMIC-EM-REGIME** — static-field null experiments do not by themselves close every dynamic/plasma regime; quantitative predictions are required before testing.
3. **TV-DSE-MVP-SUPERIORITY** — direct seawater electrolysis is not yet established here as superior to RO + conventional electrolysis for the proposed MVP boundary conditions.
4. **TV-PLASMA-MP-NET-ENERGY** — no demonstrated system-level net-energy advantage for plasma destruction of concentrated microplastics in the proposed architecture.
5. **TV-MW-MP-NET-ENERGY** — no demonstrated system-level advantage for microwave residue treatment until feed composition, dryness, catalyst and product accounting are fixed.
6. **TV-AU-COATING-STACK-QUALIFICATION** — no qualified thickness/porosity/adhesion stack has yet been specified for the proposed marine rotor.
7. **TV-N55M-ROTOR-DESIGN** — rotor diameter, pole count, RPM, air gap, sleeve stress and thermal model remain unspecified.
8. **TV-H2-CAPEX-SITE** — exact hydrogen cost remains site-specific until electricity tariff, duty cycle, water chemistry, electrolyzer quotation, compression/storage and offtake are fixed.
9. **TV-HEAVY-METAL-SPECIATION** — target contaminants and oxidation/speciation states are unspecified; treatment selection cannot be finalized.
10. **TV-LIFE-SUPPORT-CLOSURE** — oxygen production alone does not close a habitat mass/energy balance; food, CO2, thermal and nutrient loops remain open.

---

## 8. Cross-domain synthesis

The strongest architecture emerging from the evidence is functional decomposition:

`structure != conductor != corrosion barrier != catalyst != separator != energy source`

Use each subsystem where it is strongest:

- **NdFeB:** magnetic flux;
- **ferromagnetic return path:** flux closure;
- **Cu:** bulk electrical conduction;
- **Au:** selected stable electrical/contact interface;
- **CP Ti / qualified alloy:** wet-side structural/corrosion role where testing supports it;
- **membranes/RO:** bulk separation;
- **plasma/microwave:** concentrated-residue or controlled experimental treatment;
- **electrolyzer:** H2/O2 production;
- **instrumentation + controls:** falsification and artifact rejection.

This avoids asking one material or one physical effect to solve mutually incompatible objectives.

---

## 9. Primary references verified for this integration

1. Yu, L. et al. **Direct seawater electrolysis for hydrogen production.** *Nature Reviews Materials* 10, 857–873 (2025). DOI: `10.1038/s41578-025-00826-x`.
2. Sha, Q. et al. **10,000-h-stable intermittent alkaline seawater electrolysis.** *Nature* 639, 360–367 (2025). DOI: `10.1038/s41586-025-08610-1`.
3. Liu, T. et al. **Redox-mediated decoupled seawater direct splitting for H2 production.** *Nature Communications* 15, 8874 (2024). DOI: `10.1038/s41467-024-53335-w`.
4. Nakanotani, M. et al. **Nonlinear kinetic simulations of Jeans instability in a magnetized dusty plasma.** *Physical Review E* 112, 015208 (2025). DOI: `10.1103/wpmj-ks1j`.
5. García-Cely, C. & Ringwald, A. **Complete Gravitational-Wave Spectrum of the Sun.** *Physical Review Letters* 135, 061001 (2025). DOI: `10.1103/gtwg-pr41`.
6. Wang, S. & Huang, X.-G. **Chiral magnetovortical instability.** *Physical Review D* 109, L121302 (2024). DOI: `10.1103/PhysRevD.109.L121302`.
7. Tajmar, M., Kößling, M. & Neunzig, O. **In-depth experimental search for a coupling between gravity and electromagnetism with steady fields.** *Scientific Reports* 14, 19427 (2024). DOI: `10.1038/s41598-024-70286-w`.
8. Barceló, C., Liberati, S. & Visser, M. **Analogue gravity.** *Living Reviews in Relativity* 29, 2 (2026). DOI: `10.1007/s41114-026-00064-9`.
9. **Corrosion of commercial pure titanium and two titanium alloys in extremely high-chloride and high-alkali seawater electrolysis environment.** *Journal of Alloys and Compounds* 1020, 179431 (2025). DOI: `10.1016/j.jallcom.2025.179431`.
10. **Atmospheric cold plasma as a novel approach to remediating microplastics pollution in water.** *Environmental Pollution* 356, 124390 (2024). DOI: `10.1016/j.envpol.2024.124390`.
11. **A review of microplastic removal from water and wastewater by membrane technologies.** PubMed PMID: `37452543`.
12. **Pressure-Driven Membrane Processes for Removing Microplastics.** PubMed PMID: `40137033`.
13. **A critical review of microplastics and nanoplastics in wastewater: Insights into adsorbent-based remediation strategies.** *Environmental Pollution* (2025). DOI: `10.1016/j.envpol.2025.126658`.
14. U.S. Department of Energy. **Technical Targets for Liquid Alkaline Electrolysis.** Engineering benchmark/targets.
15. International Energy Agency. **Global Hydrogen Review 2026.** Published 18 June 2026.

---

## 10. Provenance note

This file was generated as an additive research-integration artifact from the 2026-09-06 interdisciplinary brainstorming thread and web-verified against the primary/reputable sources listed above. No pre-existing RLL scientific claim was changed by this commit. No external paper listed here is treated as proof of RLL.

**Custody state:** `SOURCE_REVIEWED -> SYNTHESIZED -> REPO_BRANCH_STAGED`  
**Claim state:** `EXTERNAL_ADJACENT_EVIDENCE`; RLL validation status unchanged.
