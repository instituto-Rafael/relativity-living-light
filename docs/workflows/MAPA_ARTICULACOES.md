# Mapa de Articulações — Rede de Workflows RLL

> **Gerado**: 2026-07-20 | **FASE 25** — Refatoração Profissional
>
> Este documento descreve: (1) como os workflows se conectam entre si, (2) o que cada trigger produz, (3) lacunas identificadas na rede.

---

## 1. Grafo de Delegação

```
                        ┌──────────────────────────────────────┐
                        │  rll-pipeline-linear-completo.yml    │
                        │  (Gate Determinístico — FASE 24)     │
                        │  44 steps | 7 fases | 1 job          │
                        └────────────┬─────────────────────────┘
                                     │ uses: (workflow_call)
                    ┌────────────────┴────────────────┐
                    │                                 │
             RLL-CI.yml                     RLL_SCIENTIFIC.yml
          (modo=apenas_ciencia)           (modo=apenas_ciencia)
          check: rll                      check: rll
```

**Legenda**: `uses:` = chamada `workflow_call` (o pipeline canônico é reusável).

---

## 2. Grafo de Triggers Automáticos

```
PUSH para main/claude/*
├── python-tests.yml           → check: test
├── formulas-artifacts.yml     → check: build-formulas-artifacts
├── formulas-artifacts-validation.yml → check: formulas-manifest
│
├── [se paths: schemas/]
│   └── validate-schema-contracts.yml
│
├── [se paths: tools/validate_academic_parameter_registry.py, ...]
│   └── academic-parameter-governance.yml
│
├── [se paths: app/, core/lowlevel_runtime/, build.gradle]
│   └── android-build.yml
│
└── [se paths: src/rll/structural_integration.py, ...]
    └── rll-structural-integration.yml

PULL REQUEST
├── convention-check.yml       → check: check-conventions
├── yml-syntax-validation.yml  → check: validate-yaml
├── dha-fisher-ci.yml
├── six-sigma-real-data-controls.yml
├── validate-academic-correlation-package.yml
├── validate-cross-repo-relationship-registry.yml
├── validate-real-dataset-variance-registry.yml
├── validate-schema-contracts.yml
├── validate-sequence-metrics.yml
├── real-data-contract-ci.yml
└── rll-structural-integration.yml
```

---

## 3. Grafo de Dependências Científicas

```
Dados reais (data/real/cosmology/)
    │
    ├── rll-validacao-cientifica-completa.yml
    │   Job: fit_pantheon_rll → scripts/pantheon/run_rll_vs_pantheon.py
    │       → results/ci/pantheon_fit_*.json
    │   Job: fit_desi_bao → scripts/compute_rll_real_pipeline.py --desi-only
    │       → results/ci/desi_bao_chi2_*.json
    │   Job: joint_mcmc_p0 → python -m data.pipelines.structure_d.run_all --bayes
    │       → results/ci/joint_mcmc_*/
    │   Job: bayes_factor_p0 → src/run_full_analysis.py (dynesty)
    │       → results/ci/bayes_factor_*.json
    │   Job: gerar_contrato_falsificadores
    │       → docs/cronologia-auditoria/CONTRATO_FALSIFICADORES_RLL.md
    │
    ├── bayes_analysis.yml
    │       → src/run_full_analysis.py → ln(B₁₀), corner plots
    │
    ├── desi-dr2-bao-validation.yml
    │       → scripts/check_desi_dr2_bao_covariance.py
    │
    └── real-data-complete-execution.yml
            → results/real_data/

Schemas (schemas/)
    └── validate-schema-contracts.yml
            → scripts/validate_omega_schemas.py
            → scripts/validate_information_evolution_trace.py

Artefatos (artifacts/)
    ├── formulas-artifacts.yml
    │       → tools/formula_artifact_builder.py
    │       → artifacts/formulas/
    ├── canonical-route-artifacts.yml
    │       → artifacts/canonical-route/
    └── iml_artifact.yml
            → tools/iml/iml_pipeline.py
            → artifacts/iml/iml_artifact.json
```

---

## 4. Articulação com `.github/workflow-orchestrator/`

O diretório `.github/workflow-orchestrator/` contém um sistema de catálogo declarativo:

```
.github/workflow-orchestrator/
├── catalog.yml          — inventário de sessões disponíveis
├── session.yml          — definição de sessão de orquestração
└── workflows/
    ├── core/            — workflows de infraestrutura
    ├── real_data/       — workflows de dados reais
    └── science/         — workflows científicos
```

`unified-workflow-session-orchestrator.yml` lê este catálogo para determinar quais workflows executar em sequência. Este é um mecanismo **alternativo** ao pipeline linear — mais flexível mas menos determinístico.

**Relação**: O pipeline linear (FASE 24) é o gate determinístico; o orquestrador de sessão é para composições ad-hoc.

---

## 5. Articulação com `.github/To_add/`

