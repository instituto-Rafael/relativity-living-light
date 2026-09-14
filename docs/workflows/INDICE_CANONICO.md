# Índice Canônico de Workflows — RLL

> **Gerado**: 2026-07-20 | **Workflows totais**: 44 | **Branch**: `claude/rll-cronologia-auditoria-qyvn83`
>
> Este índice substitui `docs/YML_WORKFLOWS_INDEX.md` como referência humana primária.
> A tabela de SHA256 bruta é mantida em `YML_WORKFLOWS_INDEX.md` (auto-gerada por `tools/docs_inventory.py`).

---

## Visão Estrutural

```
CAMADA 0 · Pipeline Canônico (gate determinístico único)
    └── rll-pipeline-linear-completo.yml  [44 steps, 7 fases]

CAMADA 1 · Core CI Automático (push / pull_request — checks obrigatórios)
    ├── python-tests.yml            [push → check: test]
    ├── convention-check.yml        [PR   → check: check-conventions]
    ├── formulas-artifacts.yml      [push → check: build-formulas-artifacts]
    ├── formulas-artifacts-validation.yml [push/dispatch → check: formulas-manifest]
    └── yml-syntax-validation.yml   [PR   → check: validate-yaml]

CAMADA 2 · Entradas Manuais Canônicas (delegam ao Pipeline Canônico)
    ├── RLL-CI.yml                  [dispatch → rll-pipeline modo=apenas_ciencia]
    └── RLL_SCIENTIFIC.yml          [dispatch → rll-pipeline modo=apenas_ciencia]

CAMADA 3 · Validação Científica em PR (checks de qualidade)
    ├── dha-fisher-ci.yml
    ├── real-data-contract-ci.yml
    ├── rll-structural-integration.yml
    ├── six-sigma-real-data-controls.yml
    ├── validate-academic-correlation-package.yml
    ├── validate-cross-repo-relationship-registry.yml
    ├── validate-real-dataset-variance-registry.yml
    ├── validate-schema-contracts.yml
    └── validate-sequence-metrics.yml

CAMADA 4 · Orquestradores Manuais
    ├── rll-validacao-cientifica-completa.yml  [P0/P1 desbloqueadores PODE]
    ├── real-data-complete-execution.yml       [CANÔNICO para dados reais]
    ├── rll-real-data-orchestrator.yml         [orquestrador multi-domínio]
    └── unified-workflow-session-orchestrator.yml

CAMADA 5 · Pipelines Computacionais
    ├── bayes_analysis.yml
    ├── calc-data.yml
    ├── canonical-route-artifacts.yml
    ├── import-data.yml
    ├── rll-book-data-pipeline.yml
    └── rll-data-pipeline.yml

CAMADA 6 · Validações Científicas Específicas
    ├── academic-parameter-governance.yml  [push]
    ├── claim-boundary-quality-gates.yml
    ├── desi-dr2-bao-validation.yml
    ├── iml_artifact.yml
    ├── orbital-shape-angular-momentum-validation.yml
    ├── orbital-state-vector-v2.yml
    ├── rll-balance-report.yml
    └── unified-geometry.yml

CAMADA 7 · Dados, Sementes e Inventário
    ├── dense-feature-matrix.yml
    ├── raw-data-manifest-status.yml
    ├── real-data-bootstrap-validation.yml
    ├── real-seed-ingestion-plan.yml
    ├── real-seed-validation-v0.yml
    └── repo-real-inventory.yml

CAMADA 8 · Auxiliares / Específicos
    ├── android-build.yml            [build Android — trigger: app/]
    ├── START_MANUAL_HERE.yml        [AUXILIAR → use real-data-complete-execution.yml]
    └── validacao_real.yml           [AUXILIAR → use real-data-complete-execution.yml]
```

---

## CAMADA 0 — Pipeline Canônico

### `rll-pipeline-linear-completo.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | RLL FASE 24.1 — Gate Determinístico |
| **Trigger** | `workflow_dispatch` |
| **Job único** | `pipeline-linear` (44 steps sequenciais) |
| **Inputs** | `modo` (completo/apenas_ciencia/apenas_governanca/apenas_dados/dry_run); `commit_artefato` (bool) |
| **Artefato** | `pipeline-linear-artefato-{run_id}` com `PIPELINE_LINEAR_LOG.md` + `CHECKSUMS.sha256` |
| **Status** | ✅ CANÔNICO — gate único de execução completa |

