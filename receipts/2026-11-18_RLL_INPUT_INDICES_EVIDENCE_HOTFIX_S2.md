# RLL bounded hypothesis diagnostic — successor receipt

μID: MU-RLL-INPUT-INDICES-EVIDENCE-20261118-S2
Parent: MU-RLL-INPUT-INDICES-EVIDENCE-20261118-S1 (producer receipt in this directory).
Source/executed code: instituto-Rafael/relativity-living-light@cef32f840aee1be7984fe202d48c1297ac39ab05.
Kind: EXECUTED_LOCAL_DIAGNOSTIC / NOT_SCIENTIFIC_VALIDATION; claim_allowed=false.
No code change in this successor; generated artifact and observation receipt only.

## Readback / software gate

All six files in source commit were fetched through Git and compared byte for byte against locally tested files; equality confirmed. Focused local suite 67 passed, seven subtests, one environment deprecation warning.

## Hypothesis diagnostic

Command: `python scripts/rll_desi_adversarial.py --root . --output-dir /tmp/rll-hotfix-profile --seed 1748365262 --starts 5 --bootstrap 8 --leave-tracer-out`.
Exit 0. Three models, 13 BAO observations, pinned 13x13 covariance; rd=147.09 Mpc and Omega_r=9.2e-5 fixed. Seven tracer-block holdouts, refit without the held-out observations. Optimizer bounds and seed are recorded in executable source/artifact; five starts do not prove global optimality.

| Model | fitted k | chi2 | AICc diagnostic | boundary parameters |
|---|---|---|---|---|
| CPL | 4 | 5.699271710 | 18.699271710 | w0 |
| LCDM | 2 | 10.284009527 | 15.484009527 |  |
| RLL | 5 | 7.813068490 | 26.384497061 | wt |

CPL has lowest raw chi2 in this run; LCDM lowest AICc. No preordained winner. CPL w0 and RLL wt hit a boundary, so constrained exploration and parameter identifiability remain relevant limitations.
Bootstrap: eight synthetic replicates under fitted LCDM; three as/extremer improvements; exploratory plus-one p=4/9 with resolution=1/9. reliable_tail_inference=false, critical_values_calibrated=false. This tiny B cannot establish scientific significance or rejection. Fits on public observations != independent physical experiment. No SN/CMB/RSD joint fit, posterior, perturbation solver or independent replication performed.

Artifact: `results/audit/rll_input_indices_evidence_hotfix_20261118/adversarial_s1748365262_n5_b8_h1_ed83affed174.json`.
SHA-256: `6dd3dffdf11e3322408e9d3d94f17f2a600255ec4e9db8a3e2be8f0e46c95129`.
Artifact and companion checksum copied byte-for-byte from generated output, not edited by hand.

## Observed GitHub CI on code commit cef32f8

| Run | Workflow | Observed result |
|---|---|---|
| 44214396640 | concept-knowledge-matrix | success |
| 44214396274 | formulas-artifacts | success |
| 44214393852 | dashboard-ux-compilation | failure, zero jobs returned; root cause TOKEN_VAZIO |
| 44214392158 | android-build | failure, zero jobs returned; root cause TOKEN_VAZIO |
| 44214391467 | automatic Gradle dependency submission | failure at validate-project |

Gradle job 134500453771 log reports missing gradle/wrapper/gradle-wrapper.jar. That path was already absent in the parent tree. Android/dashboard workflow bytes and gradle/wrapper paths have no diff from parent ac833cb; unchanged source is not complete proof of runtime causality. No failed check suppressed or marked successful. Existing workflows triggered on branch push; no manual dispatch was issued. This CI does not execute the focused hypothesis/input suite; that suite remains LOCAL_ONLY. Successors containing receipts have their own CI state, which must not inherit the source commit's check status.

## Boundaries / rollback / R3

GITPAT actual binding/authentication remains NOT_EXECUTED; authorized GitHub connector handled repository writes. No credential value read/copied/hashed, settings modified, new workflow, PR, merge, release or global pointer advance.
Provider promotion gate remains blocked as described in S1. Rollback: leave this branch unmerged or a reviewed successor revert; original receipts retained.
F_ok: bounded real-data numerical diagnostic, synthetic bootstrap and holdout executed; generated results preserved with checksum.
F_gap: full/focused exact-head CI, three observed CI failures, boundary identification, adequate bootstrap calibration, independent review/replication, PAT runtime, enforceable promotion controls.
F_next: diagnose zero-job workflow failures, repair Gradle wrapper setup on its owning CI route, then run the focused suite under authorized exact-code CI before promotion.