8 workflows pendentes de ativação:

```bash
.github/To_add/
├── 01_*.yml  ...  11_*.yml   (não ativados — aguardam revisão)
```

Estes NÃO fazem parte da rede ativa. Quando ativados, devem ser adicionados a este mapa.

---

## 6. Lacunas Identificadas (TOKEN_VAZIO da Rede)

### L-WF-01: Falta trigger automático para MCMC/Bayes [H, P2]

**Situação atual**: `rll-validacao-cientifica-completa.yml` (que executa MCMC emcee + dynesty) é `workflow_dispatch` puro — não é disparado automaticamente em nenhuma condição.

**Implicação**: Se parâmetros do modelo mudarem (`src/rll/`), o CONTRATO_FALSIFICADORES não é re-gerado automaticamente.

**Proposta**: Adicionar trigger `push` com `paths: src/rll/**, data/pipelines/structure_d/**` em modo `apenas_bayes` (timeout longo — usar `schedule` em vez de `push` se o custo for proibitivo).

**Status**: TOKEN_VAZIO [H] — decisão de custo/benefício pendente.

### L-WF-02: Dois aliases fazem a mesma coisa (baixa prioridade) [C, P3]

`RLL-CI.yml` e `RLL_SCIENTIFIC.yml` são idênticos (ambos delegam ao pipeline linear com `modo=apenas_ciencia`). Existem por compatibilidade histórica.

**Proposta**: Manter os dois (custo zero), documentar que são aliases.

**Status**: Aceitável — sem ação necessária.

### L-WF-03: `START_MANUAL_HERE.yml` não tem caminho claro de migração [C, P2]

`START_MANUAL_HERE.yml` tem inputs mais ricos (`run_profile`, `book_scope`) que `real-data-complete-execution.yml`. Se for removido, esses inputs se perdem.

**Proposta**: Manter como AUXILIAR com header de deprecação. Se inputs forem necessários, migrar para `rll-pipeline-linear-completo.yml` com novo `modo=`.

**Status**: TOKEN_VAZIO [C] — input mapping pendente.

### L-WF-04: Sem índice navegável de artefatos [C, P2]

Os artefatos produzidos pelos workflows estão dispersos em `results/`, `artifacts/`, `docs/cronologia-auditoria/`. Não existe um índice automático de "qual workflow produziu o quê".

**Solução**: `docs/workflows/INDICE_ARTEFATOS.md` (criado nesta FASE 25) + step 43 do pipeline linear gera `PIPELINE_LINEAR_LOG.md` com tabela step→artefato.

**Status**: Parcialmente resolvido por este PR.

### L-WF-05: Sem orquestração de rollback [H, P3]

Se um step crítico do pipeline linear falhar (ex: `joint_mcmc_p0`), não há workflow de rollback ou re-execução parcial além de re-disparar o pipeline inteiro.

**Proposta**: Adicionar input `step_inicial` ao `rll-pipeline-linear-completo.yml` para retomar de um step específico.

**Status**: TOKEN_VAZIO [H] — baixa prioridade, `continue-on-error: true` mitiga.

---

## 7. Convenções de Segurança Aplicadas

Todos os workflows devem satisfazer `tools/audit_github_workflows.py --strict`:

| Requisito | Descrição |
|-----------|-----------|
| `permissions.contents: read` | Sem escrita implícita |
| `persist-credentials: false` | Sem credenciais persistentes |
| `actions/upload-artifact@v4` | Versão pinada v4 |
| `CHECKSUMS.sha256` | Todo artefato real tem checksum |
| `CLAIM_BOUNDARY` env var | Fronteira de afirmações em jobs de output |
| `SYNTHETIC_BOUNDARY` env var | Dados sintéticos marcados |

Violações bloqueiam o check `validate-yaml`.

---

## 8. Histórico de Evolução da Rede

| FASE | PR | Data | Mudança na Rede |
|------|----|------|-----------------|
| FASE 7 | #506 | 2026-07-07 | Criado `rll-validacao-cientifica-completa.yml` (11 jobs P0) |
| FASE 18 | #551 | 2026-07-14 | Resultados rs_star calibrado — primeiro run do pipeline |
| FASE 19 | #553 | 2026-07-14 | rd calibrado G2 fechado |
| FASE 20 | #554 | 2026-07-15 | MCMC emcee G1 + dynesty G3 fechados |
| FASE 22 | #556 | 2026-07-16 | G4 bias E&H fechado |
| FASE 23 | #561 | 2026-07-17 | 7 docs sincronizados |
| FASE 24 | #567 | 2026-07-18 | `rll-pipeline-linear-completo.yml` — 44 steps, gate único |
| FASE 25 | — | 2026-07-20 | Refatoração estrutural + índices + mapa de articulações |

---

*Este mapa deve ser atualizado sempre que um novo workflow for adicionado ou uma articulação mudar.*