**Fases internas**:

| FASE | Steps | Escopo |
|------|-------|--------|
| 0 | 01–06 | Infraestrutura, dependências, validação YAML, audit |
| 1 | 07–12 | Dados e contratos (inventário, ingestão, manifesto) |
| 2 | 13–18 | Validação científica core (Pantheon+, DESI BAO, w_eff, z_t) |
| 3 | 19–23 | MCMC + Bayes P0 (emcee, dynesty, structure_d) |
| 4 | 24–29 | Pipelines computacionais (IML, formulas, balanço, DHA) |
| 5 | 30–34 | Sementes e domínios (orbital, bootstrap, métricas) |
| 6 | 35–40 | Governança e contratos (academic gov, six sigma, variance, correlation) |
| 7 | 41–44 | Contrato final, relatório, log de referência, upload artefato |

**Log de referência**: Cada step registra `step → yml_origem → script → status` em `results/linear/step_status.tsv`. Step 43 agrega em `PIPELINE_LINEAR_LOG.md`.

---

## CAMADA 1 — Core CI Automático

### `python-tests.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Python tests |
| **Trigger** | `push` (branches: main, claude/\*) |
| **Check obrigatório** | `test` |
| **Script** | `pytest -q` |
| **Status** | ✅ OBRIGATÓRIO — não remover |

### `convention-check.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Convention Consistency Check |
| **Trigger** | `pull_request` |
| **Check obrigatório** | `check-conventions` |
| **Script** | `scripts/check_convention_conflicts.sh` |
| **Status** | ✅ OBRIGATÓRIO — não remover |

### `formulas-artifacts.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | formulas-artifacts |
| **Trigger** | `push` (paths: schemas/, tools/formula_artifact_builder.py, …) |
| **Check obrigatório** | `build-formulas-artifacts` |
| **Script** | `tools/formula_artifact_builder.py` |
| **Artefato** | `artifacts/formulas/` |
| **Status** | ✅ OBRIGATÓRIO — não remover |

### `formulas-artifacts-validation.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Formulas artifacts validation |
| **Trigger** | `push` + `workflow_dispatch` |
| **Check obrigatório** | `formulas-manifest` |
| **Script** | `scripts/validate_formulas_manifest.py` |
| **Status** | ✅ OBRIGATÓRIO — não remover |

### `yml-syntax-validation.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | YAML Syntax Validation Gate |
| **Trigger** | `pull_request` |
| **Check obrigatório** | `validate-yaml` |
| **Scripts** | `tools/audit_github_workflows.py --strict`; `python -c "import yaml; yaml.safe_load(...)` |
| **Status** | ✅ OBRIGATÓRIO — não remover |

---

## CAMADA 2 — Entradas Manuais Canônicas

### `RLL-CI.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | RLL Scientific CI — entrada manual canônica |
| **Trigger** | `workflow_dispatch` |
| **Delegação** | `uses: rll-pipeline-linear-completo.yml` com `modo=apenas_ciencia` |
| **Check obrigatório** | `rll` (herdado do pipeline) |
| **Status** | ✅ CANÔNICO — entrada manual para CI científico |

### `RLL_SCIENTIFIC.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | RLL Scientific Validation — entrada manual canônica |
| **Trigger** | `workflow_dispatch` |
| **Delegação** | `uses: rll-pipeline-linear-completo.yml` com `modo=apenas_ciencia` |
| **Status** | ✅ CANÔNICO — alias de RLL-CI.yml (mantido por compatibilidade) |

---

## CAMADA 3 — Validação Científica em PR

### `dha-fisher-ci.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | DHA Fisher Validation |
| **Trigger** | `pull_request` (paths: scripts/run_desi_dha_pipeline.py, scripts/export_dha_forecast.py, …) |
| **Scripts** | `scripts/run_desi_dha_pipeline.py`; `scripts/export_dha_forecast.py` |
| **Artefato** | `dha-fisher-ci-artefatos/` |
| **Status** | ✅ ativo |

### `real-data-contract-ci.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Real Data Contract CI |
| **Trigger** | `pull_request` (paths: data/contracts/, schemas/) |
| **Job** | `real-data-contract` |
| **Script** | `scripts/validate_real_data_contract.py` |
| **Status** | ✅ ativo |

