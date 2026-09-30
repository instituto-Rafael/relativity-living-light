# RLL_QCD_PRIMORDIAL_GATE

Status: **implemented contract; live numerical EoS/constraint ingestion still gated by TOKEN_VAZIO**.

## 1. Scientific scope

This module creates a falsifiable bridge between QCD-era thermodynamics and the RLL cosmological sector. It does **not** treat LHC anisotropic-flow coefficients as direct cosmological observables.

The supported chain is:

```text
QCD / collider evidence
  -> thermodynamic EoS input epsilon(T), g_*s(T)
  -> primordial expansion H(T), t(T), a(T)
  -> explicit RLL-vs-baseline Delta_H(T)
  -> verified cosmological bound
  -> PASS / FALSIFIED / TOKEN_VAZIO
```

The unsupported shortcut is:

```text
v2 or v3 -> RLL confirmed
```

ALICE and CMS light-ion measurements are therefore registered as `REFERENCE_ONLY`: they support the collective-QCD/hydrodynamic bridge and sensitivity to the initial nuclear geometry, but they do not provide a direct RLL likelihood.

## 2. Physics contract

The gate uses one complete non-RLL thermal background energy density,

\[
\epsilon_{\rm bg}(T),
\]

plus an explicitly separated RLL contribution,

\[
\epsilon_{\rm RLL}(T).
\]

The two expansion histories are

\[
H_{\rm bg}^2(T)=\frac{8\pi G}{3c^2}\epsilon_{\rm bg}(T),
\]

\[
H_{\rm RLL}^2(T)=\frac{8\pi G}{3c^2}\left[\epsilon_{\rm bg}(T)+\epsilon_{\rm RLL}(T)\right],
\]

with

\[
\Delta_H(T)=\frac{H_{\rm RLL}(T)-H_{\rm bg}(T)}{H_{\rm bg}(T)}.
\]

For navigation/diagnostics the current v1 implementation also reports the radiation-era proxy

\[
t(T)\simeq \frac{1}{2H(T)},
\]

and the entropy-conservation scale-factor ratio

\[
aTg_{*s}^{1/3}=\mathrm{const}.
\]

The `t=1/(2H)` value is an approximation, not a replacement for integrating the full Friedmann/continuity system through a varying QCD equation of state.

## 3. Double-counting invariant

A common unsafe decomposition is

\[
\rho_{\rm rad}+\rho_{\rm QCD}
\]

when `rho_rad` was already computed with effective relativistic degrees of freedom that include the QCD plasma. That can count the same thermal energy twice.

For this reason v1 requires the single field:

```text
epsilon_background_GeV_fm3
```

and rejects split keys such as `rho_rad_GeV_fm3` and `rho_QCD_GeV_fm3`.

If a future version supports component decomposition, every component must carry an explicit disjointness/provenance contract before summation.

## 4. PSPI propagation rule

The PSPI principle is implemented as a descendant-propagation gate rather than as deletion:

| local gate | PSPI action | descendant input | history |
|---|---|---:|---|
| `PASS` | `ALLOW_LOCAL_RESULT_ONLY` | yes | preserved |
| `FALSIFIED` | `QUARANTINE_FROM_DESCENDANTS` | no | preserved |
| `TOKEN_VAZIO` | `HOLD_MISSING_EVIDENCE` | no | preserved |

`PASS` is deliberately local. The receipt always emits:

```json
"global_scientific_claim_allowed": false
```

because this gate alone cannot establish RLL preference over LambdaCDM/CPL.

This realizes the invariant:

```text
DO NOT PROPAGATE != DELETE
```

A failed ancestor remains in append-only provenance but is not silently inherited by descendant calculations.

## 5. Decision prerequisites

A numerical result can become `PASS` or `FALSIFIED` only when all of these are true:

1. `source_kind == real_data`;
2. source checksum/provenance is verified;
3. the baseline comparison is equivalent;
4. the EoS provenance is verified;
5. an explicit `max_abs_delta_h` constraint exists;
6. that constraint itself is verified.

Otherwise the state is `TOKEN_VAZIO`, even if the tool can calculate diagnostic numbers.

## 6. Input schema

Canonical schema:

```text
schemas/rll-qcd-primordial-input.v1.schema.json
```

