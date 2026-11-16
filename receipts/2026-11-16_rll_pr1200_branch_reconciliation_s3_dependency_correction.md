# RLL PR #1200 — Correção sucessora S3: dependências das três vias

- mu_id: MU-RLL-PR1200-S3-DEPENDENCY-GUARD-20261116
- parent_commit: d8b0fec26222e87882e28103550d6ae2cbf87301
- previous_receipt: receipts/2026-11-16_rll_pr1200_branch_reconciliation_s2.md
- target: work/rll-pr1200-reconcile-stdlib-gates-20261116 (isolada, sem alterar main/lab/integration/release)
- source: https://github.com/instituto-Rafael/relativity-living-light/pull/1200
- status: CORRECTIVE_SUCCESSOR / IMPLEMENTED_UNTESTED / CLAIM_ALLOWED_FALSE
- finding: O merge de linha da etapa S2 preservava hunk syntax mas não garantia closure de dependências do workflow.
- gaps N0 confirmados em rll/lab: tests/test_ci_scientific_skills.py ainda usa NumPy/Pandas, tools/ci_scientific_skills.py não é a versão stdlib; tools/validate_rll_section_retrofeedback.py, tests/test_rll_section_retrofeedback.py, data/contracts/rll_section_retrofeedback_operator.v1.json e tools/rll_ws01_background_decision_evidence.py ausentes. Os comandos extras em python-tests referenciavam tools/ci/rll_federated_pr_assurance_v1.py e tools/rll_lcm_graph_benchmark_v1.py, ausentes de lab.
- correction: restaurar os blobs originais de rll/lab para ci-scientific-skills.yml, python-tests.yml e rll-governance-quality-gate.yml. Nenhum desses workflows permanecerá forward-ported sem dependências completas.
- original_blob_restored:
  - .github/workflows/ci-scientific-skills.yml: 05d653d876051231e2c5da9c7702872f509adfde
  - .github/workflows/python-tests.yml: 341254368fee4dbf066a9504217d0e409d93e840
  - .github/workflows/rll-governance-quality-gate.yml: 90b0c63d9bff54e60b2df66a8200e083ee544fe3
- retained_delta: somente os dois workflows de auditoria de dados da etapa S1, cujos validadores/arquivos fonte existem em main e lab com SHA idêntico.
- control: lineage append-only S2 preservada como tentativa invalidada em escopo; readback exigido; testes exact-head e runtimes NOT_RUN. claim_allowed=false.
- next: adicionar dependency-closure preflight + testes antes de promover novos hunks de main; não executar merge global.