### `rll-structural-integration.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | RLL Structural Integration |
| **Trigger** | `pull_request` + `workflow_dispatch` |
| **Scripts** | `scripts/run_strong_gravity_calibration.py`; `python -m pytest tests/test_structural_integration.py` |
| **Status** | ✅ ativo |

### `six-sigma-real-data-controls.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Six Sigma Real Data Controls |
| **Trigger** | `pull_request` (paths: tools/validate_six_sigma_real_data_controls.py, …) |
| **Script** | `tools/validate_six_sigma_real_data_controls.py` |
| **Status** | ✅ ativo |

### `validate-academic-correlation-package.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Validate Academic Correlation Package |
| **Trigger** | `pull_request` |
| **Script** | `tools/validate_academic_correlation_package.py` |
| **Status** | ✅ ativo |

### `validate-cross-repo-relationship-registry.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Validate Cross-Repo Relationship Registry |
| **Trigger** | `pull_request` |
| **Scripts** | `tools/validate_cross_repo_relationship_registry.py`; `tools/validate_session_operating_system.py`; `tools/validate_session_reality_science_claims.py` |
| **Status** | ✅ ativo |

### `validate-real-dataset-variance-registry.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Validate Real Dataset Variance Registry |
| **Trigger** | `pull_request` |
| **Script** | `tools/validate_real_dataset_variance_registry.py` |
| **Status** | ✅ ativo |

### `validate-schema-contracts.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Validate Schema Contracts |
| **Trigger** | `pull_request` (paths: schemas/, fixtures/, src/rll/scientific_infinity.py, …) + `push` main |
| **Scripts** | `scripts/validate_omega_schemas.py`; `scripts/validate_information_evolution_trace.py`; múltiplos validadores de schema |
| **Status** | ✅ ativo — crítico para integridade de schemas |

### `validate-sequence-metrics.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Validate sequence metrics calculator |
| **Trigger** | `pull_request` |
| **Script** | `pytest -q tests/test_calculate_sequence_metrics.py` |
| **Status** | ✅ ativo |

---

## CAMADA 4 — Orquestradores Manuais

### `rll-validacao-cientifica-completa.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | RLL Validação Científica Completa — P0/P1 Desbloqueadores PODE |
| **Trigger** | `workflow_dispatch` |
| **Inputs** | `modo` (completo/apenas_fit/apenas_bayes/apenas_falsificadores/dry_run); `commit_resultados` (bool) |
| **Jobs** | 11 jobs: setup → fit_pantheon_rll → fit_desi_bao → weff_cpl_mapping → zt_falsification → joint_mcmc_p0 → bayes_factor_p0 → h0_grid_scan → gerar_contrato_falsificadores → relatorio_final → [commit_resultados] |
| **Artefatos** | `results/ci/` + `docs/cronologia-auditoria/CONTRATO_FALSIFICADORES_RLL.md` |
| **Nota** | Usado nas FASEs 18–22 para obter resultados formais G1–G4 |
| **Status** | ✅ CANÔNICO para validação científica P0 — use quando precisar de MCMC/Bayes novos |

### `real-data-complete-execution.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Real Data Complete Execution |
| **Trigger** | `workflow_dispatch` |
| **Inputs** | `modo` (audit_only/materialize/validate/full); `dataset_group`; `commit_results` |
| **Jobs** | `verify_real_source_signatures` → `real_data_materialization_audit` → `run_all_real` |
| **Artefatos** | `results/real_data/` |
| **Status** | ✅ CANÔNICO para execução de dados reais — substitui validacao_real.yml e START_MANUAL_HERE.yml |

### `rll-real-data-orchestrator.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | RLL Real Data Orchestrator |
| **Trigger** | `workflow_dispatch` |
| **Inputs** | `pipeline_scope` (rll/iml/formulas/book/all); `dataset_group` (geomagnetic/heliophysics/cosmology/all); `mode` (metadata_only/fetch/compute/plots/full) |
| **Scripts** | `scripts/compute_rll_real_pipeline.py`; `tools/iml/iml_pipeline.py`; `scripts/rll_pipeline.py` |
| **Status** | ✅ ativo — mais granular que real-data-complete-execution.yml |

