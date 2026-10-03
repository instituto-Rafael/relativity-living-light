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

## Session catalog v3 and capacity profiles

The session catalog is at [`.github/workflow-orchestrator/session.yml`](../../.github/workflow-orchestrator/session.yml). Its read-only inventory scans root workflows for receipts, while dispatch is restricted to explicit manifests under `workflows/tower/` and `workflows/research/`.

| Perfil | Escopo | Budget máximo |
|---|---|---:|
| `quick_session` | structure, contract, tests and governance | 120 min |
| `transit_refactor` | bounded operational tower | 190 min |
| `real_data_session` | real-data custody and metadata audits | 185 min |
| `full_session` | tower plus real-data profile; excludes science shadow | 305 min |
| `science_shadow_session` | deterministic and frontier checks in isolation | 190 min |
| `literature_session` | academic intake and Jekyll preview | 15 min |
| `pages_preview_session` | Jekyll preview artifact | 15 min |

Execution is sequential, fail-fast and single-flight. The largest budget leaves 55 minutes under the parent job's 360-minute timeout. The research workflow generates a preview artifact; it does not deploy to Pages. Candidate relations remain `RELATIONAL_PENDING` and `claim_allowed: false`.

See [RLL_RESEARCH_FRAGMENT_ROUTE_V1.md](RLL_RESEARCH_FRAGMENT_ROUTE_V1.md) for provenance, workflow inputs and review gates.
