# RLL License Authority Reconciliation — 2026-09-25

**state:** `CONTRADICTION_PRESERVED / EDITORIAL_SUCCESSOR`  
**claim_allowed:** false  
**producer head observed:** `4ccd00625863e37604d2786afc77fb55598d3a83`

## Why this document exists

The repository already records a license-authority contradiction. This
successor makes that contradiction impossible to miss without silently changing
historical grants or the scientific corpus.

Observed surfaces:

1. `LICENSE.md` — custom `RAFCODE-𝚽 vΩ-EXTENDED` authorial/legal-symbolic
   surface (blob `26c69bb3c850bc2b3063621a5f72a2badc1535c2`);
2. `pyproject.toml` — `project.license.text = "MIT"`
   (blob `7b1bfc2bcaa7c48c4083cf2e0602a675cac49680`);
3. README/badges and historical documents point to mixed license descriptions;
4. `data/governance/RLL_ETHICS_LICENSE_FRICTION_LEDGER_20260816_V1.jsonl`
   already records this as a contradiction and explicitly says not to
   auto-rewrite the surfaces.

Therefore:

```text
LICENSE.md_CUSTOM != PYPROJECT_MIT
LICENSE_METADATA != AUTHORIAL_SYMBOLIC_TEXT
HISTORICAL_GRANT != SILENTLY_REVOCABLE
```

## Current authority state

There is no approved single canonical machine-readable license expression for
the entire repository at this checkpoint.

```text
canonical_repository_license = TOKEN_VAZIO_CONTRADICTION
```

Do not infer a stricter or more permissive grant by choosing whichever surface
is convenient.

## Relationship to RAFAELIA v1000

The 2026-09-25 RAFAELIA v1000 policy developed in
`rafaelmeloreisnovo/Rafaelia_Private` is **not automatically imported into
RLL**.

RLL contains:

- scientific code;
- papers/documents;
- externally sourced data;
- datasets with their own terms;
- historical public license statements;
- possibly independently licensed components.

Any future migration must be scoped by file/artifact and preserve rights
already validly granted.

## Scientific independence

License reconciliation must never change a scientific gate.

```text
LICENSE_DECISION != SCIENTIFIC_VALIDATION
COMMERCIAL_RIGHT != CLAIM_ALLOWED
COPYRIGHT != PHYSICAL_TRUTH
```

Negative and null scientific evidence must remain unchanged by legal/editorial
work.

## Required closure

A canonical license expression may be promoted only after:

1. file/component inventory;
2. separation of code, papers, data and third-party material;
3. identification of historical grants already made;
4. rightsholder/contributor authority review;
5. data-source license review;
6. explicit decision about future original RLL material;
7. synchronized update of `LICENSE.md`, package metadata, README, citation and
   machine-readable surfaces;
8. successor receipt.

Until then:

```text
auto_license_rewrite = false
commercial_clear = false
claim_allowed = false
```

## Immediate documentation rule

Readers must consult this reconciliation before treating the README license
badge, `pyproject.toml` or `LICENSE.md` as a complete repository-wide
license answer.

## R3

**F_ok:** contradiction is explicitly preserved and routed.

**F_gap:** canonical expression, file-level inventory, historical grant map and
legal review remain open.

**F_next:** produce the file/domain license inventory without changing
scientific results or prior public grants.
