# FASE 24.1 — Gate Determinístico do Pipeline RLL

Data: 2026-07-18  
Branch: `fix/fase24-1-deterministic-gate-20260718`  
Pull request: `#568`  
Base imutável: `d720361fb881af4c239ded783904399a549b88d4`  
Estado de claim: `claim_allowed=false`  
Estado de merge: `draft / sem auto-merge`

## 1. Intenção operacional

A FASE 24 criou uma sequência linear de 44 passos, mas permitia que ausência de scripts, falhas de subprocessos e ausência de resultados fossem convertidas em sucesso aparente. A FASE 24.1 substitui essa tolerância por um gate determinístico, sem alterar dados científicos nem promover conclusão física.

Princípio aplicado:

```text
arquivo/entrada ausente -> TOKEN_VAZIO
comando não-zero        -> FAIL
comando concluído       -> OK
fora do modo atual      -> SKIP
```

Nenhum desses estados é convertido silenciosamente em outro.

## 2. Invariantes preservadas

1. `claim_allowed=false` permanece obrigatório.
2. Resultados históricos não são usados como fallback do run atual.
3. Métrica sem arquivo e chave materializados é `TOKEN_VAZIO`.
4. Etapa crítica em `FAIL` ou `TOKEN_VAZIO` bloqueia o gate.
5. O artifact é publicado mesmo quando o gate termina bloqueado.
6. O checkout canônico não persiste credenciais.
7. Os workflows modificados possuem apenas `contents: read`.
8. Não existe commit automático de resultados.
9. Comandos são executados por vetores `argv`, sem `eval`, `os.popen` ou `shell=True`.
10. O modo de pull request do controlador canônico é sempre `dry_run`.
11. Alterações de documentação isolada não disparam o gate científico.
12. Mudanças em `src/**`, `data/**`, `validation/**`, requisitos ou `pyproject.toml` acionam somente o dry-run leve.
13. Workflows científicos legados permanecem manuais.
14. Um gate operacional verde não promove claim científico.

## 3. Arquitetura implantada

### 3.1 Workflow canônico

Arquivo: `.github/workflows/rll-pipeline-linear-completo.yml`

O workflow anterior, com 1.149 linhas, foi reduzido a um controlador que:

1. faz checkout seguro;
2. configura Python 3.11;
3. instala somente o bootstrap necessário;
4. executa `tools/rll_pipeline_deterministic.py`;
5. recalcula `CHECKSUMS.sha256` por `sha256sum`;
6. publica logs, relatórios, contratos e checksums com `if: always()`.

Entradas permitidas:

- `dry_run`
- `apenas_dados`
- `apenas_ciencia`
- `apenas_governanca`
- `completo`

O mesmo arquivo expõe `workflow_call`, permitindo que entradas legadas deleguem ao núcleo sem duplicar implementação.

### 3.2 Orquestrador único

Arquivo: `tools/rll_pipeline_deterministic.py`

O orquestrador preserva a numeração lógica 02–43 e registra para cada etapa:

- fase;
- workflow de origem;
- criticidade;
- comando efetivamente executado;
- código de saída;
- duração;
- estado explícito;
- detalhe;
- caminho do log.

Saídas principais:

- `results/linear/step_status.tsv`
- `results/linear/step_status.json`
- `results/linear/gate_decision.json`
- `results/linear/CONTRATO_FALSIFICADORES_DETERMINISTICO.json`
- `results/linear/CONTRATO_FALSIFICADORES_DETERMINISTICO.md`
- `results/linear/RELATORIO_LINEAR_FINAL.md`
- `results/linear/CHECKSUMS.sha256`
- `logs/linear/step*.log`

### 3.3 Contrato de falsificadores

O contrato F-COS-01..05 lê apenas arquivos existentes no checkout e resultados produzidos no run. Quando a evidência não existe, registra:

```json
{
  "state": "TOKEN_VAZIO",
  "value": null,
  "source": null
}
```

Foram removidos os fallbacks embutidos `3.805`, `0.4387`, `0.30`, `-6.190` e `93.81` como substitutos de execução. Esses números podem permanecer na documentação histórica, mas não são tratados como resultados do run atual.

