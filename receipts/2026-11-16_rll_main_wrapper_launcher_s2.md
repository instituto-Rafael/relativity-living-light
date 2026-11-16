# RLL — S2 Gradle Wrapper launchers (2026-11-16)

- mu_id: MU-RLL-WRAPPER-LAUNCHER-S2-20261116
- parent_commit: 862105ddc56e6b98fb8cd79ee29d9439b1b76cda
- previous receipt: receipts/2026-11-16_rll_main_wrapper_restore_s1.md
- evidence: GitHub Gradle submission run 43820849863 on S1 fails with "no main manifest attribute" in gradle/wrapper/gradle-wrapper.jar.
- root cause: main gradlew and gradlew.bat ran `java -jar gradle-wrapper.jar`; Gradle Wrapper JAR is executable by `java -classpath jar org.gradle.wrapper.GradleWrapperMain`, not by -jar.
- Unix fix: exact lab Git blob faf93008b77e7b52e18c44e4eef257fc2f8fd76d, confirmed equal to main with only classpath/entrypoint corrections; executable mode 100755 preserved.
- Windows fix: set classpath to local Gradle Wrapper JAR and run GradleWrapperMain; preserve CRLF and previous command args.
- regression: tests/test_gradle_wrapper_presence_v1.py checks class presence, SHA pin, Unix and Windows launch patterns, no -jar.
- scope: review branch work/rll-main-gradle-wrapper-binary-hotfix-20261116-v1, not protected main.
- claim_allowed=false; status=IMPLEMENTED_UNTESTED; only exact CI on new HEAD can resolve Gradle outcome.
- rollback: restore previous blob from parent as corrective successor, no force.
