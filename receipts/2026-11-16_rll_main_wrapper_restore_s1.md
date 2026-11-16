# RLL Ω — Gradle wrapper restored to main review candidate (2026-11-16)

- mu_id: MU-RLL-GRADLE-WRAPPER-MAIN-20261116-S1
- source_repository: instituto-Rafael/relativity-living-light
- source_branch: rll/lab@b3f549f9d75d912f411f80d0e8d5753c946faebd
- binary_source: gradle/wrapper/gradle-wrapper.jar | Git SHA-1 blob a4b76b9530d66f5e68d973ea569d8e19de379189 | size 43583 bytes
- target: work/rll-main-gradle-wrapper-binary-hotfix-20261116-v1 based on main@ac833cb1278ffde951e602dd70df4c11bcda6ac0
- issue: GitHub automatic Gradle dependency submission fails with 'Unable to access jarfile gradle/wrapper/gradle-wrapper.jar' in PRs #1212 #1213 #1214 #1215 #1204
- change: identical existing lab blob (no rebuild); add SHA-256 distribution checksum already present in lab; correct outdated bootstrap fallback message; static zip test.
- authority: scope only main review branch, no writes to protected main, no force-push, no rule bypass.
- evidence: source Git tree consulted untruncated, exact blob SHA/size compared; target blob/tree must be verified by readback.
- execution: IMPLEMENTED_UNTESTED; exact-head tests NOT_RUN and Gradle submission NOT_RUN at receipt creation.
- uncertainty: jar byte provenance beyond Git object/source lab requires exact-run execution check, not inferred from blob identity alone.
- claim_allowed: false
- rollback: create reviewed revert of this PR; no branch history rewrite.
