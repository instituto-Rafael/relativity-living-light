# FASE 25.1 — Contrato Executável da Rede de Workflows

> Estado: implementação estrutural · `claim_allowed=false`
>
> Objetivo: fazer o mapa da FASE 25 responder automaticamente ao território executável do repositório.

## 1. Princípio

A documentação humana continua necessária para explicar intenção e contexto, mas a **fonte de verdade executável** passa a ser:

1. `.github/workflow-contract.yml` — invariantes declaradas;
2. `.github/workflows/*.yml` — implementação operacional;
3. `tools/validate_workflow_docs.py` — comparação determinística;
4. `artifacts/workflow-docs/` — recibo consultável de cada validação.

O `INDICE_CANONICO.md` permanece como mapa humano. Quando houver divergência, o contrato e o YAML prevalecem até que o índice seja regenerado.

## 2. Métricas separadas

O pipeline canônico possui três medidas diferentes, que não devem ser confundidas:

| Medida | Valor | Significado |
|---|---:|---|
| Workflows ativos | 44 | Arquivos executáveis diretamente em `.github/workflows/` |
| Steps físicos do job canônico | 6 | Entradas da lista `jobs.deterministic-gate.steps` |
| Etapas lógicas | 44 | Sequência interna 01–44 executada pelo orquestrador Python |
| Fases lógicas | 8 | FASE 0 até FASE 7 |

Assim, “44 steps” sozinho é ambíguo. A forma canônica é: **44 etapas lógicas, distribuídas em 8 fases, encapsuladas por 6 steps físicos do GitHub Actions**.

## 3. Checks e limite de evidência

O contrato confirma localmente que os workflows e jobs documentados existem. Ele não consulta regras externas do GitHub.

Portanto:

```text
job presente no repositório != check exigido pela branch protection
```

A lista de checks é classificada como `repository_local_only` e `branch_protection_verified=false` até existir evidência obtida da configuração da branch.

## 4. Política temporal dos resultados científicos

A precedência ocorre por campo, não por substituição cega do run inteiro:

1. Um valor calculado por run completo e válido pode se tornar o valor corrente da mesma linhagem.
2. Um run parcial atualiza somente os campos que realmente calculou.
3. Um campo `null` ou `TOKEN_VAZIO` em run parcial não sobrescreve valor numérico histórico válido.
4. Mudança de dataset, priors, código ou método cria nova linhagem comparável; não apaga automaticamente a anterior.
5. Resultado invalidado deve permanecer preservado com `status=INVALIDATED` e justificativa, nunca ser removido silenciosamente.

Regra central:

> **TOKEN_VAZIO não apaga evidência histórica**; ele registra ausência na execução ou linhagem atual.

## 5. Unidade mínima de proveniência

Todo resultado científico futuro deverá carregar:

```yaml
result_id: F-COS-04
run_id: "<github-run-id>"
commit_sha: "<40-hex>"
execution_mode: completo
value: null
uncertainty: null
unit: dimensionless
status: TOKEN_VAZIO
method: dynesty
artifact_path: artifacts/bayes_factor/bayes_factor_result.json
artifact_sha256: TOKEN_VAZIO
dataset_lineage:
  pantheon_plus: "<sha256>"
  desi_dr2: "<sha256>"
claim_allowed: false
```

Sem `run_id`, commit, método e linhagem de dados, um número pode ser histórico, mas não é promovido a estado canônico.

## 6. Execução

```bash
python3 tools/validate_workflow_docs.py --strict --write-report
pytest -q tests/test_validate_workflow_docs.py
```

Saídas:

- `artifacts/workflow-docs/workflow_registry.json`
- `artifacts/workflow-docs/WORKFLOW_DOCS_REPORT.md`

## 7. Próximo vetor

A FASE 25.1 fecha a divergência entre mapa e runtime. A FASE 26 deverá materializar o ledger por run, validar manifests contra schema e aplicar a política temporal automaticamente.

\[
R_3=\langle
F_{ok}=contrato\ executável,
F_{gap}=ledger\ científico\ ainda\ não\ materializado,
F_{next}=manifesto\ canônico\ por\ run
\rangle
\]
