# RLL Operator Lab V1 — Provider Evidence Index

**Tested implementation head:** `f7d1a4b0b9659b059be697f3f78512af6dcfb01b`  
**PR:** #996  
**Workflow run:** 36258384349  
**Job:** 108449381820  
**Provider conclusion:** SUCCESS

## Evidence

- `RLL_OPERATOR_LAB_CI_PROVIDER_RECEIPT_V1.json` — compact provider execution receipt.
- `RLL_OPERATOR_LAB_GIT_ANCHOR_V1.json` — branch-head + GitHub merge-ref identity binding.
- `RLL_OPERATOR_LAB_EVIDENCE_ENVELOPE_CI_V1.json` — exact envelope emitted by CI.
- `RLL_OPERATOR_LAB_EVIDENCE_ENVELOPE_PROVIDER_ANCHORED_V1.json` — successor envelope with verified Git anchors.

## Exact observed results

- 8 unit/mutation tests: PASS.
- 10 negative controls: PASS.
- 10 positive fixtures: PASS.
- receipt file SHA-256: `e09f240a8a7a16ae9d26fd906e5523ffee7d336340aef94d4c25e05a3b7dd9ec`.
- receipt payload SHA-256: `298b8a0d49befc3394b6b9846cb5a1626da668fa601adb67dbe9e0d82ff1f5b4`.
- CI envelope root: `725d6d827092968f9facc6342ecc186ba9e3fa2b1b94384f827644ee03e6501f`.
- provider-anchored successor root: `9e64ef64afc19a18690a132683ab568f613c528abafc52258473b77fb61131b2`.
- artifact ZIP SHA-256: `93b9b8e7390ccc654c06c0fdc6beb9cfef6dc3525eba13ff90ff48b9eec5c14e`.

## Boundary

The provider merge-ref is GitHub-signed and has the same tree as the tested branch head. The author branch-head commit itself is unsigned. This is provider/repository evidence, not ICP-Brasil/X.509 identity, RFC3161 trusted time, human non-repudiation or scientific claim validation.

`claim_allowed=false`
