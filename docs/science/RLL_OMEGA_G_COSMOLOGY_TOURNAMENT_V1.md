# RLL Omega_G Cosmology Tournament V1

## Why this layer exists

The first Omega_G integration stopped at mathematical governance: canonical geometry source, RLL consumer contract, validator and boundary tests. That was insufficient for scientific use because no fair comparison surface connected Omega_G to the existing cosmology likelihoods.

This layer fixes that omission by reusing the established G4 background tournament rather than creating a second likelihood implementation.

## Existing likelihood authority reused

`tools/run_g4_background_tournament.py` already compares:

- LCDM;
- wCDM;
- CPL/w0waCDM;
- GEDE;
- IDE Q=3 beta H rho_Lambda;
- RLL.

Its common background data are:

- pure cosmic-chronometer H(z);
- DESI DR2 BAO 13-vector with committed 13x13 covariance;
- Pantheon+SH0ES with full STAT+SYS covariance and profiled M_B.

Therefore Omega_G is tested *around* this engine, not by replacing it.

## Experimental arms

```text
ARM0_BASELINE     = G4 unchanged
ARM1_NULL_BINDING = Omega_G plumbing enabled, exact baseline parity required
ARM2_BOUND        = one approved geometry->observable mechanism at a time
ARM3_ABLATION     = remove the active Omega_G term
ARM4_HOLDOUT      = predeclared out-of-sample confirmation
```

The first scientific requirement is not improvement. It is identity:

[
M_{\Omega_G=I}(D)=M_{\rm baseline}(D).
]

If null plumbing changes LCDM, wCDM, CPL or RLL, the integration fails before any candidate test.

## Models

The required comparison set is:

[
\{\Lambda{\rm CDM},\;w{\rm CDM},\;{\rm CPL},\;{\rm RLL}\}.
]

GEDE and IDE remain additional controls already present in G4.

Every shared parameter, dataset, covariance and optimizer policy must remain matched. Every additional Omega_G parameter counts in (k) for AIC/AICc/BIC.

## Dataset boundaries

### H(z)

Eligible only through an explicit mechanism that maps a dimensionless or unit-declared Omega_G invariant into the H(z) prediction without reusing an effect already present in the chronometer reduction.

### DESI DR2 BAO

The full committed 13x13 covariance is preserved. No Omega_G term may be added after the fact to DM/rd, DH/rd or DV/rd without stating whether it acts on H(z), comoving distance, r_d, or survey compression.

### Pantheon+

The full STAT+SYS covariance and profiled M_B policy remain unchanged. An Omega_G candidate must specify whether it changes luminosity distance, source-state nuisance, propagation, or another named layer.

### f sigma8 and CMB

These are deliberately **not** admitted to a background-only Omega_G binding. They remain blocked until model-specific perturbation closure and the relevant likelihood contract exist. This follows the same fairness boundary as G4.

## Binding registry

The registry is:

`data/inputs/omega_g/observable_effect_binding_registry.v1.yaml`

No candidate can become active unless all fields are populated:

[
BIND(I_j,O_k,mechanism,units,covariance,falsifier)
]

plus the mathematical map, parameter bounds, aggregation level, double-counting audit, holdout and provenance.

Current H(z), BAO, Pantheon+, growth, CMB and lensing bindings are intentionally TOKEN_VAZIO/BLOCKED until such mechanisms are declared.

## Runner

Fast structural validation:

```bash
python tools/run_omega_g_cosmology_tournament.py --mode validate
```

Exact null-parity gate:

```bash
python tools/run_omega_g_cosmology_tournament.py --mode null-parity
```

Existing G4 background baseline through the Omega_G bridge:

```bash
python tools/run_omega_g_cosmology_tournament.py \
  --mode baseline \
  --seeds 11,23,37 \
  --maxiter 250 \
  --integration-points 4096 \
  --output artifacts/omega_g/g4_baseline.json
```

A short `maxiter=3` run is a smoke test only and must not be promoted as a converged cosmological fit.

## What this does not yet do

It does not invent a geometry-to-cosmology equation. That would be the exact error the binding gate was created to prevent.

The next scientific object is one explicit candidate binding with dimensions and mechanism. It must first pass synthetic recovery, then the real background tournament, then ablation and holdout.

## Current state

```text
Omega_G mathematical source                 PASS_MATERIALIZED
RLL consumer contract                       PASS_MATERIALIZED
cosmology tournament contract               PASS_MATERIALIZED
observable binding registry                 PASS_MATERIALIZED
runner                                      PASS_MATERIALIZED
focused tests                               MATERIALIZED_NOT_EXECUTED
null parity                                 TOKEN_VAZIO_NOT_RUN
G4 baseline through bridge                  TOKEN_VAZIO_NOT_RUN
Omega_G physical/cosmological binding       TOKEN_VAZIO
scientific claim                            BLOCKED
```

R3=<F_ok: LambdaCDM/wCDM/CPL/RLL + H(z)/DESI BAO/Pantheon comparison surface is now explicitly connected to Omega_G governance; F_gap: no approved physical binding exists yet and no new tournament run has been executed; F_next: execute null parity, then define exactly one mechanism-complete binding and test synthetic recovery before real-data comparison>.
