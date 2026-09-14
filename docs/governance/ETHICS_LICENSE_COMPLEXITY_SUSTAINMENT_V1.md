# Ethics / License / Complex-Network Sustainment V1

## Purpose

This layer reduces operational friction between authorial ethics language, repository licensing, provenance, uncertainty, complex-network routing and executable governance. It preserves source material and adds typed boundaries beside it.

Canonical machine-readable contract:

`governance/ethics_license_complexity_sustainment.v1.json`

Validator:

`tools/validate_ethics_license_complexity_sustainment.py`

Adversarial tests:

`tests/test_ethics_license_complexity_sustainment.py`

Parable router:

`docs/governance/RAFAELIA_OPERATIONAL_PARABLES_V1.md`

## Non-destructive rule

The source texts `LICENSE.md` and `newadd/06_ETHICS_SYSTEMS.md` are not rewritten by this change. Their original authorial language remains addressable. This layer only states what may or may not be inferred operationally from those texts.

## Friction matrix

| Interface | Friction | Operational reduction | Residual state |
|---|---|---|---|
| LICENSE ↔ machine scanners | custom license is not a standard SPDX license | local `LicenseRef-RAFCODE-PHI-vOmega-EXTENDED` routing metadata | `TOKEN_VAZIO_LICENSE_SPDX_COMPATIBILITY` |
| LICENSE ↔ legal effect | repository prose and enforceability are different objects | `legal_effect_claim=false` | `TOKEN_VAZIO_LICENSE_ENFORCEABILITY_REVIEW` |
| repository ↔ third-party material | repository-level declaration cannot establish every external artifact's rights | `BLOCK_UNTIL_RIGHTS_RECORD` | `TOKEN_VAZIO_RIGHTS_PER_ARTIFACT` |
| Ethica[8] ↔ executable controls | values are named but not all are measurable | map symbolic values to governance controls first | `TOKEN_VAZIO_ETHICA_OPERATIONAL_METRICS` |
| ethics ↔ physical-field language | physical-language claim has no frozen measurable field test | model/ontology status only | `TOKEN_VAZIO_ETHICS_PHYSICAL_FIELD_EVIDENCE` |
| Phi_ethica ↔ stability | Lyapunov candidate is not yet a complete scoped stability proof | require domain/sign/equilibrium proof receipt | `TOKEN_VAZIO_LYAPUNOV_STABILITY_PROOF` |
| complex-network design ↔ runtime | network is specified but not yet evidenced by a dedicated run receipt | validator + CI | `TOKEN_VAZIO_COMPLEX_NETWORK_RUNTIME` |
| internal ethics ↔ external review | internally coherent controls are not independent review | preserve internal status | `TOKEN_VAZIO_INDEPENDENT_ETHICS_REVIEW` |

## P0 priorities

1. Keep legal-effect claims blocked until a concrete use has the needed review/instrument.
2. Build an artifact-level rights ledger for redistributed third-party inputs and outputs.
3. Keep the physical-field interpretation of ethics unpromoted until variables, units, observables, baseline and falsifier are frozen.

These P0 items prevent the highest-value false promotions: legal certainty without review, redistribution without rights provenance, and physical interpretation without measurable evidence.

## Complex-network invariants

The contract is a typed directed multigraph. Node count and edge count are structural measurements only. They are never a truth score.

Required edge fields:

```text
id
source
target
relation
provenance
claim_boundary
```

Required gap fields:

```text
id
state=TOKEN_VAZIO
urgency
domain
cause
evidence_needed
falsifier
F_next
closure_policy=STRUCTURED_RECEIPT_REQUIRED
```

A closure receipt must contain:

```text
schema=rll.token_vazio_closure_receipt.v1
gap_id
artifact_path
sha256
commit_sha
result
claim_allowed=false
```

## Anti-regression

The validator rejects:

- claim/legal/certification promotion inside this governance layer;
- standard-SPDX equivalence invented for the custom license;
- third-party redistribution defaulting to allow when rights are unknown;
- dangling graph edges;
- duplicate nodes, edges or TOKEN_VAZIO IDs;
- deletion or mutation of historical graph relations;
- disappearance of TOKEN_VAZIO without a structured closure receipt;
- parable promoted to proof;
- physical-field status silently promoted from TOKEN_VAZIO;
- removal of measurable runtime boundaries from the symbolic no-limit phrase.

## Ethics-by-Design operational translation

This V1 does not attempt to numerically score moral values. It maps selected values to controls that are already testable:

```text
Verdade          → evidence_before_claim
Humildade        → TOKEN_VAZIO_instead_of_invention
Responsabilidade → provenance + receipt + rollback
Coerência        → invariants + anti-regression
Liberdade        → exploration in work branches without premature promotion
Consciência      → explicit claim boundaries
Serviço          → reconstructible outputs usable by another agent
```

Any future numeric Ethica[8] scheduler must declare its scale, uncertainty, adversarial examples and non-circular falsifier.

## Parable boundary

The internal chain

`ESTATÍSTICA → TOKENS → METÁFORAS → VECTORES → PALAVRA → PROMESSA → Ωⁿ`

is a routing model. It means:

`measurement → explicit unknowns → conceptual bridge → typed relation → specification → falsifiable contract → audited iteration`.

The phrase “nenhum limite é real” is retained as a motivational parable only. Operational limits remain real, measured and enforced.

## R3

```text
F_ok:
  - authorial source text preserved
  - boundaries typed beside source text
  - 8 useful TOKEN_VAZIO entries recorded
  - complex network has stable IDs and provenance
  - anti-regression rules are executable
  - parables have internal routes without evidence promotion

F_gap:
  - legal-effect review
  - per-artifact rights ledger
  - Ethica[8] measurable metrics
  - stability proof closure
  - physical-field evidence
  - independent ethics review
  - first runtime receipt for this exact registry

F_next:
  execute validator and full Python CI; preserve the receipt; then close only those gaps for which new evidence actually exists.
```