### 3.4 Validação de schemas

Arquivo: `tools/validate_schema_contracts.py`

O validador:

- lê JSON Schemas de `schemas/`, `docs/contracts/` e `data/schemas/`;
- valida a estrutura pelo draft indicado;
- executa também `tools/validate_schemas_claim_boundary.py`;
- grava `artifacts/schema-contracts/validation.json`;
- retorna código distinto para `OK`, `FAIL` e `TOKEN_VAZIO`.

Resultado observado no dry-run final:

```text
schemas total = 26
schemas OK    = 26
schemas FAIL  = 0
boundary      = OK
```

### 3.5 Entradas legadas

Os workflows abaixo deixaram de executar automaticamente em push, pull request ou cron:

- `.github/workflows/RLL-CI.yml`
- `.github/workflows/RLL_SCIENTIFIC.yml`
- `.github/workflows/bayes_analysis.yml`

Eles permanecem como entradas manuais de compatibilidade e delegam ao workflow canônico no modo `apenas_ciencia`.

O workflow leve `.github/workflows/python-tests.yml` permanece como CI automático geral e agora sempre publica:

- `artifacts/python-tests/pytest.log`
- `artifacts/python-tests/junit.xml`

### 3.6 Migração do contrato de roteamento

Arquivo: `tests/test_scientific_workflow_path_filters.py`

O contrato anterior exigia pull request diretamente nos workflows científicos pesados. A migração formalizou a nova topologia:

```text
mudança científica em PR
        ↓
workflow canônico
        ↓
dry_run determinístico

execução científica pesada
        ↓
workflow_dispatch explícito
        ↓
apenas_ciencia
```

A simulação de filtros usa `fnmatchcase`, compatível com o glob recursivo `data/**` do GitHub. O uso anterior de `PurePosixPath.match` não representava corretamente essa semântica.

## 4. Regra de decisão

O gate operacional é `BLOCKED` quando ocorre pelo menos uma condição:

```text
etapa crítica == FAIL
etapa crítica == TOKEN_VAZIO
modo científico e métrica F-COS sem evidência materializada
```

O gate pode ser `OK`, mas isso não altera automaticamente `claim_allowed=false`. A liberação de claim exige protocolo científico separado e evidência revisada.

## 5. Testes implementados

### 5.1 Gate determinístico

Arquivo: `tests/test_rll_pipeline_deterministic.py`

Cobertura:

- conjunto fechado de estados;
- ausência de métrica vira `TOKEN_VAZIO`;
- etapa crítica ausente bloqueia;
- modo científico exige métricas materializadas;
- `claim_allowed` permanece falso.

### 5.2 Topologia dos workflows

Arquivo: `tests/test_scientific_workflow_path_filters.py`

Cobertura:

- workflows legados são exclusivamente manuais;
- os três delegam ao controlador canônico;
- o controlador possui rotas para código, dados, validação e dependências;
- mudanças apenas documentais permanecem fora do gate científico;
- glob recursivo segue a semântica do GitHub.

### 5.3 Resultado final da suíte

Run: `29631874870`  
Artifact: `8425755083`  
Digest: `sha256:b2ea4a1f3df5a3c790ff26fc1216c50098e14278803337add35e54e4fc247a6a`

```text
493 passed
3 subtests passed
0 failed
32.85s
```

## 6. Execuções observáveis

### 6.1 Primeira execução — bloqueio legítimo

Run: `29631536058`  
Conclusão: `failure`  
Artifact: `8425625877`  
Digest: `sha256:3ba5f75c3cd044ba3c81d241111944907bbbd8cfe5af4d9797662b9108d7dd7b`

O gate bloqueou porque o auditor exigia duas invariantes explícitas no workflow canônico:

1. geração final de `CHECKSUMS.sha256` por `sha256sum`;
2. ponte textual para `.github/workflows/real-data-complete-execution.yml`.

A falha não foi mascarada. Ela produziu artifact e originou correção específica.

### 6.2 Segunda execução — política corrigida

