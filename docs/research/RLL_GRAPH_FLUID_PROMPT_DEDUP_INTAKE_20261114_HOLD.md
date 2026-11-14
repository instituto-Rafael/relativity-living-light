# RLL Ω — Scientific cross-domain intake and prompt/workflow dedup (HOLD)

**Date:** 2026-11-14. **Status:** OBSERVED_SCOPED / REVIEW_ONLY / claim_allowed=false.
**Producer authority:** instituto-Rafael/relativity-living-light (this repository). **No PR, merge, release or science claim authorized by this note.**

## Scope and boundaries

- This is a *scientific methods intake*, not a change to the RLL cosmology model and **not** validation of RLL versus ΛCDM.
- Continuous mechanics: mass continuity, momentum/Navier–Stokes, heat advection–diffusion, rotating/stratified boundary conditions.
- Conservative discretization: integrate physical fluxes over finite-volume faces, then represent signed directed transfers in a graph. Correlation edges are **not** proof of causal transport.
- Observability: distinguish states not identifiable from available observations; METAR is atmospheric station data, not deep-ocean measurements.
- Number theory/prime moduli: possible computational indexing/coprimality tests; no physical mechanism follows solely from prime structure.
- Topological features do **not** resolve Bonnet-pair ambiguity in general; intrinsic topology alone does not distinguish two noncongruent isometric immersions with the same mean curvature. Extrinsic geometric information is required.

## E01 — proposed falsifiable numerical baseline

1. Define units, domain, control-volume mesh, time step, boundary conditions and known initial tracer/temperature field.
2. Build a conservative finite-volume flux solver and an equivalent directed-flux graph.
3. Compare per-step global budget, local residual, positivity, resolution/time-step sensitivity and a manufactured solution.
4. Only then evaluate neural/graph approximations against the classical solver, with out-of-distribution tests.
5. Record negative results and all execution environments. **NOT_RUN:** implementation, CI, ARMv7, AArch64 and physical observations.

## Prompt/workflow corpus provenance (private-source boundary)

- Connected Gmail account: user-provided; raw mail must remain in Gmail/authorized private records.
- Read-only discovery sample: 46 messages returned by a bounded search for workflow/prompt terms; 20 had an extractable “Original prompt” span.
- Normalization used for a preliminary exact comparison: Unicode NFC, collapse Unicode whitespace, locale-aware lowercase. Among the **20 extracted spans**, 20 distinct normalized texts and **0 exact collisions** were observed. This is *not* corpus-level deduplication or evidence that every span is complete.
- Candidate overlap, **not** equivalence: UserLAnd PR #269 vs #270 (CI/validation); florisboard PR #28 vs UserLAnd PR #95 (Android APK automation). Compare the full original instructions and their repo-specific constraints before asserting semantic duplication.
- Existing RLL source `src/rll/latentes.py` implements `ucase_prompt` and a SHA-256-based normalized prompt token unit; its current behavior is not a cross-source dedup engine. Canonical content identity, equivalence classes and exact provider coverage remain untested.
- Never publish Gmail excerpts, private ChatGPT Project bodies, mail IDs or private Drive contents in public GitHub.

## Related existing RLL material

- `docs/validation/prompts/RLL_REAL_VALIDATION_PROMPT.md` — conservative Pantheon+ comparability/claim gate; unchanged.
- `src/rll/latentes.py` — existing prompt normalization and seven-direction semantic representation; unchanged.
- `docs/canonicos/INTEGRACAO_3_UNIVERSOS_RAFAELIA.md` — geophysical hypotheses cannot become cosmology validation by analogy.
- `docs/science/RLL_CLIMATE_TORNADO_IONOSPHERE_30MIN_FREESTANDING_V1.md` — prior explicit missing-fluid-budget gates.

## Candidate references, discovery only — not reproduced or scientifically verified here

- https://arxiv.org/abs/2601.02157 — graph-based multi-fidelity Navier–Stokes learning
- https://arxiv.org/abs/2309.12077 — stochastic Navier–Stokes under location uncertainty for ocean modeling
- https://arxiv.org/abs/2412.16353 — structure-preserving stochastic shallow-water numerics

## Gates and rollback

`SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM`. 
`TOKEN_VAZIO_CONTENT_SHA256`; `TOKEN_VAZIO_FULL_PROMPTS`; `TOKEN_VAZIO_CROSS_PROVIDER_EQUIVALENCE`; `NOT_RUN_E01`; `claim_allowed=false`.

Falsifiers: exact normalized collision, incorrect extraction truncation, nonconservative flux budget, false claim of provider completeness, dissimilar repo-specific tasks merged as one.

Rollback: leave this isolated review branch unmerged; corrections use successor commits. Preserve every original prompt and email. R3: `F_ok=source paths and bounded extraction observed`; `F_gap=semantic/manual and full-corpus review`; `F_next=compare complete prompt pairs with source-bound results and test E01`.
