# Schemas

## Status

`schema_registry / claim_bounded_contract_index`

## Purpose

This directory contains structural JSON Schema contracts used by the repository to validate metadata shape, graph/package coherence and claim-gated research artifacts.

These schemas are **contracts of structure**, not scientific validation artifacts.

## Claim boundary

```text
schema_parse_success != scientific_validation
schema_parse_success != RLL_confirmed
schema_parse_success != model_preference
schema_parse_success != peer_review
schema_parse_success != physical_claim
```

A schema can verify that an object has the required fields and claim gates. It cannot verify that a cosmological, mathematical, physical, institutional, legal or market claim is true.

## Canonical schemas

| Schema | Role | Claim state |
|---|---|---|
| `relational_validation_package.schema.json` | Structural contract for relational validation packages. | `claim_allowed=false` |
| `relation_graph.schema.json` | Structural contract for claim-bounded relation graphs. | `claim_allowed=false` |
| `information_evolution_trace.schema.json` | Structural contract for internal custody traces across information states, transformations, tests and epistemic gates. | `claim_allowed=false`; unknown origin remains `TOKEN_VAZIO` |
| `rll_run_manifest.schema.json` | Structural contract for field-level provenance of one scientific execution. | `claim_allowed=false`; partial absence cannot silently supersede prior evidence |
| `rll_epistemic_void.schema.json` | Structural contract for unknowns, contradictions, creative alternatives, falsifiers and objective exit conditions. | `claim_allowed=false`; creativity generates candidates, not evidence |
| `omega_artifact.schema.json` | Structural contract for RAFAELIA Ω living knowledge units. | epistemic status required |
| `omega_node.schema.json` | Structural contract for RAFAELIA Ω versioned semantic cells. | score fields are routing metadata |
| `omega_relation.schema.json` | Structural contract for RAFAELIA Ω weighted semantic relations. | preserves relation-weight formula |
| `omega_schema.json` | Structural aggregate for RAFAELIA Ω architecture state. | preserves canonical Ω equation |

## Omega examples

Minimal RAFAELIA Ω fixtures live in `schemas/examples/`. They are didactic examples for structural validation only: they do not validate scientific claims, promote metaphors to evidence, or close TOKEN_VAZIO gaps.

`schemas/examples/information_evolution_trace.example.json` demonstrates how an unknown remote origin remains `TOKEN_VAZIO` while subsequent transformations become internally traceable. It does not prove the historical origin or external validity of the represented information.

Validate the information-evolution contract and its contiguous example chain with:

```bash
python scripts/validate_information_evolution_trace.py
```

Validate the Omega schemas and examples with:

```bash
python3 scripts/validate_omega_schemas.py
```

Validate the RLL epistemic-void ledger with:

```bash
python tools/validate_epistemic_void.py --strict --write-report
```

The operational entropy emitted by this validator is a routing convention. It is not thermodynamic entropy, Shannon entropy, evidence or a scientific score.

## Required discipline

Every schema in this root should preserve:

1. a stable `$schema` declaration;
2. a non-empty `$id`;
3. a clear `title`;
4. a description that states the contract is structural;
5. explicit required fields;
6. `claim_allowed=false` when the artifact touches validation, relation mining, scientific claims or evidence promotion;
7. a `next_gate` or equivalent field when the object can move toward stronger review.

## Allowed interpretation

Allowed:

```text
This artifact matches a structural contract.
This artifact is claim-bounded.
This artifact can be routed to the next gate.
```

Blocked:

```text
This artifact validates RLL.
This artifact refutes LCDM/CPL.
This artifact proves a physical theory.
This artifact creates market/legal/institutional conclusion.
```

## Validation command

```bash
python tools/validate_schemas_claim_boundary.py
```

This validator checks the schema files themselves for minimal structural and claim-boundary discipline. It does not execute cosmology, validate physics, prove mathematics or promote any scientific claim.
