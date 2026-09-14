# Guia de Workflows — RLL

> Navegação rápida. Contrato verificável: [`workflow-contract.yml`](workflow-contract.yml). Arquitetura Ω: [`docs/workflows/RLL_WORKFLOW_ARCHITECTURE_OMEGA_V1.md`](../docs/workflows/RLL_WORKFLOW_ARCHITECTURE_OMEGA_V1.md). Governança operacional: [`docs/governance/RLL_OPERATIONAL_GOVERNANCE.md`](../docs/governance/RLL_OPERATIONAL_GOVERNANCE.md). Documentação ampliada: [`docs/workflows/`](../docs/workflows/).

## Pipeline Canônico

**`.github/workflows/rll-pipeline-linear-completo.yml`**

- **44 etapas lógicas** numeradas de 01 a 44;
- **8 fases** internas, da FASE 0 à FASE 7;
- **6 steps físicos** no job GitHub Actions `deterministic-gate`;
- triggers: `workflow_dispatch`, `workflow_call` e `pull_request`;
- em pull request, o modo é forçado para `dry_run`.

Input reutilizável/manual: `modo` (`completo`, `apenas_ciencia`, `apenas_governanca`, `apenas_dados`, `dry_run`).

## Checks documentados no repositório

| Contexto/job local | Workflow |
|---|---|
| `deterministic-gate` | `rll-pipeline-linear-completo.yml` |
| `test` | `python-tests.yml` |
| `validate-workflow-architecture` | `yml-syntax-validation.yml` |
| `yaml-deep-audit` | `yaml-deep-audit.yml` |
| `check-conventions` | `convention-check.yml` |
| `build-formulas-artifacts` | `formulas-artifacts.yml` |
| `formulas-manifest` | `formulas-artifacts-validation.yml` |
| `epistemic-contract` | `frontier-research-composition.yml` |
| `governance-quality-gate` | `rll-governance-quality-gate.yml` |

Esta tabela comprova que os jobs existem no código, mas **não comprova a configuração de branch protection** no GitHub. A proteção externa deve ser verificada separadamente; no contrato local, `branch_protection_verified=false`.

## Arquitetura Ω

A composição dos workflows segue a fronteira:

```text
YAML declarativo
  → módulo ou script testado
    → execução limitada
      → receipt verificável
        → residual
          → decisão versionada
```

O gate `validate-workflow-architecture` verifica todos os YAMLs e trata como erro, nos workflows gerenciados:

- permissões ausentes;
- timeout ausente;
- checkout com credenciais persistentes;
- `pull_request_target` sem exceção versionada;
- contexto de evento não confiável interpolado em `run`;
- programa excessivamente longo embutido no YAML;
- ausência de artefato/receipt.

Referências externas de Actions ainda não pinadas por SHA completo permanecem como aviso de migração, não como falsa declaração de conformidade.

## Auditoria YAML profunda

O job `yaml-deep-audit` percorre cada `.yml` e `.yaml`, rejeita chaves duplicadas, classifica todos os arquivos, cruza caminhos locais, detecta inventário desatualizado e amplia a revisão de workflows para permissões, Actions mutáveis, falhas engolidas, dependências sem lock, interpolação de entradas em shell e métricas científicas embutidas no YAML.

A decisão `REVIEW_REQUIRED` é um receipt de dívida observada; não é falha sintática nem promoção científica. A matriz `yaml_file_matrix.tsv` preserva uma linha auditável para cada arquivo.

## Governança operacional

O job `governance-quality-gate` valida contratos de engenharia, qualidade, dados, segurança, ciência, biomedicina, biologia, bioquímica, fauna, flora, ecossistemas e engenharia. Ele gera receipt e relatório com `F_ok`, `F_gap` e `F_next`, mantendo `certification_claim=false`, `conformity_claim=false` e `claim_allowed=false` por padrão.

