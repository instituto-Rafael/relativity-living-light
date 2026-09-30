# RLL Geometric Weave Invariants — Execution Receipt V1

**Date:** 2026-09-21  
**Author:** RAFAEL MELO REIS  
**Execution state:** \`LOCAL_ISOLATED_EXECUTION_PASS\`  
**CI state:** \`NOT_RUN\`  
**Physical claim:** \`BLOCKED\`

## Executed verifier

\`tools/verify_geometric_weave_invariants.py\`

Source SHA-256 used in the isolated run:

\`f72185d974b81d21d9b3372e521d4c6e05a1b21822dbd4b9dfe6f4f8da371ceb\`

Runtime:

\`\`\`text
Python 3.13.5
Linux-6.18.44-x86_64-with-glibc2.41
tolerance = 1e-12
\`\`\`

## Result

\`\`\`text
RLL-GWI-001 PASS
RLL-GWI-002 PASS
RLL-GWI-003 PASS
RLL-GWI-004 PASS
RLL-GWI-005 PASS
RLL-GWI-006 PASS
RLL-GWI-007 PASS
RLL-GWI-008 PASS
RLL-GWI-009 PASS
RLL-GWI-010 PASS

TOTAL = 10 PASS / 0 FAIL
\`\`\`

## Negative controls executed

The verifier also tests declared failure boundaries instead of only positive identities.

### Affine angle boundary

An invertible affine map produced:

\[
\cos(\theta')=0.43145549730400484
\]

from an originally orthogonal axis pair, confirming that Euclidean angle is not generally affine-invariant.

State: \`EXPECTED_NON_INVARIANCE_PASS\`.

### Affine length-ratio boundary

The same affine map produced transformed unit-axis length ratio

\[
1.2747548783981961\neq1.
\]

State: \`EXPECTED_NON_INVARIANCE_PASS\`.

### Two-octagon anisotropic boundary

For the equality

\[
R_{\cap}=s_{\mathrm{hull}},
\]

a selected anisotropic scaling produced transformed length ratio

\[
1.5728365464142842\neq1.
\]

Thus the equality survived the tested rotation/uniform-scale similarity route but correctly failed the anisotropic negative control.

State: \`EXPECTED_NON_INVARIANCE_PASS\`.

## Maximum numerical residuals

- GWI-001: \(1.7763568394002505\times10^{-15}\)
- GWI-002: \(1.1102230246251565\times10^{-16}\)
- GWI-003: \(8.881784197001252\times10^{-16}\) rad
- GWI-004: \(5.551115123125783\times10^{-17}\)
- GWI-005: \(2.0816681711721685\times10^{-17}\)
- GWI-007: \(0\)
- GWI-008: \(0\)
- GWI-009 similarity residual: \(1.7763568394002505\times10^{-15}\)
- GWI-010: \(2.220446049250313\times10^{-16}\)

All are below the declared tolerance \(10^{-12}\).

## Materialized code/result commits

- verifier: \`f44f4332c255471cebccead0b5a9181b537b1d1c\`
- pytest gate: \`e6a37467334b4fb26848a8cf4f86216c870fdcb2\`
- execution result JSON: \`6c28322aae063e2cca192af2410324fa809de52f\`

## Epistemic boundary

This execution establishes:

\[
\text{implemented mathematical checks}
\to
\text{local numerical PASS}.
\]

It does **not** establish:

\[
\text{local numerical PASS}
\Rightarrow
\text{global mathematical novelty}
\]

or

\[
\text{local numerical PASS}
\Rightarrow
\text{physical/cosmological mechanism}.
\]

Remaining gates:

- prior art: \`TOKEN_VAZIO\`
- image calibration: \`TOKEN_VAZIO\`
- independent reproduction: \`NOT_RUN\`
- GitHub CI execution: \`NOT_RUN\`
- physical binding: \`TOKEN_VAZIO_BLOCKED\`

## μWRITE

\`\`\`text
μID=RLL-GWI-EXEC-20260921-V1
source/ref=docs/invariants/geometric_weave_invariants_v1.md + tools/verify_geometric_weave_invariants.py
parent=RLL-GEOMETRIC-WEAVE-INVARIANTS-20260921-V1
kind=deterministic-mathematical-verification
Δsummary=execute 10 typed invariant families plus negative controls; 10 PASS / 0 FAIL at tolerance 1e-12
evidence=LOCAL_ISOLATED_EXECUTION_PASS
gap=CI + independent reproduction + prior art + image calibration + physical binding
next=run repository CI and independent reproduction; bind no physical claim before external gates
rollback=revert this receipt/result/test/verifier commits only; preserve formal atlas and upstream MF ledger
\`\`\`

## R3

**F_ok:** executable verification now exists and all ten scoped invariant families passed the isolated deterministic run, including counterexamples for non-invariant claims.

**F_gap:** repository CI, independent reproduction, prior-art closure, image calibration and physical binding remain unresolved.

**F_next:** obtain an independent execution receipt and CI result, then classify each RLL-GWI family as classical/derived/project-composition against prior art.
