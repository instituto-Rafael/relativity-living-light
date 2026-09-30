# Correction Receipt — RMRCTI approximately 0.70 stability-related observation

**Date:** 2026-09-22  
**Author:** RAFAEL MELO REIS  
**Mode:** \`SOURCE_FIRST / APPEND_ONLY / SEMANTIC_SEPARATION\`

## User correction

The spoken reference was not an integer/index around 70. It was an approximate decimal value around **0.70**, associated with the RMRCTI stability context.

## Source finding

Repository:

\`rafaelmeloreisnovo/llamaRafaelia\`

Artifact:

\`rmrCti/zone_stats.txt\`

Blob SHA:

\`230a578abaa4675f48f967f9af414a23ef1a8ef4\`

Exact row:

\`\`\`text
28    95    0.147400    0.136800    0.700000
\`\`\`

Header:

\`\`\`text
zone  refs  IC_mean  PP_mean  CV_mean
\`\`\`

Thus:

\[
\boxed{CV_{mean}(\mathrm{zone}\ 28)=0.700000}.
\]

## Upstream definition

Source:

\`rmrCti/omega_metrics_v2.c\`

Blob SHA:

\`17cb0e5722ec180091c636ed5e1df3ba2dc68864\`

The implementation states:

\`\`\`text
CV = top10% value share using buckets
\`\`\`

and computes

\`\`\`text
CV = top_val / total_val
\`\`\`

when \`total_val>0\`.

Therefore this is a real committed RMRCTI number, but its exact implemented identity is \`CV_mean\`, not \`stable_any_rate\`.

## Semantic correction

Previous RLL interpretation:

\`TOKEN_VAZIO_INDEX_AROUND_70\`

is superseded for this recollection by:

\`SOURCE_OBSERVED_CV_MEAN_0_700000 / STABILITY_PROXY_CANDIDATE\`.

Do not merge numerically equal but distinct fields:

\[
CV_{mean}=0.7
\neq
r=0.7.
\]

Also:

\[
CV_{mean}=0.7
\neq
\Delta P\approx0.18.
\]

## Next falsifiable test

Treat \(\approx0.70\) as a candidate stability/concentration level only through the \`CV\` lineage.

Test whether \`CV_mean\` remains near 0.70 under:

- regenerated zone assignments;
- corpus/chunk perturbation;
- seed/parameter changes;
- held-out data;
- alternate implementation.

If it does not persist, retain it as a zone-specific observed statistic rather than an invariant.

## R3

**F_ok:** the approximate 0.70 recollection is now grounded in a committed RMRCTI artifact as \`zone 28 CV_mean=0.700000\`.

**F_gap:** persistence of this value under independent perturbations has not yet been demonstrated, and its exact relation to dynamical \`stable_any\` remains unproven.

**F_next:** run a dedicated CV≈0.70 replication/falsification sweep without conflating it with \(r=0.7\) or \(\Delta P\approx0.18\).
