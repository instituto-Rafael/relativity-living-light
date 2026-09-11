# RLL SECRET AUTHORITY BOUNDARY — PREFLIGHT V3

- date: 2026-09-11
- parent: `receipts/2026-09-11_RLL_SECRET_AUTHORITY_BOUNDARY_PREFLIGHT_V2.md`
- branch: `security/rll-secret-boundary-20260911`
- target: `rll/lab`
- state: `IMPLEMENTED_UNTESTED_AFTER_PRECISION_DELTA`
- claim_allowed: `false`
- publication_effect: `NONE`

## Delta since V2

- narrowed GitHub PAT evidence wording from generic authenticated-read language to `PASS_TOKEN_ACCEPTED_FOR_REPOSITORY_READ`;
- explicitly preserves the boundary that a successful public-repository GET does not prove complete organization/group authority;
- hardened JWT metadata parsing to absorb malformed Base64 as a sanitized non-secret state instead of an unhandled parser exception.

## Evidence boundary

```text
CODE_DELTA = PRESENT
EXECUTION_AFTER_V3 = TOKEN_VAZIO
PASS_AFTER_V3 = TOKEN_VAZIO
GROUP_AUTHORITY_VERIFIED = TOKEN_VAZIO
CLAIM_ALLOWED = false
```

## F_next

Use only fresh CI from the V3 head as execution evidence. Do not reuse green checks from superseded heads.
