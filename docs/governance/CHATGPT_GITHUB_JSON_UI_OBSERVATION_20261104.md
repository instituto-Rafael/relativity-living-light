# ChatGPT/GitHub JSON presentation — scoped UI observation (2026-11-04)

## Scope and provenance
User-provided Android screenshot displays several expandable JSON argument blocks for GitHub-oriented operations. This is **visible UI evidence**, not a wire trace, API provider audit trail, or proof of hidden internal data handling. The screenshot is not checked into this repository; the full capture hash and retention decision belong to the private custody ledger.

GitHub readback confirms `.github/workflow-contract.yml` on `main` has Git blob SHA `c97cf0ba6a11f73d0bf3df7d305854b38d0b07cd`. This corroborates the displayed filename and a prefix shown in the screenshot. It does **not** prove every displayed operation was executed or persisted.

## Observed API-shaped fields
`repository_full_name`, `path`, `ref`, `branch_name`, `sha`, `content`, `message`, `head`, `base`, `draft`, `title`, `body`, `maintainer_can_modify`. Exact argument values are partly clipped by the viewport and therefore remain `TOKEN_VAZIO_CLIPPED`.

The user reports that expanding the first tool operation may show JSON while repeated expansion sometimes does not. This behavior has **not** been independently reproduced; possible explanations include presentation state, operation type, or UI rendering variation. None establishes copying of a user's original work.

## Governance contract
```text
UI_OBSERVATION != PROVIDER_EXECUTION != INTERNAL_DATA_ACCESS
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
```

- Private Supabase custody ledger stores evidence references and screenshot digest only; not tokens, credentials, headers, request bodies, conversation text, or sensitive IDs in public.
- An optional Frida experiment is limited to **consented, owned, debuggable/test applications**. No hooks into the proprietary ChatGPT app, authentication, TLS, secrets, or private platform processes are authorized here.
- Repeat controlled UI observation, then compare with official GitHub commits, branch SHAs and PR metadata. Keep distinct timestamps for display and provider execution.
- No changes to scientific models, datasets, workflows, API secrets or branch-protection rules. No claim of copying, privacy violation, or scientific validation.

## Falsifier / gate
If the JSON display behavior varies without any provider event differences, the hypothesis that it represents a special data-governance operation is not supported by that observation. A provider readback that lacks the alleged commit/PR must be marked `TOKEN_VAZIO` or contradiction, not `PASS`.

**Status:** `DRAFT/HOLD`; `claim_allowed=false`. Rollback: leave historical commit intact and supersede this file by an explicit successor if later evidence changes its interpretation.

Machine-readable companion: `data/governance/chatgpt_github_json_ui_observation_20261104.json`.