O workflow novo usa `contents: read`, não recebe segredos, fixa a action de checkout por SHA completo e trata referências legadas mutáveis como dívida progressiva observável, não como aprovação silenciosa.

## Decisão Rápida

| Objetivo | Workflow |
|---|---|
| Gate completo | `rll-pipeline-linear-completo.yml` com `modo=completo` |
| Ciência pelo alias canônico | `RLL-CI.yml` |
| Alias científico histórico compatível | `RLL_SCIENTIFIC.yml` |
| Auditoria integral de YAML/YML | `yaml-deep-audit.yml` |
| Validação científica P0/MCMC/Bayes | `rll-validacao-cientifica-completa.yml` |
| Dados reais | `real-data-complete-execution.yml` |
| Análise Bayesiana standalone | `bayes_analysis.yml` |
| DESI BAO covariance | `desi-dr2-bao-validation.yml` |
| Fronteira S/P/C e recibos shadow | `frontier-research-composition.yml` |
| Governança, risco, dados, segurança e ética | `rll-governance-quality-gate.yml` |
| IML artifact | `iml_artifact.yml` |
| Inventário do repositório | `repo-real-inventory.yml` |

## Workflows auxiliares

- `validacao_real.yml` → prefira `real-data-complete-execution.yml`;
- `START_MANUAL_HERE.yml` → mantenha apenas quando seus inputs adicionais forem necessários.

## Validação do mapa contra o território

```bash
python3 tools/workflow_architecture.py \
  --contract .github/workflow-architecture/invariants.v1.yml \
  --output-dir artifacts/yml-syntax-validation \
  --strict
python3 tools/deep_yaml_audit.py \
  --output-dir artifacts/yaml-deep-audit \
  --fail-on none
python3 tools/validate_workflow_docs.py --strict --write-report
python3 scripts/rll_governance_audit.py --strict --write-report
pytest -q tests/test_workflow_architecture.py tests/test_validate_workflow_docs.py
python3 -m unittest -v tests/test_deep_yaml_audit.py tests/test_rll_governance_audit.py
```

Recibos produzidos:

- `artifacts/yml-syntax-validation/workflow_architecture_report.json`;
- `artifacts/yml-syntax-validation/WORKFLOW_ARCHITECTURE_REPORT.md`;
- `artifacts/yml-syntax-validation/yaml_parse_report.tsv`;
- `artifacts/yaml-deep-audit/deep_yaml_audit.json`;
- `artifacts/yaml-deep-audit/DEEP_YAML_AUDIT.md`;
- `artifacts/yaml-deep-audit/yaml_file_matrix.tsv`;
- `artifacts/yaml-deep-audit/findings.tsv`;
- `artifacts/workflow-docs/workflow_registry.json`;
- `artifacts/workflow-docs/WORKFLOW_DOCS_REPORT.md`;
- `artifacts/governance/rll_governance_receipt.json`;
- `artifacts/governance/RLL_GOVERNANCE_REPORT.md`.

## Articulação interna

- Contrato: [`.github/workflow-contract.yml`](workflow-contract.yml)
- Contrato da arquitetura: [`.github/workflow-architecture/invariants.v1.yml`](workflow-architecture/invariants.v1.yml)
- Perfil de governança: [`governance/rll-governance-profile.v1.json`](../governance/rll-governance-profile.v1.json)
- Governança operacional: [`docs/governance/RLL_OPERATIONAL_GOVERNANCE.md`](../docs/governance/RLL_OPERATIONAL_GOVERNANCE.md)
- FASE 25.1: [`docs/workflows/FASE_25_1_CONTRATO_EXECUTAVEL.md`](../docs/workflows/FASE_25_1_CONTRATO_EXECUTAVEL.md)
- Catálogo alternativo: [`.github/workflow-orchestrator/`](workflow-orchestrator/)
- Workflows ainda não ativos: [`.github/To_add/`](To_add/)
