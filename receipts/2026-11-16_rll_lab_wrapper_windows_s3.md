# RLL lab: Windows Gradle Wrapper alignment — S3 (2026-11-16)

- mu_id: MU-RLL-LAB-WRAPPER-WINDOWS-20261116-S3
- base: rll/lab@b3f549f9d75d912f411f80d0e8d5753c946faebd
- source: 476394cb5763ba064b83a159b8ee413b169f44e8 (scoped Gradle wrapper PR #1217)
- context: main source Gradle auto-submission run 43821138399 confirmed SUCCESS after Unix classpath fix; independent maturity gates block work→main by design.
- Git tree comparison: existing gradle-wrapper.jar, gradle-wrapper.properties and Unix gradlew blobs are identical between source and lab; do not duplicate or overwrite.
- delta: import Windows launcher fix from source blob and add regression covering Windows & Unix invocation, correct Gradle 8.10.2 SHA pin & ZIP/class.
- source_exact_blobs:
  - gradlew.bat: 9b42019c7915b971238526075306ffba3b666dd5
  - tests/test_gradle_wrapper_presence_v1.py: 79112338428b07ba76988af2f974352c5ec52d1a
- no branch history overwrite; no main edits; only work→lab route.
- test state at source: Unix Gradle auto submission PASS_SCOPED, Windows runner NOT_RUN; exact PR branch test NOT_RUN until CI.
- claim_allowed: false
- rollback: reviewed successor/revert commit, preserve original lab parent.
