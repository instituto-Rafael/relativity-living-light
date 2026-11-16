# RLL — Anterioridade geométrica, NOVOexport × GitHub × alphaXiv (2026-10-08)

**Status:** scoped provenance crosswalk; `claim_allowed=false`; `publication_ready=false`.  
**Machine-readable source:** `data/governance/RLL_GEOMETRY_PRIOR_ART_CROSSWALK_20261008_V1.json`  
**Validator:** `python3 tools/validate_geometry_prior_art_crosswalk.py`  
**Tests:** `python3 -m unittest tests/test_geometry_prior_art_crosswalk.py`

## Evidence and epistemic chronology

The private `CONVERSATIONS_CHUNKS_PRIVATE` report `memory_bridge/reports/NOVOEXPORT_TOKEN_GENEALOGY_RETRO_000_010_V1.md` records a `USER_INPUT` container occurrence of `√3/2` at **2025-10-16 08:36:51.144650 UTC**, scoped to shards `000..010`. It explicitly warns that input-container role does not prove original lexical authorship. The index was committed on **2026-09-28 11:00:25 UTC** at `865e1d13d7d962168f6121ea1267c6e242ed3361`, blob SHA `490d956c8b487641acc9f67820149dfb236f2790`. These are **distinct timestamps**. They do not establish third-party timestamp notarization of the 2025 message.

## Exact notation falsifier — scope-limited source verification

A private raw-source readback confirmed the shard SHA-256 against a historical Drive custody receipt and matched one user-role source message and UTC timestamp, with no message text published. The original source contains two mathematical forms:

- `sqrt(3)/2`, with squared value `3/4`.
- `sqrt(3/2)`, with squared value `3/2`.

They are distinct positive real values. Treating them as a single expression would create a false identity. A scoped validator and two negative tests now reject that confusion. This does not prove an original polygon reconstruction theorem or publication priority.

## Reviewed external literature

| arXiv | First posted (arXiv v1) | Chronology versus indexed 2025 token | Specific mathematical connection |
| --- | --- | --- | --- |
| [2607.01423](https://arxiv.org/abs/2607.01423) — *On Reconstructing a Convex Polygon from Partial Information* | 2026-07-01 | Indexed token earlier | The paper studies polygon reconstruction from partial constraints; an isolated `√3/2` occurrence is **not** an equivalent reconstruction algorithm or theorem. |
| [2408.06928](https://arxiv.org/abs/2408.06928) — *Constructing reflection-symmetric flexible realisations of graphs* | 2024-08-13 | Paper earlier | Graph flex/edge-length-preserving motion and NAC/RS edge-colouring require separate proofs; symbolic mirror language is **not** equivalent. |

The two papers already appear in the owner's private alphaXiv **Pythagoras & Geometry** library folder. No duplicate save or submission is necessary.

## Publication and privacy gates

The private Drive NOVOexport is authority for raw conversation bytes. The private GitHub index is a derivative and its git commit is a later immutable version anchor. The public RLL repository contains **only derived dates, Git object hashes, literature citations, method and uncertainty**. Never transfer raw conversation text, private corpus paths with contents, credentials, PATs or personal data to Pages, public artifact uploads or publication drafts.

The existing `data/governance/rll_publication_boundary_v1.json` must remain effective. `PapersPub/README.md` demands a draft, manifest, references, reproducibility and claim gates before a paper changes maturity. This report **does not submit a paper** to arXiv/alphaXiv and does not modify any scientific result.

## Reproducibility and falsifiers

Run stdlib-only:
```sh
python3 tools/validate_geometry_prior_art_crosswalk.py
python3 -m unittest discover -s tests -p test_geometry_prior_art_crosswalk.py
```

Expected: chronology/claim-boundary gate passes only for the pinned record; reversed date ordering, unexpected schema, missing SHA or publication promotion fail closed. This check cannot authenticate private source bytes or establish mathematical novelty. A separate private-custody gate must read the raw shard by exact SHA, message id, role and timestamp, and separate independent mathematical review must compare theorems and algorithms.

## R3

- `F_ok`: two paper dates, role-scoped index observation, index commit and blob anchors, fail-closed policy.
- `F_gap`: raw shard integrity readback, full 000..050 search, quote-versus-original authorship, exact formal equivalence, third-party priority evidence.
- `F_next`: validate raw provenance in private custody, attach hash-only receipt, commission mathematical falsifier review; do not publish a novelty or priority claim.