### `unified-workflow-session-orchestrator.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Unified Workflow Session Orchestrator |
| **Trigger** | `workflow_dispatch` |
| **Catalog** | `.github/workflow-orchestrator/session.yml` + `catalog.yml` |
| **Status** | ✅ ativo — usa sistema de catálogo YAML separado |

---

## CAMADA 5 — Pipelines Computacionais

### `bayes_analysis.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Análise Bayesiana RLL vs ΛCDM — entrada manual canônica |
| **Trigger** | `workflow_dispatch` |
| **Script** | `src/run_full_analysis.py` (dynesty nested sampling) |
| **Artefato** | `bayes-analysis-results/` com `ln(B₁₀)`, corner plots |
| **Status** | ✅ ativo — produz F-COS-04 formal |

### `calc-data.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Calcular/Processar dados reais — guarded audit |
| **Trigger** | `workflow_dispatch` |
| **Guard** | `tools/ci/real_data_workflow_policy.sh` |
| **Status** | ✅ ativo |

### `canonical-route-artifacts.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Canonical Route Artifacts |
| **Trigger** | `workflow_dispatch` |
| **Artefato** | `artifacts/canonical-route/` |
| **Status** | ✅ ativo |

### `import-data.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Importar dados reais — guarded audit |
| **Trigger** | `workflow_dispatch` |
| **Guard** | `tools/ci/real_data_workflow_policy.sh` |
| **Status** | ✅ ativo |

### `rll-book-data-pipeline.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | RLL Book Data Pipeline |
| **Trigger** | `workflow_dispatch` |
| **Escopo** | Pipeline de dados para geração do livro RLL |
| **Status** | ✅ ativo |

### `rll-data-pipeline.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | RLL Data Pipeline |
| **Trigger** | `workflow_dispatch` |
| **Script** | `scripts/rll_pipeline.py` |
| **Status** | ✅ ativo |

---

## CAMADA 6 — Validações Científicas Específicas

### `academic-parameter-governance.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Academic Parameter Governance |
| **Trigger** | `push` (paths: tools/validate_academic_parameter_registry.py, docs/yml/ACADEMIC_PARAMETER_REGISTRY.yml, …) |
| **Scripts** | `tools/validate_academic_parameter_registry.py`; `tools/scan_rll_model_evidence.py`; `tools/run_rll_academic_claim_governance.py`; `tools/apply_rll_outcome_protocol.py` |
| **Status** | ✅ ativo — governance automática em push |

### `claim-boundary-quality-gates.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Claim Boundary Quality Gates |
| **Trigger** | `workflow_dispatch` |
| **Script** | `tools/validate_claim_allowed_gate.py` |
| **Status** | ✅ ativo — gate de fronteira de afirmações |

### `desi-dr2-bao-validation.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | DESI DR2 BAO validation |
| **Trigger** | `workflow_dispatch` |
| **Script** | `scripts/check_desi_dr2_bao_covariance.py` |
| **Artefato** | resultados χ² DESI |
| **Status** | ✅ ativo — valida F-COS-03/F-COS-05 |

### `iml_artifact.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | IML Artifact Generator |
| **Trigger** | `workflow_dispatch` |
| **Script** | `tools/iml/iml_pipeline.py --steps 42` |
| **Artefato** | `artifacts/iml/iml_artifact.json` |
| **Status** | ✅ ativo |

### `orbital-shape-angular-momentum-validation.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Orbital Shape Angular Momentum Validation |
| **Trigger** | `workflow_dispatch` |
| **Script** | `scripts/validation/validate_orbital_shape_angular_momentum.py` |
| **Status** | ✅ ativo |

### `orbital-state-vector-v2.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Orbital State Vector V2 |
| **Trigger** | `workflow_dispatch` |
| **Status** | ✅ ativo |

### `rll-balance-report.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | RLL Balance Report |
| **Trigger** | `workflow_dispatch` |
| **Script** | `scripts/rll_balance_report.py --metric bic` |
| **Artefato** | `artifacts/rll_balance/` |
| **Status** | ✅ ativo |

### `unified-geometry.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | unified-geometry |
| **Trigger** | `workflow_dispatch` |
| **Status** | ✅ ativo |

---

## CAMADA 7 — Dados, Sementes e Inventário

