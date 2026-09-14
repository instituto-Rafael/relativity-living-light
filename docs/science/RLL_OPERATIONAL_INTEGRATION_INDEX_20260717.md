# RLL Operational Integration Index — 2026-07-17

**Branch:** `agent/rll-operational-integration-house-20260717`  
**Raw-data policy:** `immutable`  
**New-physics claim state:** `claim_allowed=false`

## 1. Delivery purpose

This index closes the structural integration cycle requested for mathematics,
knowledge, data governance, documentation and a single operational execution
home.

The delivery does not modify observational values. It adds executable operators,
source and branch registries, tests, CI, documentation and a synchronized
falsification roadmap.

## 2. Canonical reading and execution order

1. `docs/science/RLL_OPERATIONAL_INTEGRATION_HOUSE_20260717.md`
2. `data/registries/rll_operational_integration_registry.json`
3. `data/registries/rll_recent_primary_sources_2026.json`
4. `src/rll/structural_integration.py`
5. `tests/test_structural_integration.py`
6. `docs/science/RLL_RECENT_LITERATURE_INTEGRATION_20260717.md`
7. `docs/canonicos/19_ROADMAP_FALSIFICADORES_RLL.md`
8. `.github/workflows/rll-structural-integration.yml`

## 3. Implemented mathematical operators

```text
f(z)                       logistic RLL transition
rho_s(z)                   transition density fraction
w_eff(z)                   continuity-derived effective EoS
eta(z)                     cosmic distance-duality diagnostic
F_AP(z)                    Alcock–Paczynski ratio
Q=beta H rho               minimal interaction comparator
p_eff=p-3Hxi               bulk-viscous comparator
FRB residual               observed delay minus standard nu^-2 plasma term
SHA-256 payload hash       deterministic provenance primitive
branch readiness           required-artifact and TOKEN_VAZIO gate
```

## 4. Operational branches

| ID | Branch | Status |
|---|---|---|
| B00 | governance/provenance | implemented |
| B01 | logistic background | partial |
| B02 | BAO–SNe compatibility | partial |
| B03 | interacting dark sector | hypothesis |
| B04 | bulk viscosity | hypothesis |
| B05 | modified gravity/EFT | reference only |
| B06 | FRB/plasma propagation | hypothesis |
| B07 | photon-field/magneto-optical | hypothesis |

Each branch declares equations, observables, required artifacts and its own claim
boundary. A branch cannot borrow evidence from another branch silently.

## 5. Recent source integration

The source registry includes verified or metadata-verified primary records for:

- DESI DR2 BAO;
- Generalized Emergent Dark Energy;
- dissipative/bulk-viscous cosmology;
- interacting dark sectors;
- Anton–Schmidt dark energy;
- DESI–supernova distance crosschecks;
- distance-duality diagnostics;
- FRB/plasma/large-scale-structure relations;
- FRB cosmology review;
- ACT DR6 cosmic birefringence;
- dark-matter versus dark-energy birefringence inference.

Inclusion means `relevant comparator`, not `RLL validated`.

## 6. Commit ledger

| Order | Commit | Function |
|---:|---|---|
| 1 | `3bb31c4fd6ea4d66048c78ae17dbe12e3c77bf9f` | structural mathematical operators and gates |
| 2 | `bb4ff89c18998833fd7cc0f2da4780b4a812c26c` | recent primary-source registry |
| 3 | `3cd50835a2425bb855ff4247b0a86a29e375c2da` | operational branch registry and immutable-data policy |
| 4 | `95d41738d3b71487603dc30b26c724f37879e6ca` | fail-closed regression tests |
| 5 | `2ae44df5e43c1086a2fe986d82eb5a79d5b09b27` | canonical execution house |
| 6 | `94cfbbd20e31db63b0356047e3581eb496002f64` | recent-literature integration ledger |
| 7 | `5e74ae7fc0e6d8781489c08604d3ddddfbd6f362` | dedicated lightweight CI |
| 8 | `99bbe046f367d210e374f0e33b672e0a837dff0f` | synchronized falsification roadmap |

This index is intentionally the final documentation commit in the series.

## 7. Verification performed

An isolated local run of the committed test layer produced:

```text
PYTHONPATH=src python -m pytest -q tests/test_structural_integration.py
16 passed
```

The GitHub workflow repeats the same test in Python 3.11 with a five-minute
limit and no unnecessary scientific backend installation.

## 8. Execution invariants

```text
raw data immutable
all transformations versioned
compatibility before joint inference
same data/covariance for comparable baselines
metrics generate labels
missing artifacts block promotion
TOKEN_VAZIO remains explicit
negative results remain preserved
source proximity never implies equivalence
background and propagation evidence remain separated
```

## 9. Next executable work

### P0

- connect real BAO/SNe distance products to `eta(z)` and `F_AP(z)` reports;
- generate method/calibration sensitivity outputs;
- stop or branch posterior execution when compatibility is unresolved;
- unify full DESI and full SN covariance in the canonical posterior.

### P1

- execute the background tournament with GEDE, Anton–Schmidt, viscous and
  interacting baselines under the same data contract;
- define the physical identity of `Omega_s0`;
- derive conservation and perturbation stability.

### P2

- build independent FRB/plasma and polarization null-model pipelines;
- integrate CLASS/CAMB only after covariant and perturbative closure.

## 10. Claim boundary

The completed structure establishes operational integration and testable
mathematical objects. It does not establish a new cosmological component,
interaction, viscosity, modified gravity, nonstandard propagation, superiority
or independent replication.

`F_ok`: mathematics, sources, data policy, knowledge and documentation now share
one execution house.  
`F_gap`: real compatibility reports, unified posterior and physical closure remain
future executable gates.  
`F_next`: execute Gate 1 on real BAO/SNe distances before another global posterior.
