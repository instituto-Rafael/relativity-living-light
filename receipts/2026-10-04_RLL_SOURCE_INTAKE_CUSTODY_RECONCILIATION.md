# Receipt — RLL source-intake custody reconciliation

## Identity

- repository: `instituto-Rafael/relativity-living-light`
- route: `work/rll-coherence-custody-hotfix-20261004 -> rll/lab`
- base commit: `175869778e8f1b690f9ead029efe1d7aceae0c35`
- change class: documentation/custody hotfix
- scientific code or formula mutation: `NONE`
- claim promotion: `NONE`

## Inputs read

- canonical scientific artifact: `results/structure_d/joint_real_likelihood.json`
- Drive custody folder: `13B9hxoGZB5P552fF6DsOVl3vbrsYVmeW`
- Drive manifest file: `1_N7I1M2FFuShSls5NIlD-CGbypq5ckKv`
- prior main intake: PR #1045, head `e16ea9a7376ae89dd892d3d2bdffd6d18def4ab4`, merge `ce69e6c7b9dc160d246318e6599ed69d5dc291ea`

## Custody observations

| Source | Drive file ID | Size bytes | Hash state | Semantic state |
|---|---|---:|---|---|
| 001 | `1swqfTf88AYI5Q5xyylz8awwx3Zq5fqie` | 48785143 | declared hash; `TOKEN_VAZIO_HASH_READBACK` | source only |
| 002 | `1fmma2jAR0N1ZqIJMvOilW5t7OAAtO4nn` | 10065647 | declared hash; `TOKEN_VAZIO_HASH_READBACK` | visual concept; not evidence |
| 003 | `1Vd6qmHf-ejKmY5HnCMjUB0MrtN2KjwUc` | 8706240 | SHA-256 `a2f9632a9b538d609c4b6745f27725627a626246a770dd8a6881107c28fa1e5f` verified | numerical matrix; semantics pending |

Source 003 contains `vetores_amor_cruzado.csv`, 18821256 bytes, 7778 rows including one header row, and 128 columns on every observed row.

## Delta

1. synchronized the paper table with the current canonical JSON;
2. separated scientific artifact state from repository CI state;
3. forward-ported source-intake custody to the governed lab route;
4. replaced the stale pending-ID gap with verified metadata readback;
5. preserved unverified hashes, semantics, mapping and reproduction as explicit `TOKEN_VAZIO` states;
6. added navigation and traceability routes for humans and machine agents.

## Gates

- `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`
- global `claim_allowed=false`
- branch maturity: PR must target `rll/lab`
- exact PR/CI receipt: pending provider execution
- independent scientific reproduction: `TOKEN_VAZIO_REPRODUCTION`
- source-to-RLL mapping: `TOKEN_VAZIO_SOURCE_TO_RLL`

## Rollback

Revert the single reconciliation commit or close the PR without merge. Raw Drive objects, scientific data, code, formulas and the canonical JSON are untouched.

## R3

```text
F_ok   = custody identities and source 003 byte/shape readback are bound to the governed documentation route.
F_gap  = hashes 001/002, semantic schema, source-to-RLL mapping, reproduction and CI remain open.
F_next = accept only reproducible receipts; keep claim promotion blocked.
```
