# PRE-PAPER — RLL Operator Lab + Evidence Envelope Bridge V1

**Date:** 2026-09-26  
**State:** PRE_PAPER / BEFORE_IMPLEMENTATION / APPEND_ONLY / claim_allowed=false  
**Repository authority:** instituto-Rafael/relativity-living-light  
**Parent main:** 7831d4b862779860e6d0fe70e7601631fd782e98

## 0. Intent

Integrate the tested typed-domain executor concept from the Papers session atlas into RLL as an isolated **Operator Lab** that cannot silently promote physics claims.

The lab will:
- execute only a fixed, reviewed operator whitelist;
- run negative controls before positive fixtures;
- emit a deterministic receipt and manifest;
- remain outside canonical Rx formula selection;
- remain outside SCI_GATE closure;
- expose its receipt to an RMR-ZIPRAF Evidence Envelope V1 bridge.

## 1. Authority split

RLL is the implementation authority for this runtime.

Papers precursor:
- repository: rafaelmeloreisnovo/papers
- PR: #108
- implementation precursor commit: 03efd335ee7b1bfd7e77c6fa61873c19b0ee437f
- current audited branch head observed before this delta: c4a59abcfcb8761e7ed4f7d3296d7110d00c2336

The RLL lab does not import code at runtime from Papers and does not depend on the Papers branch being merged.

## 2. Scientific boundary

\[
OperatorLab \neq PhysicsContract \neq FormulaSelection \neq SCI\_GATE\ Closure.
\]

No path emitted by Operator Lab may become a cosmological equation, physical constant, likelihood term or claim merely because:
- it is mathematically defined;
- it passes local fixtures;
- it has a receipt;
- it is included in an Evidence Envelope.

Promotion requires a separate, explicit physical derivation and scientific-gate evidence.

## 3. Fail-closed requirements

The lab SHALL enforce:
- \`claim_allowed=false\`;
- \`physics_binding=false\`;
- \`scientific_gate_effect=NONE\`;
- \`training=false\`;
- \`ai_runtime=false\`;
- \`network=false\`;
- \`dynamic_eval=false\`;
- \`dynamic_exec=false\`;
- \`arbitrary_shell=false\`;
- internal operator allowlist only.

Unsupported operators return \`BLOCKED_UNSUPPORTED\`.

Domain/type/branch failures return typed blocked states and stop the remaining path.

## 4. Negative-first invariant

\[
NegativeControls(P)\rightarrow PositiveFixtures(P).
\]

A suite is \`FAIL_CLOSED\` if:
- a required negative fixture unexpectedly passes;
- its expected falsifier/reason is absent;
- no negative fixture exists;
- a positive fixture diverges after negative controls pass.

## 5. Initial runtime subset

V1 will carry the same bounded stdlib-only subset tested in Papers:
- identity;
- reciprocal;
- natural/base/iterated logarithm;
- exponential;
- restricted real power;
- sine/cosine/tangent/arctangent;
- degree/radian conversion;
- real nth root/square root;
- Euclidean norm.

The full operator registry remains larger than the executable subset.

## 6. RLL receipt

The first RLL Operator Lab run SHALL emit a receipt containing:
- schema/version;
- run_id;
- source refs;
- suite hash;
- negative/positive counts;
- observed states;
- receipt SHA-256;
- repo ref;
- boundary flags;
- claim_allowed=false.

This receipt is execution evidence only.

## 7. Evidence Envelope bridge

The bridge SHALL embed/reference the RLL receipt as an artifact in an RMR-ZIPRAF Evidence Envelope V1 compatible object.

Conceptual chain:

\[
RLL\ OperatorLab
\rightarrow Receipt
\rightarrow SHA256
\rightarrow EvidenceEnvelope
\rightarrow ExternalAnchors.
\]

The bridge does not self-verify:
- BLAKE3 unless a real provider is present;
- Ed25519 unless signature/public key is supplied;
- X.509 / ICP-Brasil certificate paths;
- RFC3161 timestamp tokens.

Missing external providers remain \`TOKEN_VAZIO\` / \`NOT_PRESENT\`.

## 8. Git anchor

The first closure available in this cycle may be a verified Git commit reference:
- commit object exists;
- tree/parent identity matches;
- GitHub signature state recorded exactly.

A Git commit reference is not equivalent to human identity, certificate validation or trusted timestamp.

## 9. No canonical Rx mutation

V1 SHALL NOT modify:
- \`rx/orchestrator.py\`;
- \`configs/rx_physics_contracts.json\`;
- formula bindings;
- SCI_GATE executor registry.

Integration is additive and isolated.

## 10. Reproduction boundary

Local deterministic fixtures can produce TESTED evidence.

Independent reproduction requires an orthogonal runtime/provider and is not claimed by this delta.

## 11. Rollback

Implementation occurs on:
\`feat/rll-operator-lab-evidence-envelope-v1-20260926\`.

Main remains unchanged until review/merge.

R3=<F_ok: RLL integration contract frozen before code; F_gap: runtime implementation, receipt, envelope bridge, CI and external anchors; F_next: implement isolated lab + negative-first tests + envelope bridge without changing canonical Rx>.
