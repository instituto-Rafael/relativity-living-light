# RLL Cellular Metabolic Manifold Bridge V1 — 2026-09-18

**Repository authority:** `instituto-Rafael/relativity-living-light`  
**State:** `GOVERNED_SCIENCE_BRIDGE`  
**claim_allowed:** false  
**Predecessors:** `docs/research/RLL_BIOPHOTON_METABOLIC_TRANSDUCTION_GATE_20260815.md`, `docs/science/SESSION_CAPTURE_RELATIONAL_MANIFOLD_20260915.md`.

## 1. Purpose

This bridge routes the session-wide biochemical/cellular expansion into RLL without converting biology into cosmology.

The only allowed role here is:

```text
cellular/environmental state
-> measurable observables
-> typed model / likelihood / falsifier
-> evidence gate
```

Forbidden shortcut:

```text
metabolite analogy -> cosmological truth
```

## 2. Core state

Define a compartment-indexed cellular/environment state:

```math
x_{cell,c}(t)=
[
Glc, Ins, Lac, Pyr,
Gln, Glu, NH4,
ATP, ADP, AMP, PCr, Cr,
NADH/NAD+, NADPH, GSH/GSSG,
Na+, K+, Cl-, Ca2+, Pi, SO4,
pH, pO2, pCO2, psi_m, ROS,
Fe_{labile}, FeS,
dNTPs
]_{c,t}
```

where `c` may be blood/plasma, interstitium, cytosol, mitochondrial matrix, chloroplast, vacuole, urine, or another explicitly named compartment.

Invariant:

```text
pool != flux
one compartment != another compartment
static concentration != causal rate
```

## 3. Cross-kingdom routing

### Mammalian/animal route

```text
dietary substrate
-> endocrine signaling (including insulin where applicable)
-> membrane transport
-> glycolysis / mitochondrial respiration
-> ATP/redox
-> biosynthesis / maintenance / signaling
```

Insulin is not represented as a generic "metabolic accelerator"; its tissue-specific uptake/storage/catabolic effects must be modeled explicitly.

### Plant route

```text
light + CO2 + mineral nutrients
-> chloroplast carbon/reducing-power production
-> cytosolic metabolism
-> mitochondrial respiration
-> growth / storage / stress response
```

Under oxygen limitation, plant cells can shift toward fermentative pathways that regenerate NAD+.

### Fungal route

The fungal route is allowed to include melanization/radiation response as a separate environmental interaction channel, not as a default energy source. The classic Chernobyl melanin/radiotropism literature is fungal; radioresistant bacteria are tracked separately and are not promoted as the same mechanism.

## 4. Corrected respiration/fermentation boundary

Aerobic mitochondrial respiration:

```text
pyruvate -> acetyl-CoA -> TCA -> NADH/FADH2
-> electron transport chain
-> O2 terminal electron acceptor
-> proton motive force
-> ATP synthase
```

Ethanolic fermentation is distinct:

```text
pyruvate -> acetaldehyde + CO2 -> ethanol
NADH -> NAD+
```

In plants, hypoxia suppresses oxidative phosphorylation and promotes fermentative support of glycolysis. Aerobic fermentation can occur in selected biological contexts, so the gate must use measured O2/flux rather than a hard binary rule.

## 5. Organellar routing

RLL will not use a single "organelle proxy" for all biology.

```text
mitochondrion -> respiration / ATP-redox
chloroplast -> light capture / photosynthetic electron transfer / carbon fixation support
Golgi -> trafficking / glycosylation / lipid-polysaccharide processing
vacuole/lysosome -> storage/degradation/ion homeostasis
ER -> synthesis/folding/lipid metabolism
```

Plant and animal Golgi share core trafficking functions but plant Golgi has major polysaccharide/cell-wall functions.

## 6. N/P/S/NaCl typed channels

### Nitrogen

```text
N -> amino acids / nucleotides / cofactors
plant GS/GOGAT -> organic nitrogen assimilation
Gln -> nitrogen donor + carbon/redox interface
```

### Phosphate

```text
Pi -> ATP/ADP
Pi -> DNA/RNA backbone
Pi -> phospholipids
Pi -> phosphorylation/signaling
```

### Sulfur

```text
S -> cysteine / methionine
-> glutathione
-> Fe-S / cofactors / protein thiols
-> respiration + redox + enzyme/genome maintenance
```

### NaCl

```text
NaCl != one scalar biological driver
Na+ != Cl-
ion gradients != osmotic pressure != membrane voltage
```

For plants, NaCl stress must be represented by explicit Na+, Cl-, osmotic, transport/sequestration and growth variables.

## 7. Radiation / melanin / triboluminescence gate

Allowed external anchors:

- melanized fungi can be highly radioresistant and may show radiation-associated growth/redox changes;
- melanin can contribute to shielding/free-radical quenching and shows radiation-dependent electronic/redox effects;
- adhesive-tape triboluminescence under controlled vacuum conditions can reach the X-ray range.

Disallowed promotion:

