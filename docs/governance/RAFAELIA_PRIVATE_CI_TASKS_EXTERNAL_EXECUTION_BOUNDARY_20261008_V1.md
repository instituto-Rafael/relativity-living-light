# RAFAELIA Ω — CI privada: ChatGPT Tasks, executor externo e receipt (V1)

**Data da reconciliação:** 2026-10-08  
**Autoridade da afirmação operacional:** declaração do responsável na sessão WorkflowMusica  
**Estado:** USER_DECLARED_ARCHITECTURE / DOCUMENTARY_BOUNDARY / UNTESTED_EXTERNAL_EXECUTION  
**claim_allowed:** `false`

## 1. Corrigenda da sessão inteira

O responsável esclareceu: a **CI privada não executa dentro do GitHub Actions**. A orquestração interna usada no GPT ocorre por meio de **Tasks do ChatGPT**, enquanto a execução de CI, quando realizada, acontece em um **executor externo**.

O registro atual corrige a associação anterior entre `GitHub Actions` e `PRIVATE_CI_EXECUTED`. A correção é prospectiva e epistemológica; **não apaga** históricos de workflow nem converte `FAIL` em `PASS`.

### Relação entre planos

```text
GPT TASK (agenda/orquestra/consulta)
    -> autorização e contrato de teste
    -> EXECUTOR EXTERNO (CI, shell, compilação, device/runtime)
    -> RECEIPT EXTERNO (identidade, hashes, resultados e escopo)
    -> μREAD / validação de proveniência
    -> GitHub / Drive μWRITE (índice de evidência)
    -> gate científico, jurídico e de publicação separados
```

Não há identidade entre `TASK` e `EXECUTION`. Uma Task não fornece, por si só, shell persistente, equipamento físico, build de APK ou binário de teste. A invocação de qualquer recurso externo depende das ferramentas e permissões efetivamente disponíveis na execução da Task.

## 2. Correção de inferências sobre GitHub Actions

As chamadas de GitHub neste ciclo retornaram fatos observacionais, inclusive:

- RLL PR #1076, HEAD `67140f891a7cfabd929f010e0a3940fda50ceaaa`: 17 sucesso / 5 falha dentre 22 runs de workflows consultados.
- RLL PR #1077: houve runs com sucesso e falha documental; snapshots de HEAD distintos são históricos, não soma cumulativa de gates atuais.
- Papers PR #133: o GitHub reportou `FAILURE` com steps ausentes e logs indisponíveis nos jobs consultados.

Esses resultados sustentam `GITHUB_PROVIDER_WORKFLOW_OBSERVED`, **não** `PRIVATE_CI_PASS`, `PRIVATE_CI_FAIL` ou `EXTERNAL_PHYSICAL_EXECUTION`.

Mesmo quando uma workflow do GitHub efetivamente reporta `completed/success`, ela continua um dado da superfície GitHub. A política de **CI privada externa** é outra rota, com recibo próprio. Não se deve declarar `GITHUB_ACTIONS_NEVER_EXECUTED` globalmente, pois há observações de runs: a afirmação mais precisa é que **GitHub Actions não é o executor autorizado da CI privada descrita pelo usuário**.

## 3. Tipagem formal das capacidades e ausências

| Campo | Estado sob esta arquitetura | Consequência |
|---|---|---|
| `GPT_TASKS` | `ORCHESTRATOR_ONLY` | Agendar, observar, classificar e registrar, quando as ações estiverem disponíveis |
| `PRIVATE_CI_ON_GITHUB_ACTIONS` | `NOT_APPLICABLE_BY_USER_POLICY` | Não usar status Actions como comprovante de CI privada |
| `EXTERNAL_CI_RUNNER` | `USER_DECLARED_EXTERNAL` | Identidade/ambiente do executor exigem receipt |
| `EXTERNAL_CI_EXECUTION` | `TOKEN_VAZIO_EVIDENCE` | Não afirmar execução ou aprovação sem comprovante de origem |
| `EXTERNAL_DEVICE_RECEIPT` | `TOKEN_VAZIO_EVIDENCE` | Nenhum dispositivo é presumido |
| `GPT_TASK_SCHEDULE` | `NOT_CREATED_IN_THIS_RECONCILIATION` | Documento não cria agendamento |
| `GITHUB_WORKFLOW_STATUS` | `OBSERVATION_ONLY` | Preserva logs e conclusões no escopo do provedor |
| `SCIENCE_CLAIM` | `BLOCKED` | Gate científico independente |
| `CLAIM_ALLOWED` | `false` | Nunca derivar de um status isolado |

