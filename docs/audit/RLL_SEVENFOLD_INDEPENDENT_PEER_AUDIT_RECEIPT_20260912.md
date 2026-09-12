# RLL Sevenfold Independent Peer Audit V1 — append-only receipt

Date: 2026-09-12  
Authority: `instituto-Rafael/relativity-living-light`  
State: `IMPLEMENTED_UNEXECUTED`  
Claim allowed: **false**

## Why this exists

The RLL already separates source, artefact, execution, evidence and claim. This
receipt adds a stricter peer-review topology for false-positive resistance.

Each review round targets exactly one atomic claim or gap.

Seven isolated peer houses receive the same pinned input bundle. A house cannot
see any other house's verdict before sealing its own receipt.

Each house contains two internal sides:

1. `constructive_reconstructor` — reconstruct the strongest bounded claim
   genuinely supported by the source;
2. `adversarial_falsifier` — attack that frozen reconstruction.

Unresolved disagreement inside the pair is `INCONCLUSIVE`, never averaged away.

## Seven houses

1. `P1_PROVENANCE / Ω_SRC / ‡SOURCE_SCOPE_ABLATION`
2. `P2_IDENTITY / Ω_ID / ‡IDENTITY_COLLISION_ATTACK`
3. `P3_RUNTIME / Ω_RUN / ‡CLEAN_ROOM_REPLAY`
4. `P4_OBSERVABLE / Ω_OBS / ‡OBSERVABLE_BLIND_SPLIT`
5. `P5_SEMANTIC / Ω_SEM / ‡SEMANTIC_NEGATION_INVERSION`
6. `P6_SCIENCE / Ω_SCI / ‡NULL_MODEL_AND_ABLATION`
7. `P7_GOVERNANCE / Ω_GOV / ‡PROMOTION_BOUNDARY_ATTACK`

Each house owns seven mandatory checks.

[
7 	ext{houses}	imes7 	ext{checks}=49 	ext{checks per atomic target}
]

## False-positive controls

Forbidden:

- majority voting;
- compensatory averages;
- peer-to-peer verdict leakage before sealing;
- shared conclusion seed;
- converting `TOKEN_VAZIO` to zero/PASS;
- allowing one strong house to compensate a failed house;
- rewriting the source after the adversarial side starts;
- promoting a seven-house method PASS directly to a scientific claim.

Aggregation is fail-closed:

- any `FAIL_FALSIFIED` → review blocked;
- any `TOKEN_VAZIO` or `INCONCLUSIVE` → not promotable;
- all seven `PASS_BOUNDED` → method review passed, **claim still not allowed**;
- independent replication remains required.

## Semantic token networks

The framework allows every house to externalize its own semantic graph:

`source → claim → assumption → equation → observable → test → falsifier → receipt`.

This is an auditable representation built from the pinned source bundle.

It does **not** claim access to hidden model tokens, private chain-of-thought,
weights, embeddings or internal reasoning state.

Likewise, “free will” is not asserted. What is implemented is bounded
independence of search/reconstruction/falsification routes.

## Authorship

Peer houses are analytical roles, not legal authors.

AI/tool assistance must be recorded separately from human/project authorship.
A commit or hash can establish chronology/integrity of an observed artefact; it
does not, by itself, prove exclusive authorship.

## F_ok

- seven independent review houses defined;
- seven checks per house;
- unique Ω namespace and unique ‡ falsifier per house;
- constructive/adversarial pair inside each house;
- non-compensatory aggregation;
- externalized semantic graphs only;
- authorship boundary explicit.

## F_gap

- `TOKEN_VAZIO_SEVENFOLD_EXECUTION_RECEIPTS`;
- `TOKEN_VAZIO_INDEPENDENT_REVIEWER_INSTANCES`;
- `TOKEN_VAZIO_FIRST_ATOMIC_TARGET_EXECUTION`.

## F_next

Execute one atomic RLL claim/gap through all seven houses. The best pilot is the
highest-priority unresolved perturbation gap after the current canonical graph
is read, while keeping the seven peer verdicts isolated until receipt sealing.

SOURCE != CONFIG != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