```text
melanized fungus -> radiation-only metabolism
melanin -> universal radiation battery
triboluminescent X-ray -> ordinary cell mechanism
nanostructure -> automatic biological X-ray source
```

Any biological X-ray channel requires direct spectroscopy/dosimetry above detector/background controls.

## 8. RLL observables

Candidate observables for a real-data bridge:

```text
O2 consumption rate
CO2 production rate
ATP/ADP
PCr/ATP
lactate/pyruvate
glutamine/glutamate
NAD(H), NADP(H)
GSH/GSSG
pHi / pHe
membrane / mitochondrial potential
Na+, K+, Cl-, Ca2+
Pi
sulfur metabolites
ROS markers
growth / viability
cell-cycle state
dNTP pools
ethanol where biologically appropriate
photon flux / spectrum with detector controls
radiation dose / energy / geometry
```

## 9. Second-order model

A candidate non-cosmological RLL bridge is:

```math
z(t) = [x_{cell}(t), x_{env}(t), x_{organelle}(t)]
```

```math
y(t)=H(z(t),u(t);theta)+epsilon(t)
```

where `u(t)` is a controlled perturbation and `y(t)` is a measured biological observable.

The model must beat a simpler baseline outside the training sample after complexity penalty.

## 10. Falsifiable hypotheses

### RLL-CMM-H1 — pool/flux distinction

Flux-resolved features improve prediction over static pools alone.

**Falsifier:** no out-of-sample improvement or the gain disappears under measurement-error controls.

### RLL-CMM-H2 — N/P/S bottleneck

Explicit N/P/S variables improve stress/proliferation prediction beyond carbon/ATP alone.

**Falsifier:** no reproducible incremental information after cell-type and energy-state controls.

### RLL-CMM-H3 — oxygen branch

Validated hypoxia produces a measurable shift from oxidative phosphorylation toward fermentative flux in suitable plant/fungal systems.

**Falsifier:** no reproducible O2/ethanol/lactate/redox shift.

### RLL-CMM-H4 — sulfur/Fe-S bridge

Perturbing sulfur availability changes Fe-S-dependent respiratory/genome-maintenance observables through measured intermediates.

**Falsifier:** no effect on Fe-S state or downstream functions in a calibrated perturbation range.

### RLL-CMM-H5 — melanin/radiation

Melanization modifies a predefined radiation-response endpoint versus matched controls.

**Falsifier:** no effect after matched strain, dose and blinded replication.

### RLL-CMM-H6 — tribo biological null

Ordinary physiological mechanical deformation does not generate X-ray-scale emission above background.

**Falsifier:** independently replicated spectroscopy/dosimetry demonstrates otherwise.

## 11. Required controls

```text
temperature
pH
oxygenation
cell density
growth phase
osmolarity
ionic strength
nutrient composition
radiation dosimetry
detector dark current/read noise
prior illumination / delayed luminescence
batch
cell/strain identity
blinding where feasible
pre-registered endpoints
```

## 12. Claim boundary

```text
RLL_cellular_bridge = MODEL_SPEC
RLL_cellular_bridge != physiological validation
RLL_cellular_bridge != medical advice
RLL_cellular_bridge != cosmological evidence
external literature != local reproduction
```

## 13. Literature anchors

- Dadachova E, Casadevall A. Curr Opin Microbiol. 2008. PMID:18848901.
- Casadevall A et al. Microbiol Spectr. 2017. PMID:28256187.
- Camara CG et al. Nature. 2008. doi:10.1038/nature07378.
- Krämer D et al. Rev Sci Instrum. 2013. PMID:23742586.
- Zabalza A et al. J Exp Bot. 2019. PMID:30861072.
- The Many Facets of Hypoxia in Plants. PMCID:PMC7356549.
- Try or Die: Dynamics of Plant Respiration and How to Survive Low Oxygen Conditions. PMCID:PMC8780655.
- Protein Transport in Plant Cells: In and Out of the Golgi. PMCID:PMC4243656.
- The Close Relationship between the Golgi Trafficking Machinery and Protein Glycosylation. PMID:33321764.
- Droux M. Photosynth Res. PMID:16328799.
- Nitrogen assimilation in plants: current status and future prospects. PMID:34973427.
- The basics of phosphate metabolism. PMCID:PMC10828206.
- The Role of Chloride Channels in Plant Responses to NaCl. PMID:38203189.

## R3

**F_ok:** session content is routed into typed cellular observables and falsifiers without cosmological promotion.  
**F_gap:** no local wet-lab/isotope dataset and no direct biological X-ray evidence.  
**F_next:** build a bounded real-data adapter only when a public dataset or laboratory receipt supplies explicit units, compartments and provenance.


## 14. Neuroenergetic/osmotic extension — 2026-09-19

The typed extension for sulbutiamine/B1, action-vigor, multigradient membrane transport, EC-KH-pH, BAT, magnesium, B12 and omega-3/6/9 is maintained in `docs/science/RLL_CMM_NEUROMETABOLIC_OSMOTIC_EXTENSION_20260919.md`. It remains a model/falsifier layer, not evidence by analogy.
