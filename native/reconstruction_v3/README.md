# Reconstruction V3 — bounded freestanding foundation

Authorizing request: implement the JSON reconstruction pipeline in RLL and Mapa.
Implementation authority: `instituto-Rafael/relativity-living-light`.
Federation route authority: `rafaelmeloreisnovo/Mapa`.

## Implemented and tested scope

`rv3.c` validates a complete JSON byte buffer and creates caller-owned tokens:
kind, byte span, containing token, and object-key span. No libc, heap, I/O,
floating point, or external dependencies are used by the kernel. Integers in
the JSON are retained as literal spans; the kernel never rounds their values.
Malformed JSON, invalid UTF-8, unpaired Unicode surrogates, storage exhaustion,
and container depth overflow return typed errors with zero valid output count.
Maximum supported container depth is 128; the hosted scanner chooses 64.
Recursion, conditionals and loops are used explicitly. This is not a branchless
or stackless implementation. Duplicate keys remain separate token identities.

The hosted `scan.c` adapter uses stdio and static buffers (16 MiB source,
262144 tokens); it rejects oversize inputs. `ingest.py` uses Python standard
library and SQLite, retaining exact original bytes and SHA-256, tokens, reported
status fields, missing reasons, literal references, candidate snapshots and
display-math candidates. These adapters are **not freestanding**. The kernel
does not implement SQLite or file persistence. Sources are private local input;
do not commit the database, exports, or original conversations to public GitHub.

## Reproduce

From repository root:

```sh
cc -std=c99 -O2 -Wall -Wextra -Werror -ffreestanding -fno-builtin \
  -fno-stack-protector -c native/reconstruction_v3/rv3.c -o /tmp/rv3.o
nm -u /tmp/rv3.o
cc -std=c99 -O2 -Wall -Wextra -Werror native/reconstruction_v3/rv3.c \
  tools/reconstruction_v3/scan.c -o /tmp/rv3-scan
python3 -m unittest discover -s tests/reconstruction_v3 -v
python3 tools/reconstruction_v3/ingest.py --scanner /tmp/rv3-scan \
  --database /private/output/reconstruction.sqlite /private/input/codex.json
```

Optional `--export-snapshots /private/output/observations` exports UTF-8 decoded
`path`/`file_path` plus `content` pairs under source SHA and containing-token ID.
Paths escaping the root are retained in the DB but skipped during export.
Existing different content is never overwritten. Use a private directory
without concurrent untrusted writers. These are candidate observed files,
not a complete Git checkout. No repository name or version order is invented.

## Evidence and limitations

Local five-test fixture suite PASS; freestanding native object has no undefined
symbols. Receipt: `receipts/reconstruction_v3/20260930-foundation.json`.
No ARM32/ARM64 runtime, real corpus ingestion, historical counts, external patch
retrieval, scientific validation, or semantic-equivalence claim is established.
The counts in the supplied audit remain AUDIT rather than asserted totals.

The API is **bounded full-document**, not an incremental stream parser. Large
documents require a future streaming implementation or explicitly raised
capacities. Never split a JSON document at arbitrary byte offsets. Python
retains the document and token output in memory; no claim of low-memory
processing for the 1.1 GB export is made.

References are observed literals with `resolution=PENDING`; a citation is not
execution evidence. Formula candidates are AUDIT and are not semantically
deduplicated, canonical, authorially attributed, or scientifically promoted.
No causal/commit ancestry is inferred from time order or co-occurrence.

## Remaining V3 gates

| Scope from the 20-point audit | State / next gate |
|---|---|
| Snapshots, missing content, diff external IDs | Field indexing implemented; exact real-schema binding and completeness gate NOT_RUN |
| Repositories, file versions, commits, PRs | Candidate content export only; repository/ref binding and graph resolution PENDING |
| Turns, branches, attempts/failures | Literal references and reported statuses indexed; explicit linkage PENDING |
| Source code functions/APIs/dependencies | Language parsers and provenance spans PENDING |
| Formula equivalence and genealogy | Display-math candidates AUDIT; domains, definitions and equivalence proof PENDING |
| Concepts, ontology, claims/evidence, decisions | Typed ontology/classification with excerpt evidence and calibrated labels PENDING |
| Citations, terminal output, assets | Selected field indexing; schema-specific joining and execution gates PENDING |
| Technical reasoning dataset | Pair/schema binding, privacy classification and quality gates PENDING |
| Complete knowledge graph | Parent/key token graph implemented; semantic graph and unresolved-edge reconciliation PENDING |

Rollback: discard the review branch; existing scientific pipelines, ontology
states, federation gaps and bootstrap are unchanged. No auto-merge is requested.
