# RLL — Zero-dependency module matrix V1

Date: 2026-09-23
State: ENGINEERING_ROUTE / CLAIM_BLOCKED
Invariant: SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.

## Purpose

This matrix separates three goals that must not be conflated:

1. active zero-third-party runtime — deterministic RLL execution from Python stdlib and project-owned C/ASM;
2. legacy dependency retirement — older repository families migrate only after a parity gate;
3. scientific external references — CLASS/CAMB, official covariance/data releases and independent implementations remain external evidence or benchmark authorities where replacing them would change the scientific question.

Migration rule: port -> parity gate -> add/switch route -> preserve legacy -> rollback.

No global search/replace is authorized.

## Module matrix

| Need | Historical external surface | Project-owned route | State | Gate / boundary |
|---|---|---|---|---|
| scalar math, integration, matrix operations | NumPy/SciPy | rx/kernel.py, rx/freestanding_math.py | ACTIVE | Rx selftest + freestanding65 parity |
| cosmological background LCDM/wCDM/CPL/RLL | NumPy/SciPy | rx/cosmology.py | ACTIVE | versioned physics contracts; claim blocked |
| fairness statistics AIC/AICc/BIC, S8, covariance readiness | NumPy | rx/fairness.py | NEW_STDLIB_ROUTE | tools/validate_rx_fairness.py |
| CSV/JSON tabular IO | pandas/NumPy | rx/kernel.py | ACTIVE | family-specific serialization parity |
| bounded HTTP reads | requests | rx/http.py | ACTIVE_BOUNDED | read-only host/security gate |
| YAML configuration subset | PyYAML | rx/yaml_subset.py | ACTIVE_BOUNDED | not a general YAML claim |
| JSON-schema subset | jsonschema | rx/schema_subset.py | ACTIVE_BOUNDED | not a full JSON Schema implementation |
| plots | matplotlib | authored SVG writers in rx/kernel.py | ACTIVE | plot migration gate |
| deterministic optimizer | SciPy optimize | rx/kernel.bounded_coordinate_search | ACTIVE_BASELINE | algorithm differs; contract-specific parity required |
| posterior sampling baseline | emcee | rx/inference.py bounded random-walk Metropolis | NEW_BASELINE | deterministic gate; emcee parity remains TOKEN_VAZIO |
| nested Bayesian evidence | dynesty | none | TOKEN_VAZIO | do not substitute a different algorithm silently |
| astronomy convenience APIs | astropy | domain-specific ports required | TOKEN_VAZIO | only exact used semantics should be ported |
| growth/Boltzmann reference | CLASS/CAMB | internal approximate growth exists | EXTERNAL_BENCHMARK_REQUIRED | do not rebrand approximation as Boltzmann parity |
| Pantheon+ full-covariance evidence | external data release/provenance | project loader/materializer routes | PARTIAL | data/hash/covariance gate, not a library-rewrite problem |
| low-level deterministic execution | libc/libm/runtime helpers | core/lowlevel_runtime C/ASM/Q16 | ACTIVE_BOUNDED | undefined-symbol/dynamic-dependency + physical target gates |
| 65-observation Rx/C parity | Python/C representation | rx/freestanding_math.py + C joint65 | VERIFIED_ENGINEERING_PARITY | exact Q16 receipt parity; not model preference |
| installation/package defaults | heavy legacy Python stack | requirements-rx.txt repo route | OPEN_PACKAGING_BOUNDARY | base wheel still preserves legacy dependencies; decouple only with CLI/install compatibility gate |

## Authorship and provenance boundary

The project can own its implementation, ABI, tests, fixed-point representation,
receipts and orchestration. Standard mathematics and external observational
datasets keep their original provenance. Reimplementing Simpson integration,
Metropolis sampling, covariance algebra or cosmological baseline equations does
not make the underlying method a new scientific invention.

CLASS/CAMB have a different role: independent Boltzmann-code references.
Removing them from the active runtime is valid. Removing them from the
verification strategy would weaken evidence.

## Remaining dependency program

Priority after this delta:

1. close scalar fairness consumers against rx/fairness.py with explicit parity vectors;
2. migrate one SciPy optimization family at a time where the result contract permits;
3. use rx/inference.py only as a deterministic baseline; keep emcee parity open;
4. implement and validate a nested-evidence route before retiring dynesty;
5. port astropy consumers according to the exact units/coordinate semantics used;
6. decide the packaging boundary only after installed-CLI compatibility is proven;
7. keep CLASS/CAMB as optional external benchmark gates;
8. do not select RX-PHYSICS-CANONICAL-V2 until Omega_r, growth semantics, r_d/r_s/CMB semantics and the H(z) surface are explicitly resolved.

## Rollback

All additions in this slice are additive. Existing NumPy/SciPy/emcee/dynesty
routes are not deleted or rewritten. Reverting the branch removes the new
stdlib surfaces without changing datasets, physics contracts, historical
results or receipts.

claim_allowed=false