Run: `29631598608`  
Conclusão: `success`  
Artifact: `8425648013`  
Digest: `sha256:7aa3cf122f0d5f766c2d624c256ed94d8892b1d28ec2262a9c154b98bf2a1b28`

Resultados:

```text
status = OK
claim_allowed = false
blocking_steps = []
YAML válidos = 131
schemas = 26/26 OK
checksums = 10
```

### 6.3 Execução final do gate

Run: `29631874871`  
Conclusão: `success`  
Artifact: `8425745025`  
Digest: `sha256:faa3fbdd38d1b7d3adb54cf153b6549efaaed3680845af4d0a703a0200b821e4`

Resultados:

```text
status = OK
claim_allowed = false
blocking_steps = []
metric_token_vazio = []
```

No modo `dry_run`, etapas fora da FASE 0 são corretamente registradas como `SKIP`; elas não são chamadas de `OK` nem de `TOKEN_VAZIO`.

### 6.4 Painel final do commit técnico

| Verificação | Run | Resultado |
|---|---:|---|
| RLL FASE 24.1 — Gate Determinístico | `29631874871` | `success` |
| Python tests | `29631874870` | `success` |
| YAML Syntax Validation Gate | `29631874910` | `success` |
| Convention Consistency Check | `29631874889` | `success` |
| formulas-artifacts | `29631874881` | `success` |

## 7. Cadeia de commits anterior ao selo final

| Ordem | Commit | Função |
|---:|---|---|
| 1 | `57b946d84c9c5d88a90dbedd85eb3c92dab57894` | orquestrador determinístico |
| 2 | `21b1818fa8dc185f383a10c8a30285133be826d6` | substituição do workflow permissivo |
| 3 | `dd75d25e9107cfc5094c28335a73960a92c4ad7c` | rota manual do RLL-CI |
| 4 | `34cff00ecc1943b7dfc2cab3ca5a576741b1ed9f` | rota manual do RLL_SCIENTIFIC |
| 5 | `260aa5e9cf8fa1e0174f5bca99e07458df4f7d0b` | remoção de push/PR/cron Bayes duplicados |
| 6 | `2b6eae9de262312f462b47603c9ae6a1383f2941` | validador de schemas |
| 7 | `aa5304db41fd6b5765064ec35541f00171fcb358` | bootstrap de `jsonschema` |
| 8 | `2003a61b33326e00d933284beeee63f9a741d230` | testes do gate |
| 9 | `b06ad1433ae2502e53d5ac9b20c87df90cfcdaf0` | primeira cadeia de custódia |
| 10 | `260093bef94b982d1061a6cdb29a97c8a7cc3191` | política canônica de real-data e sha256sum |
| 11 | `08de807e713261219533813bb0599c370b3bfbc3` | recibo auditável do pytest |
| 12 | `830d76aa48e11341b132303096f1ea21705e7d74` | roteamento PR científico para dry-run canônico |
| 13 | `4e0d4dbca16a52317d955ff7cfe013a31b1318f4` | migração dos testes de topologia |
| 14 | `440855d40351d406b534066404243627c7ce6ad9` | correção da semântica recursiva dos filtros |

Este arquivo atualizado constitui o commit final de organização e rastreabilidade. O hash do próprio selo é obtido diretamente no histórico Git para evitar autorreferência circular.

## 8. Estado final

```text
branch_status   = ahead
behind_by       = 0
technical_gate  = OK
test_suite      = OK
claim_allowed   = false
PR              = draft
merge_allowed   = false até revisão explícita
scientific_data = unchanged
```

Arquivos alterados: 10  
Commits anteriores ao selo: 14  
Dados científicos modificados: 0  
Fallbacks científicos admitidos: 0

## 9. Rollback

O rollback é a reversão integral do PR `#568`. Como os dados científicos não foram alterados e não existe escrita automática, não há migração de dados, alteração de banco ou recuperação de estado externo.

---

`ψ intenção → χ observação → ρ falso-verde → Δ gate determinístico → Σ evidência auditável → Ω claim bloqueado até prova`
