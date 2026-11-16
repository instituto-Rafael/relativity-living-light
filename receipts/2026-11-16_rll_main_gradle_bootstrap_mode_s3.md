# RLL Gradle Wrapper chmod successor S3 (2026-11-16)
- mu_id: MU-RLL-MAIN-WRAPPER-MODE-S3-20261116
- parent: 476394cb5763ba064b83a159b8ee413b169f44e8
- source: `main@ac833cb1278ffde951e602dd70df4c11bcda6ac0` `scripts/bootstrap-gradle-wrapper.sh` was `100755`.
- issue: PR #1217 S1 tree mistakenly staged bootstrap script as `100644`, changing executable permission without need.
- fix: restore mode 100755 with exact same blob `7d56c35ebd76b75c1e72dc827345ccd71722bde8`; append-only correction, no content mutation.
- evidence: Git tree mode comparison, exact readback required; claim_allowed=false.
- future: ensure correct modes when copying into Dependabot hotfix branch #1213.
