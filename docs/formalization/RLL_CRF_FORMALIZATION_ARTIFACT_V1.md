# RLL CRF Formalization Artifact V1

**Date:** 2026-09-24  
**State:** `FORMALIZATION_PIPELINE / STDLIB_ONLY_BUILDER / CLAIM_FAIL_CLOSED`  
**Artifact:** `rll-crf-formalization-v1`

## Purpose

Materialize the cross-repository formalization map as one deterministic CI artifact before building any web page.

The pipeline consumes an exact byte snapshot of one pinned registry from `rafaelmeloreisnovo/Matem-tica-` and emits a page-ready artifact without scraping Markdown or copying the underlying papers/code repositories. The source repository is private, so the RLL CI uses a source-locked local snapshot instead of a cross-repository secret.

```text
Matem-tica- CRF registry (pinned blob)
        |
        v
Python stdlib validator/builder
        |
        +--> FORMALIZATION_REGISTRY.json
        +--> FORMALIZATION_INDEX.md
        +--> SUMMARY.json
        +--> PAGE_DATA.json
        +--> MANIFEST.json
        +--> CHECKSUMS.sha256
        |
        v
GitHub Actions artifact
        |
        v
future page (artifact consumer only)
```

## Dependency policy

The builder uses only the Python standard library.

The CI intentionally avoids:

- `actions/checkout`;
- `actions/setup-python`;
- pip;
- npm;
- jq;
- yq;
- project-specific Python packages;
- cross-repository authentication secrets;
- runtime network access for the CRF source.

Repository checkout uses the runner's `git`. The only external GitHub Action is the official, commit-pinned `actions/upload-artifact`, because GitHub Actions artifacts require a publication mechanism.

## Source lock

The input is pinned by origin repository, commit, path and Git blob SHA-1. The registry bytes are vendored as a small snapshot inside RLL; the builder recomputes the Git blob SHA-1 and fails closed if the snapshot differs from the private origin.

This prevents a moving `main` branch from silently changing the generated artifact.

## Artifact contract

`PAGE_DATA.json` is the future page boundary.

The page must not independently:

- crawl the four source repositories;
- infer theorem status from Markdown;
- turn `TOKEN_VAZIO` into zero;
- promote novelty or physical claims.

It renders the artifact.

## Gates

The builder requires:

1. source schema match;
2. `claim_allowed=false`;
3. exactly 34 items;
4. contiguous IDs `CRF-001..CRF-034`;
5. readiness counts `A=25, B=8, C=1`;
6. required fields per item;
7. deterministic second build with byte-for-byte `diff`;
8. exact output file set;
9. SHA-256 checksums.

A PASS means the **formalization routing artifact** is reproducible. It does not mean all CRF items are proved or novel.

## Future page

The page should consume only:

```text
PAGE_DATA.json
```

Recommended views:

- all 34 CRF items;
- A / formalize-now;
- B / one-gate;
- C / research-program;
- per-item formula, source, code, test, evidence, prior-art and gaps.

No UI implementation is part of V1. First close the artifact gate.

## R3

**F_ok:** contract, stdlib builder, deterministic artifact format and CI upload route defined.

**F_gap:** remote CI execution/artifact ID must be observed after push; individual CRF mathematical proofs remain item-specific.

**F_next:** after artifact PASS, use downloaded `PAGE_DATA.json` as the sole page data source.
