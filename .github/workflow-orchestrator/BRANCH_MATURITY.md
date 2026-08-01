# RLL — Topologia de Maturidade Evolutiva por Branches

Estado: `ACTIVE_GOVERNANCE`  
Efeito científico: `NONE`  
`claim_allowed=false`  
`branch_protection_verified=false`

## 1. Casa da obra

O repositório separa oficina, integração, estabilização e estado canônico:

```text
branch de trabalho não protegida → rll/lab → rll/integration → rll/release → main
```

- branch de trabalho não protegida: construção delimitada, hipótese de implementação e testes focados;
- `rll/lab`: laboratório reprodutível; aceita somente branches não protegidas;
- `rll/integration`: entrelace entre dados, código, testes, governança e documentação;
- `rll/release`: candidato estabilizado, com evidência ou lacuna explicitamente auditável;
- `main`: estado canônico; recebe somente `rll/release`.

Nenhum salto lateral ou promoção direta para `main` é aceito pelo gate.

## 2. Vetor de maturidade

Cada promoção calcula:

```text
M = Topologia + AmplitudeSemântica + Validação + Evidência + Governança
```

| dimensão | máximo | significado |
|---|---:|---|
| topologia | 20 | transição ocorre pela aresta autorizada |
| amplitude semântica | 20 | domínios modificados são classificados e visíveis |
| validação | 20 | testes focados e proporcionais ao estágio passam |
| evidência | 20 | há receipt/proveniência ou lacuna explícita e verificável |
| governança | 20 | contratos, YAML e fronteiras de claim permanecem coerentes |

Limiar por etapa:

| destino | mínimo |
|---|---:|
| `rll/lab` | 40 |
| `rll/integration` | 60 |
| `rll/release` | 80 |
| `main` | 90 |

Pontuação não substitui nenhum bloqueio duro. Credencial versionada, YAML inválido,
`claim_allowed=true`, transição proibida ou teste essencial falho mantêm `BLOCKED`.

## 3. Amplitude semântica dos caminhos

Os caminhos modificados são classificados como:

- dados;
- implementação;
- testes;
- governança;
- documentação;
- evidência/proveniência;
- outro.

A amplitude mede cobertura estrutural, não importância científica. Muitos arquivos
não compensam ausência de teste, evidência, falsificador ou custódia.

## 4. TOKEN_VAZIO como estado preservado

Em `release` e `main`, alteração de dados ou implementação deve apresentar:

1. evidência/proveniência rastreável; **ou**
2. `TOKEN_VAZIO` acompanhado de próximo passo verificável.

Exemplo válido:

```text
TOKEN_VAZIO_INDEPENDENT_REPLICATION
F_next: executar replicação independente usando os mesmos inputs e tolerância registrada.
```

Ausência não vira zero, sucesso ou conclusão.

## 5. Orquestrador único

`.github/workflows/unified-workflow-session-orchestrator.yml` opera em dois planos:

1. `pull_request`: executa o gate de maturidade e produz receipt JSON/Markdown;
2. `workflow_dispatch`: executa sessões sequenciais com perfil adaptativo.

Perfil `auto`:

| ref | perfil resolvido |
|---|---|
| `rll/lab` | `quick_session` |
| `rll/integration` | `real_data_session` |
| `rll/release` | `full_session` |
| `main` | `full_session` |

O YML declara rotas e limites. A decisão algorítmica permanece externalizada em
`tools/branch_maturity_gate.py`, coberta por testes.

## 6. Certificação CORE — fronteira correta

A cadeia pode produzir **evidência de domínio operacional**: uso avançado da
ferramenta, receipts, testes, rastreabilidade e critérios de promoção. Isso pode
sustentar portfólio, avaliação interna ou preparação para certificações.

Ela não emite certificação profissional, diploma, licença, conformidade externa
nem promessa salarial. Esses estados dependem de autoridade externa identificada,
critérios publicados e verificação independente.

Estado atual:

```text
TECHNICAL_MATURITY_EVIDENCE = IMPLEMENTED
EXTERNAL_CERTIFICATION = TOKEN_VAZIO_EXTERNAL_AUTHORITY
F_next: vincular uma matriz de competências a uma autoridade certificadora real,
        sem converter evidência interna em credencial externa.
```

## 7. Receipt mínimo

Cada decisão materializa:

- schema;
- commit SHA;
- workflow e job;
- `claim_allowed=false`;
- `publication_effect=NONE`;
- hash dos inputs;
- decisão;
- score e limiar;
- arquivos e domínios modificados;
- resíduos;
- próximo estado verificável.

Sem receipt, o estado é `TOKEN_VAZIO_EXECUTION_EVIDENCE`.
