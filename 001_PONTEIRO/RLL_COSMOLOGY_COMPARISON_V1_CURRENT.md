# 001_PONTEIRO - RLL cosmology comparator
START docs/research/RLL_COSMOLOGY_MODEL_COMPARATOR_AUDIT_20261108.md
AUDIT tools/ci/rll_comparator_evidence_matrix_v1.py
TESTS tests/test_rll_comparator_evidence_matrix_v1.py
PROVIDER_CI_ARTIFACT artifacts/python-tests/rll_comparator_evidence_matrix_v1.json
SOURCE results/audit/rll_model_evidence_scan.json and results/structure_d/joint_real_likelihood.csv, DESI13, other64, legacy45, growth16, G4 G5 G6, perturbation state.
P0 Same N does not mean same likelihood. Do not promote claim_allowed. No fit, no physical model validation.