Minimal **synthetic fixture** shape:

```json
{
  "schema": "rll.qcd_primordial_input.v1",
  "evidence": {
    "source_kind": "synthetic_fixture",
    "checksum_verified": false,
    "baseline_equivalent": false,
    "eos_provenance_verified": false
  },
  "constraint": {
    "max_abs_delta_h": null,
    "verified": false,
    "source": "TOKEN_VAZIO"
  },
  "reference": {
    "T_MeV": 150.0,
    "g_star_s": 20.0
  },
  "rows": [
    {
      "T_MeV": 150.0,
      "epsilon_background_GeV_fm3": 0.3,
      "epsilon_rll_GeV_fm3": 0.0,
      "g_star_s": 20.0
    }
  ]
}
```

The numbers above are **shape examples only**, not repository evidence; this fixture must resolve to `TOKEN_VAZIO`, never to a real-data verdict.

## 7. Execution

```bash
python tools/rll_qcd_primordial_gate.py INPUT.json \
  --output results/audit/rll_qcd_primordial_gate.json
```

To use the module as a hard CI/reproducibility gate:

```bash
python tools/rll_qcd_primordial_gate.py INPUT.json \
  --output results/audit/rll_qcd_primordial_gate.json \
  --require-pass
```

`--require-pass` exits nonzero for both `TOKEN_VAZIO` and `FALSIFIED`.

## 8. Bibliographic/professional reference layer

Machine-readable reference registry:

```text
data/inputs/qcd_primordial/qcd_bridge_manifest.v1.json
```

### Light-ion QGP/collectivity bridge

- ALICE Collaboration (2025), **Evidence of nuclear geometry-driven anisotropic flow in OO and Ne-Ne collisions at sqrt(s_NN)=5.36 TeV**, arXiv:2509.06428. First measurements of charged-particle elliptic and triangular flow in O-O and Ne-Ne at 5.36 TeV; hydrodynamic calculations including realistic nuclear structure describe the measurements and expose geometry sensitivity.
- CMS Collaboration (2025), **Collective flow in OO and NeNe collisions at sqrt(s_NN)=5.36 TeV**, CMS-PAS-HIN-25-009. Independent light-ion flow study used here only as QCD/hydrodynamic cross-check context.

### QCD equation of state candidates

- Bazavov et al. / HotQCD Collaboration (2014), **The equation of state in (2+1)-flavor QCD**, *Physical Review D* 90, 094503, DOI 10.1103/PhysRevD.90.094503, arXiv:1407.6387. Continuum-extrapolated thermodynamics and speed of sound across 130-400 MeV; this is the primary candidate for numerical crossover-regime ingestion.
- Bresciani, Dalla Brida, Giusti & Pepe (2025), **QCD Equation of State with Nf=3 Flavors up to the Electroweak Scale**, *Physical Review Letters* 134, 201904, DOI 10.1103/PhysRevLett.134.201904. High-temperature nonperturbative EoS coverage from 3 to 165 GeV; useful for extension above the crossover regime, not a replacement for the HotQCD crossover table.

## 9. Current evidence state

As of 2026-08-26:

```text
collider/QGP bridge references      = MATERIALIZED
QCD EoS bibliography                = MATERIALIZED
QCD EoS numeric table + checksum    = TOKEN_VAZIO
verified cosmological Delta_H bound = TOKEN_VAZIO
RLL QCD-era numerical verdict       = TOKEN_VAZIO until the above are closed
```

This is intentional: the implementation exists before the evidence is allowed to claim more than it supports.

## 10. Natural next evolution

The next reproducible cycle is:

1. ingest a licensed/open numerical or analytic HotQCD EoS representation with source hash;
2. derive or ingest a consistent `g_*s(T)` table without double counting;
3. materialize a published BBN/CMB/early-Universe constraint that can be translated into the gate's explicit observable;
4. implement the actual RLL `epsilon_RLL(T)` mapping from the model registry rather than from an ad-hoc parameter;
5. run the gate on matched baseline/RLL tables;
6. preserve the receipt and propagate only `PASS` ancestors.

That sequence converts the current conceptual bridge into a reproducible early-Universe falsification layer without upgrading evidence by rhetoric.