### `dense-feature-matrix.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Dense Feature Matrix |
| **Trigger** | `workflow_dispatch` |
| **Script** | `scripts/data_scan/build_dense_behavior_features.py` |
| **Status** | ✅ ativo |

### `raw-data-manifest-status.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Raw Data Manifest Status |
| **Trigger** | `workflow_dispatch` |
| **Job** | `build-raw-data-manifest-status` |
| **Status** | ✅ ativo |

### `real-data-bootstrap-validation.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Real Data Bootstrap Validation |
| **Trigger** | `workflow_dispatch` |
| **Script** | `scripts/data_scan/scan_real_data_bootstrap.py --repo .` |
| **Job** | `scan-real-data-bootstrap` |
| **Status** | ✅ ativo |

### `real-seed-ingestion-plan.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Real Seed Ingestion Plan |
| **Trigger** | `workflow_dispatch` |
| **Job** | `build-real-seed-ingestion-plan` |
| **Status** | ✅ ativo |

### `real-seed-validation-v0.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Real Seed Validation v0 |
| **Trigger** | `workflow_dispatch` |
| **Script** | `scripts/validation/run_real_seed_validations.py` |
| **Status** | ✅ ativo |

### `repo-real-inventory.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | repo-real-inventory |
| **Trigger** | `workflow_dispatch` |
| **Script** | `tools/docs_inventory.py` (gera `docs/YML_WORKFLOWS_INDEX.md`) |
| **Status** | ✅ ativo |

---

## CAMADA 8 — Auxiliares / Específicos

### `android-build.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Android Build |
| **Trigger** | `push` (paths: app/, core/lowlevel_runtime/, build.gradle) |
| **Status** | ✅ ativo — específico para build Android |

### `START_MANUAL_HERE.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | START MANUAL HERE - YML Interoperability Orchestrator |
| **Trigger** | `workflow_dispatch` |
| **Status** | ⚠️ AUXILIAR — use `real-data-complete-execution.yml` para execução de dados reais ou `rll-pipeline-linear-completo.yml` para pipeline canônico |

### `validacao_real.yml`

| Campo | Valor |
|-------|-------|
| **Nome** | Validacao Real RLL |
| **Trigger** | `workflow_dispatch` |
| **Status** | ⚠️ AUXILIAR — supersedido por `real-data-complete-execution.yml` |

---

## Tabela Mestre (Referência Rápida)

