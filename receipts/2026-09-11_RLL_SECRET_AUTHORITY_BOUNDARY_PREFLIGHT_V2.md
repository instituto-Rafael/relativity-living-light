# RLL SECRET AUTHORITY BOUNDARY — PREFLIGHT V2

- date: 2026-09-11
- parent: `receipts/2026-09-11_RLL_SECRET_AUTHORITY_BOUNDARY_PREFLIGHT.md`
- branch: `security/rll-secret-boundary-20260911`
- target: `rll/lab`
- repository: `instituto-Rafael/relativity-living-light`
- state: `IMPLEMENTED_UNTESTED_AFTER_SECURITY_DELTA`
- claim_allowed: `false`
- publication_effect: `NONE`

## Delta since V1

- added canonical `SECURITY.md`;
- extended `.github/CODEOWNERS` to cover:
  - `tools/rll_secret_boundary_assurance.py`;
  - `tests/test_rll_secret_boundary_assurance.py`;
  - `SECURITY.md`.

## Security policy additions

- secrets/PAT/JWT/private keys must never be committed or copied into public reports;
- exposure requires revocation/rotation, not only masking;
- same-repository CI defaults to `github.token`;
- external/cross-repository PAT authority remains explicit and isolated;
- Climate trial and future dataset credential remain separate lifecycles;
- private vulnerability reporting is used only when externally available;
- unavailable platform security settings remain `TOKEN_VAZIO_EXTERNAL_SETTING`.

## Provenance boundary

V1 remains immutable historical preflight. V2 supersedes only the implementation inventory, not V1's evidence statement.

```text
SOURCE_OBSERVED = true
IMPLEMENTATION_PRESENT = true
EXECUTION_AFTER_V2 = TOKEN_VAZIO
PASS_AFTER_V2 = TOKEN_VAZIO
CLAIM_ALLOWED = false
```

## F_next

Re-run PR gates for the new head. Merge into `rll/lab` only on fresh green evidence. Credential execution remains a separate runtime receipt.
