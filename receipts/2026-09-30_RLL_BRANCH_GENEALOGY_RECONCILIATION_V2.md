# Receipt — RLL Branch Genealogy Reconciliation V2

**Date:** 2026-09-30  
**State:** `B0_RECONCILIATION_CANDIDATE`  
**claim_allowed:** `false`

## Authority event

PR #1021 was merged directly into `main` at:

`f142206269cd9d86027d3cd7d6379f98c02b1dcf`

That event is preserved. This receipt does not retroactively relabel the merge as a canonical promotion-chain PASS.

## Frozen refs

```text
main            3a34d6f3841857d2a1802a2902cbb9176f026122
rll/lab         90ca23949df579d99018814dd1c6856f2b38214b
rll/integration 2f30179ebebf91e7514ffdffb61609a3cf12ef0b
rll/release     2cb3e3e88677ea9ac1f263377114b539db7bc47f
```

All recursive-tree responses used for this audit were `truncated=false`.

## Exact path topology

Using merge-base tree → branch-tip blob comparisons:

```text
main vs rll/lab:
  main-only/changed path set = 533
  lab-only/changed path set  = 300
  overlap                     = 168

rll/lab vs rll/integration:
  lab changed paths          = 84
  integration changed paths  = 0

rll/integration vs rll/release:
  integration changed paths  = 949
  release changed paths      = 0

rll/release vs main:
  release changed paths      = 0
  main changed paths         = 1251
```

The August observation of zero main/lab path intersection is historical only. The current September snapshot has 168 overlapping changed paths.

## Convergence blob identity

The work→lab candidate carries the four exact blobs already merged into main:

```text
658432d8694b35a1a9ddb072838c82062e317386  data/governance/PAPERS_RLL_CONVERGENCE_V1.json
847e1ff7bacb3948118ea512f367c03fc1bd977d  docs/governance/PAPERS_RLL_CONVERGENCE_V1.md
25651491c8c6c99228d4a29b59735a7f074e8d2e  tests/test_papers_rll_convergence_v1.py
5d070cdf652598ac7f0b849d4faa3e124af7998f  tools/validate_papers_rll_convergence_v1.py
```

## Route decision

```text
WORK -> rll/lab                    = canonical candidate
WORK -> rll/integration            = BLOCKED
WORK -> rll/release                = BLOCKED
bulk rll/lab -> rll/integration    = FORBIDDEN pending batch review
bulk rll/integration -> rll/release= FORBIDDEN pending batch review
bulk rll/release -> main           = FORBIDDEN pending batch review
```

No branch-maturity rule is weakened.

## Negative results preserved

- WS01 preregistered distance-tolerance failure;
- documentation-inventory drift;
- G6 MCMC-convergence blocker;
- G7/G9/G10/G11 open executor/replication/claim-router gaps.

## R3

`F_ok` = current genealogy frozen; exact recursive path deltas measured; convergence blobs byte-identical; work→lab route accepted structurally.  
`F_gap` = 168 main/lab overlap paths require dependency partition; selective promotion route beyond lab remains TOKEN_VAZIO.  
`F_next` = complete #1023 checks; then build B0/B1 dependency batches instead of merging divergent branch histories.
