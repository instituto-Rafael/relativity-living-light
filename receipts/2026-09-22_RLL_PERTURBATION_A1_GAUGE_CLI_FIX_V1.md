# μWRITE — A1.2 Direct-CLI Import Failure/Repair — 2026-09-22

State: IMPLEMENTATION_FAIL_OBSERVED -> NARROW_FIX_APPLIED -> CI_PENDING

μID=RLL-PERTURB-A1-GAUGE-CLI-20260922-V1

first_failed_run:
- workflow: CLASS CAMB Baseline Crosscheck
- run_id: 35721565467
- job_id: 106725423103
- head_sha: 5e9cd27b08c4377a4d34d9ecf2ababa643572470
- focused_tests: 15/15 PASS before direct CLI step
- A1.1: 9/9 PASS
- failing_step: Execute A1.2 gauge-variable regularity diagnostic
- observed_error: ModuleNotFoundError: No module named 'tools'

classification:
- type: EXECUTION_PATH_IMPORT_ERROR
- scientific_equations_falsified: false
- A1.2_gate_executed: false
- claim_allowed: false

repair:
- add repository root to sys.path only when __package__ is empty/direct-script mode
- preserve canonical tools.* import
- add regression reproducing exact direct CLI invocation from repository root
- no equation, threshold, sweep, or scientific state changed

rollback:
- revert the two direct-CLI commits only if a superior packaging/import route replaces them
- preserve this failure receipt

F_next:
- consume rerun on repaired head
- if A1.2 executes, judge it on mathematical/regularity output rather than import plumbing
