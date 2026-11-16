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

---

## Successor — provider merge and correct placement readback

Readback reference: `2026-10-28`, provider state only.

### Provider facts

- PR #1046: `MERGED` into `rll/lab`;
- accepted head: `89f718fe83b121e98e4bd23780c0a821c9bddb94`;
- merge commit: `52701b31a246c426ea398a5625234b1726969270`;
- exact-head gates recorded on PR #1046: 11/11 workflows `SUCCESS`;
- Python receipt: `2068 passed + 42 subtests passed` in `276.87s`;
- current `rll/lab` head: `7569b30617468a37584872c093ff3b3959e3a161`;
- ancestry check: current `rll/lab` is 345 commits ahead of the merge commit and 0 behind.

### Correct placement matrix

| Knowledge class | Canonical placement | State |
|---|---|---|
| raw ZIP source bytes | Drive folder `13B9hxoGZB5P552fF6DsOVl3vbrsYVmeW` | preserved outside Git history |
| stable source IDs, size, bounded hash/shape observations | `data/source_intake/2026-10-04/` on `rll/lab` | documented |
| custody/provenance contract | this GitHub receipt on `rll/lab` | successor appended |
| mutable operational state and provider events | Drive μWRITE ledger and CURRENT_STATE | successor required/read back separately |
| code, formulas, likelihoods and canonical scientific JSON | producer-owned GitHub paths | untouched |
| `rll/integration`, `rll/release`, `main` | maturity-gated destinations | no promotion inferred or performed by this successor |

### Promotion boundary

Provider branch comparison does not prove that this merge reached later maturity layers:

- `rll/integration`: diverged from the #1046 merge lineage at readback;
- `rll/release`: behind the merge lineage;
- `main`: diverged and retains its own older intake history;
- direct `lab -> main` promotion remains forbidden.

`CI_PASS != SCIENTIFIC_VALIDATION`. The scientific gaps remain unchanged:

- sources 001/002 independent byte rehash: `TOKEN_VAZIO_HASH_READBACK`;
- source 003 semantic schema and producer rule: `TOKEN_VAZIO`;
- source-to-RLL scientific mapping: `TOKEN_VAZIO_SOURCE_TO_RLL`;
- independent scientific reproduction: `TOKEN_VAZIO_REPRODUCTION`;
- global `claim_allowed=false`.

## Successor R3

```text
F_ok   = PR #1046 merge and exact-head CI are now provider-bound; knowledge classes are routed to GitHub or Drive by authority.
F_gap  = later maturity promotion, hashes 001/002, source 003 semantics/mapping and independent reproduction remain open.
F_next = review this successor through work -> rll/lab; never infer release/main or scientific promotion from custody success.
```
