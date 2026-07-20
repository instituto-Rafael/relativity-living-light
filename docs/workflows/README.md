# Documentação de Workflows — RLL

Diretório iniciado na **FASE 25** e endurecido na **FASE 25.1** com um **contrato executável** entre documentação e YAML real.

## Ordem de autoridade

1. [`.github/workflow-contract.yml`](../../.github/workflow-contract.yml) — invariantes legíveis por máquina;
2. [`.github/workflows/`](../../.github/workflows/) — implementação operacional;
3. [`tools/validate_workflow_docs.py`](../../tools/validate_workflow_docs.py) — validação determinística;
4. artefatos de validação em `artifacts/workflow-docs/`;
5. índices humanos deste diretório.

Os índices explicam o sistema; o contrato e os YAMLs determinam o estado executável.

## Documentos

| Arquivo | Propósito |
|---|---|
| [INDICE_CANONICO.md](INDICE_CANONICO.md) | Mapa humano dos workflows, camadas, triggers, scripts e status |
| [MAPA_ARTICULACOES.md](MAPA_ARTICULACOES.md) | Grafo de dependências, delegações e lacunas da rede |
| [INDICE_ARTEFATOS.md](INDICE_ARTEFATOS.md) | Rastreabilidade workflow → artefato → resultado científico |
| [FASE_25_1_CONTRATO_EXECUTAVEL.md](FASE_25_1_CONTRATO_EXECUTAVEL.md) | Correções de semântica, fronteira de evidência e precedência temporal |

## Métrica canônica do pipeline

`.github/workflows/rll-pipeline-linear-completo.yml` contém:

- **44 etapas lógicas** executadas pelo orquestrador;
- **8 fases**, da FASE 0 à FASE 7;
- 6 steps físicos no job `deterministic-gate`.

Essas medidas descrevem camadas diferentes e não devem ser reduzidas à expressão ambígua “44 steps”.

## Checks documentados

`deterministic-gate` · `test` · `validate-yaml` · `check-conventions` · `build-formulas-artifacts` · `formulas-manifest`

A presença desses jobs é verificável no repositório. A configuração externa de branch protection permanece `branch_protection_verified=false` até auditoria específica da regra da branch.

## Executar a validação

```bash
python3 tools/validate_workflow_docs.py --strict --write-report
pytest -q tests/test_validate_workflow_docs.py
```

## Navegação rápida

Consulte [`.github/GUIA_WORKFLOWS.md`](../../.github/GUIA_WORKFLOWS.md).