`TOKEN_VAZIO` é **informação tipada sobre uma obrigação de prova**, não o número 0 nem a conclusão de que um sistema falhou. `NOT_APPLICABLE` é diferente de `NOT_RUN`: no primeiro, a rota não faz parte do contrato; no segundo, a operação era aplicável, mas não ocorreu ou não possui evidência.

## 4. Contrato mínimo para um receipt de CI externa

```yaml
receipt_schema: rafaelia.external_private_ci.v1
source_repository: TOKEN_VAZIO
source_commit_sha: TOKEN_VAZIO
source_tree_or_artifact_sha256: TOKEN_VAZIO
executor_id: TOKEN_VAZIO
executor_location_class: EXTERNAL
authorization_ref: TOKEN_VAZIO
task_prompt_or_dispatch_ref: TOKEN_VAZIO
toolchain_and_versions: TOKEN_VAZIO
target_architecture: TOKEN_VAZIO
tests_and_predeclared_falsifiers: TOKEN_VAZIO
start_and_end_time: TOKEN_VAZIO
exit_status: TOKEN_VAZIO
input_manifest_and_sha256: TOKEN_VAZIO
output_manifest_and_sha256: TOKEN_VAZIO
stdout_stderr_or_log_digest: TOKEN_VAZIO
device_receipt: TOKEN_VAZIO
license_provenance_gate: TOKEN_VAZIO
independent_review: TOKEN_VAZIO
rollback_reference: TOKEN_VAZIO
claim_allowed: false
```

Este bloco é **modelo declarativo** e não é YAML de GitHub Actions nem evidência de uma execução. Não usar secrets ou dados identificadores em recibos públicos; hashes e referências devem respeitar direitos/licenças e privacidade.

## 5. Gates e falsificadores

- **P0 — autoridade/autoria/licença:** nenhuma incorporação/redistribuição antes da verificação por ativo.
- **‡TASK:** a Task possui instrução, limite, autorização e observabilidade; `TASK_CREATED != TASK_EXECUTED`.
- **‡EXTERNAL:** execução externa comprovada, com HEAD exato, ambiente, código de saída e hashes. `TASK_EXECUTED != TEST_EXECUTED`.
- **‡RECEIPT:** validação independente da identidade, conteúdo, integridade e relação do receipt com HEAD e executor.
- **‡METHOD:** hipóteses e falsificadores congelados antes dos resultados relevantes; preservar negativos.
- **‡SCIENCE:** reprodução e validade observacional separadas da execução e da conformidade.
- **‡PUBLICATION:** liberação explícita por reivindicação, não por contagem de workflows.
- **†FAILURE:** diferença numérica em WS01 continua `NUMERICAL_METHOD_CONTRACT_FAIL`; não virar automaticamente `PHYSICAL_MODEL_FALSIFIED` nem `FRAUD`.

## 6. Operação e rollback

Sem transformar esta nota em execução:

1. Task interna pode solicitar/levar a cabo **consulta e preparação**, se ferramentas e permissões estiverem disponíveis.
2. Executor externo roda testes com ambiente e contrato próprios; só esse executor pode emitir `EXECUTION_RECEIPT`.
3. A rota de ingestão verifica SHA, manifesto, licença, privacidade e proveniência antes de gravar μ-receipt.
4. Qualquer `TOKEN_VAZIO` que dependa de teste físico permanece aberto até tal execução observável.
5. O rollback deste ajuste é reverter **apenas** este documento na branch draft. Não alterar origem, resultados históricos ou registro numérico WS01.

## R3

- `F_ok`: rota privada proposta esclarecida pelo responsável, tipos e gates documentados, separação provider/task/executor estabelecida.
- `F_gap`: nenhuma Task foi criada por esta revisão; nenhum executor externo foi conectado ou teve execução comprovada nesta revisão; receipts de CI privada ainda precisam de fonte.
- `F_next`: documentar o primeiro receipt verificável de executor externo e amarrá-lo à Task/HEAD que o solicitou, sem misturar GitHub Actions com a CI privada.

**SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM**  
**TOKEN_VAZIO ≠ 0**  
**IMPLEMENTED_UNTESTED ≠ PASS**  
**claim_allowed=false**
