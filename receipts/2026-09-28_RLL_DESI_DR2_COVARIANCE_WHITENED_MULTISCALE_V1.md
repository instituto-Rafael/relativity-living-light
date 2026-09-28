# Receipt — RLL DESI DR2 Covariance-Whitened Multiscale V1

**Date:** 2026-09-28  
**PR:** #1006  
**Branch:** \`work/desi-dr2-covariance-whitened-multiscale-v1-20260928\`  
**Base:** \`313b1f1efb332dee1e981caeccadc7b63bd77160\`  
**Tested source head:** \`adc67d49bd33e5e5ec5eb49b4a4860e654952f2a\`  
**claim_allowed:** \`false\`

## Materialized

- \`scripts/rll_desi_dr2_covariance_multiscale.py\`
- \`data/contracts/rll_desi_dr2_covariance_multiscale.v1.json\`
- \`tests/test_rll_desi_dr2_covariance_multiscale.py\`
- \`docs/science/RLL_DESI_DR2_COVARIANCE_WHITENED_MULTISCALE_V1.md\`
- \`.github/workflows/desi-dr2-covariance-multiscale-gate.yml\`

## Provider evidence

Workflow: \`DESI DR2 Covariance Whitened Multiscale Gate\`  
Run: \`36491451759\`  
Job: \`109160771657\`  
Conclusion: \`success\`

Observed provider log:

\`\`\`text
PASS_CONTRACT rll.desi_dr2.covariance_whitened_multiscale.contract.v1
PASS_REFERENCE 11.770259055546353
...... [100%]
6 passed in 0.05s
\`\`\`

The executor consumed the committed 13-vector, the committed 13×13 DESI DR2
covariance and the committed G4 reproduction. Cholesky whitening reproduced
the frozen RLL G4 DESI chi-square.

## What this PASS establishes

- observation/prediction ordering is accepted by the executor;
- the committed covariance is symmetric and positive definite under Cholesky;
- \`chi2 = r^T C^-1 r = sum(z_i^2)\` reproduces the frozen G4 RLL value;
- covariance-block chi-square closure passes for the committed block-diagonal matrix;
- Fibonacci windows are \`[2,3,5,8,13]\` and remain diagnostic only;
- \`sqrt(3)/2\`, Poincaré, Venturi and calendar namespaces do not modify the likelihood;
- \`claim_allowed=false\`.

## What this PASS does not establish

- RLL superiority;
- a new probability distribution;
- optimality of Fibonacci windows;
- a physical Poincaré mechanism;
- a Venturi-cosmology equivalence;
- Maya-calendar causality;
- independent reproduction.

The frozen G4 RLL point has \`Omega_s0=0\`, so this execution is on the LCDM
null submanifold for the background comparison. This is a covariance/residual
reproduction gate, not model discrimination.

## R3

\`\`\`text
F_ok =
full covariance consumed
+ Cholesky whitening PASS
+ RLL G4 chi2 = 11.770259055546353 reproduced
+ block closure PASS
+ Fibonacci diagnostic boundary PASS
+ 6 focused tests PASS

F_gap =
independent reproduction
+ preregistered non-null/held-out RLL profile
+ any physical Poincare/Venturi/calendar binding

F_next =
freeze one non-null or held-out RLL profile
-> apply identical ordering/covariance/Fibonacci scales
-> compare diagnostic structure without retuning
-> keep scientific claim gate separate
\`\`\`
