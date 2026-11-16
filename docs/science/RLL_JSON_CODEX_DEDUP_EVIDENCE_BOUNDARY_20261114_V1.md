# RLL Ω — JSON/JSONL deduplication and Codex provenance boundary (2026-11-14)

**Source authority:** `instituto-Rafael/relativity-living-light` (public code producer). **Review base:** `rll/lab@9ff4974d6b7082acee16cde91d665fd0e19ba0d6`. **Scope:** public Git-tracked JSON blobs, not the private Google Drive corpus. **Status:** `IMPLEMENTED_LOCAL_SYNTHETIC_TESTED / CI_NOT_YET_CONFIRMED / claim_allowed=false`.

## Observed initial baseline (N0 Git tree, 2026-11-14)
- Git tracked `rll/lab`: **3,639 blobs**, **3,458 distinct object IDs**, **83 groups with repeated blob IDs** across all file types.
- Filtering paths ending in `.json`, `.jsonl` or `.ndjson`: **762 files**, **740 distinct Git blob objects**, **11 groups of identical Git objects**, **22 additional paths** representing repeated blob objects.
- Most repeated JSON objects are archived run outputs or intentionally duplicated synthetic fixtures. Examples: `data/examples/bh_flux_presets.json` vs `data/synthetic/examples/bh_flux_presets.json`; `data/real/cosmology/real_source_signatures.json` vs `results/audit/real_source_signature_verification.json`; four historical runs with identical `formulas/formulas.json`.
- These are **structural Git-blob identities only**: not a global semantic formula dedup, not a license to delete files. They are a historical baseline at the specified commit; the runtime script adds a `.jsonl.txt` extension and reports exact scope.

## Reproducible implementation in this branch

`scripts/audit_rll_json_dedup.py`:
- Enumerates committed blobs at the specified Git commit; no filesystem traversal of untracked worktree, no network, no external Python packages, no provider secrets, no source modification.
- Records path, Git object ID, size and SHA-256 of directly accessed bytes. Object equality and SHA-256 equality are distinct evidence types.
- Parses `JSON`, `JSONL`, `NDJSON`, `JSONL.TXT` with canonical key order while preserving arrays, record order, Unicode content and scalar types. Rejects ambiguous duplicate keys, non-finite JSON numbers and malformed content; oversized inputs remain `SIZE_LIMIT` with null SHA.
- Identifies exact Git-object groups, JSON-syntax canonical equality across *different object IDs* and records duplicated across different files. Same basename or size alone is **not** a duplicate.
- Never stores or prints original JSON values in the receipt. Hashes are deterministic evidence pointers, not encryption.
- Refuses to overwrite a receipt; fail-safe exit code `2`. Prints `claim_allowed=false` and keeps scientific and semantic-equality claims separate.

Run from a checked-out RLL repository:
```sh
python -m unittest discover -s tests -p test_audit_rll_json_dedup.py -v
python scripts/audit_rll_json_dedup.py --repo . --rev HEAD --max-file-bytes 16777216 --output /tmp/rll-json-dedup-$(git rev-parse --short HEAD).json
```

The CI gate `.github/workflows/rll-json-dedup-gate.yml` executes the bounded audit on the exact PR head and writes only aggregate counts to its job summary. The detailed receipt remains in the runner's temporary filesystem; there is no public artifact upload. This gate is independent from the existing Poincaré 7D geometry gate and any cosmological fits.

## Authority separation and no-data-leak boundary

Private raw Codex archives, historical Drive DEDUP WAVE receipts, private SHA-256 manifests, provider file IDs and database rows remain exclusively in **Google Drive / private Supabase**. They are **not copied into this public repository**.

The private Supabase `raf_private.json_dedup_*` tables distinguish `METADATA_ONLY`, `HISTORICAL_RECEIPT` and `DIRECT_BYTES_VALIDATED`. The RLL script emits a *producer-side report schema*, not a credential-backed automatic writer to Supabase. Federation must be via separately authorized evidence receipts with an exact producer commit and readback. No historical RLL blob becomes an assertion about private Codex content.

## Gate table and falsifiers

| Gate | Status before CI | Falsifier |
| --- | --- | --- |
| G0 Tree and exact-blob census | OBSERVED_SCOPED at specified lab commit | Missing Git object / differing tree digest |
| G1 Synthetic JSON adversarial tests | LOCAL_PASS_SCOPED (8 unit cases) | Different content merged; null/false/zero conflated; duplicated keys accepted |
| G2 Full Git JSON canonical scan | IMPLEMENTED_UNTESTED_REMOTE | `PARSE_FAILED` or `SIZE_LIMIT` silently promoted to PASS |
| G3 Private Drive/Codex global corpus | NOT_RUN | Unread source invented as absent or duplicate |
| G4 Supabase private reconciliation | TOKEN_VAZIO_EXACT_PR_HEAD | Event references a commit other than this PR's actual head |
| G5 Science/physical claims | BLOCKED | Duplicate data interpreted as physical evidence |

**Rollback:** leave the work branch unmerged; supersede with another receipt/commit in a new branch, without deleting existing source blobs or archival outputs. The earlier isolated branch `audit/rll-poincare-isosceles-dedup-20261114-v1` is precedent, not an implied merge into `rll/lab`.

**R3:** `F_ok` = source-tree structural duplicates enumerated and local synthetic test implementation; `F_gap` = current exact-head CI, canonical pass over full RLL Git tree, private Drive/Codex exhaustive scan, scientific validation; `F_next` = verify exact-head CI and reconcile private Supabase receipt after code readback without exporting private content. 