| Workflow | Camada | Trigger | Check Obrigatório | Status |
|----------|--------|---------|-------------------|--------|
| `rll-pipeline-linear-completo.yml` | 0 | dispatch | — | ✅ CANÔNICO |
| `python-tests.yml` | 1 | push | `test` | ✅ OBRIGATÓRIO |
| `convention-check.yml` | 1 | PR | `check-conventions` | ✅ OBRIGATÓRIO |
| `formulas-artifacts.yml` | 1 | push | `build-formulas-artifacts` | ✅ OBRIGATÓRIO |
| `formulas-artifacts-validation.yml` | 1 | push/dispatch | `formulas-manifest` | ✅ OBRIGATÓRIO |
| `yml-syntax-validation.yml` | 1 | PR | `validate-yaml` | ✅ OBRIGATÓRIO |
| `RLL-CI.yml` | 2 | dispatch | `rll` (herdado) | ✅ CANÔNICO |
| `RLL_SCIENTIFIC.yml` | 2 | dispatch | `rll` (herdado) | ✅ CANÔNICO |
| `dha-fisher-ci.yml` | 3 | PR | — | ✅ ativo |
| `real-data-contract-ci.yml` | 3 | PR | — | ✅ ativo |
| `rll-structural-integration.yml` | 3 | PR+dispatch | — | ✅ ativo |
| `six-sigma-real-data-controls.yml` | 3 | PR | — | ✅ ativo |
| `validate-academic-correlation-package.yml` | 3 | PR | — | ✅ ativo |
| `validate-cross-repo-relationship-registry.yml` | 3 | PR | — | ✅ ativo |
| `validate-real-dataset-variance-registry.yml` | 3 | PR | — | ✅ ativo |
| `validate-schema-contracts.yml` | 3 | PR+push | — | ✅ ativo |
| `validate-sequence-metrics.yml` | 3 | PR | — | ✅ ativo |
| `rll-validacao-cientifica-completa.yml` | 4 | dispatch | — | ✅ CANÔNICO P0 |
| `real-data-complete-execution.yml` | 4 | dispatch | — | ✅ CANÔNICO dados |
| `rll-real-data-orchestrator.yml` | 4 | dispatch | — | ✅ ativo |
| `unified-workflow-session-orchestrator.yml` | 4 | dispatch | — | ✅ ativo |
| `bayes_analysis.yml` | 5 | dispatch | — | ✅ ativo |
| `calc-data.yml` | 5 | dispatch | — | ✅ ativo |
| `canonical-route-artifacts.yml` | 5 | dispatch | — | ✅ ativo |
| `import-data.yml` | 5 | dispatch | — | ✅ ativo |
| `rll-book-data-pipeline.yml` | 5 | dispatch | — | ✅ ativo |
| `rll-data-pipeline.yml` | 5 | dispatch | — | ✅ ativo |
| `academic-parameter-governance.yml` | 6 | push | — | ✅ ativo |
| `claim-boundary-quality-gates.yml` | 6 | dispatch | — | ✅ ativo |
| `desi-dr2-bao-validation.yml` | 6 | dispatch | — | ✅ ativo |
| `iml_artifact.yml` | 6 | dispatch | — | ✅ ativo |
| `orbital-shape-angular-momentum-validation.yml` | 6 | dispatch | — | ✅ ativo |
| `orbital-state-vector-v2.yml` | 6 | dispatch | — | ✅ ativo |
| `rll-balance-report.yml` | 6 | dispatch | — | ✅ ativo |
| `unified-geometry.yml` | 6 | dispatch | — | ✅ ativo |
| `dense-feature-matrix.yml` | 7 | dispatch | — | ✅ ativo |
| `raw-data-manifest-status.yml` | 7 | dispatch | — | ✅ ativo |
| `real-data-bootstrap-validation.yml` | 7 | dispatch | — | ✅ ativo |
| `real-seed-ingestion-plan.yml` | 7 | dispatch | — | ✅ ativo |
| `real-seed-validation-v0.yml` | 7 | dispatch | — | ✅ ativo |
| `repo-real-inventory.yml` | 7 | dispatch | — | ✅ ativo |
| `android-build.yml` | 8 | push | — | ✅ específico |
| `START_MANUAL_HERE.yml` | 8 | dispatch | — | ⚠️ AUXILIAR |
| `validacao_real.yml` | 8 | dispatch | — | ⚠️ AUXILIAR |

---

## Checks Obrigatórios (Branch Protection)

> Estes 6 checks NÃO PODEM ser removidos ou renomeados — são branch protection requirements.

| Check Name | Workflow Fonte | Trigger |
|-----------|----------------|---------|
| `rll` | `RLL-CI.yml` → `rll-pipeline-linear-completo.yml` | manual dispatch |
| `test` | `python-tests.yml` | push |
| `validate-yaml` | `yml-syntax-validation.yml` | PR |
| `check-conventions` | `convention-check.yml` | PR |
| `build-formulas-artifacts` | `formulas-artifacts.yml` | push |
| `formulas-manifest` | `formulas-artifacts-validation.yml` | push/dispatch |

---

## Guia de Decisão — "Qual workflow usar?"

```
Quero executar o pipeline científico completo?
  → rll-pipeline-linear-completo.yml (modo=completo)

Quero só a ciência (fit + MCMC + Bayes)?
  → RLL-CI.yml ou RLL_SCIENTIFIC.yml (ambos delegam ao pipeline canônico)

Quero reproduzir os resultados P0 formais (MCMC emcee, dynesty)?
  → rll-validacao-cientifica-completa.yml

Quero executar dados reais (fetch/materialize/validate)?
  → real-data-complete-execution.yml

Quero dados reais por domínio (cosmologia, geomagnético, heliofísica)?
  → rll-real-data-orchestrator.yml

Quero análise Bayesiana standalone?
  → bayes_analysis.yml

Quero validar DESI DR2 BAO covariance?
  → desi-dr2-bao-validation.yml

Quero inventário do repositório?
  → repo-real-inventory.yml

Quero apenas executar testes Python?
  → python-tests.yml (automático em push)
```

---

*Documento de referência FASE 25. Próxima atualização: quando novos workflows forem adicionados ou categorias mudarem.*
