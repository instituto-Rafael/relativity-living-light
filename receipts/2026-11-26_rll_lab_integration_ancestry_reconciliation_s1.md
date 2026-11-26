# RLL — reconciliação de ancestralidade LAB / INTEGRATION

- mu_id: MU-RLL-LAB-INTEGRATION-ANCESTRY-20261126-S1
- SOURCE: PR #1251 merged, LAB 43fa8a3b103ab54973cb0198243ef06876608eee; PR #1222 merged, INTEGRATION 63c0cf749ed52c554aaa69b5cd0766c82e9b4b4a.
- merge-base: be9a2d91287a979f9a770561c5c11861529106e2; tree of merge-base and INTEGRATION: fe5f45c43b8008a5f82e259218ad424a9f55e427 (identical).
- LAB tree before correction: edc8f469daf362adf3b3ea0603a63be9a674d712.
- Observation: LAB ahead 81, behind 1; exact comparison 63 changed paths (47 additions, 16 modifications, no removals); the sole missing integration merge has no unique content relative to the common ancestor.
- Action: create isolated two-parent commit (LAB first, INTEGRATION second), preserve every LAB blob and mode, add only this receipt. Route via work branch -> rll/lab; no direct protected ref updates. Use a merge commit, not squash/rebase, if approved, to preserve both ancestries.
- Acceptance: exact tree delta against LAB is this receipt only; integration is an ancestor of the candidate; current-head mandatory CI and resolved review threads before merge; compare current refs again before downstream promotion.
- Rollback: do not merge if checks fail; preserve branch and evidence. If already merged, revert content changes through a reviewed successor; do not rewrite ancestry or force push.
- Prior CI evidence belongs to its original head. No scientific promotion, no writer activation, no automatic downstream merge. claim_allowed=false.
- Downstream observations: INTEGRATION -> RELEASE currently 1487 changed blob paths; RELEASE -> MAIN currently no commits ahead and 2722 behind. Direct global promotion is not approved by this receipt. Reconcile dependencies, critical deletions, evidence, and current main before the final edge.
