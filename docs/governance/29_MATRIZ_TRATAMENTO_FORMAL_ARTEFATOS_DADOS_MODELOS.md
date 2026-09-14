# Matriz de Tratamento Formal para Artefatos, Dados, Modelos e Evidências

## Status

- **Família:** governance / evidence-chain / data-treatment / formal-method
- **Tipo:** matriz operacional canônica
- **Uso:** classificar cada coisa antes de incorporar ao sistema
- **Regra:** nenhuma entrada vira conhecimento sem natureza, origem, risco, evidência e próxima ação

---

## 1. Objetivo

Este documento define uma matriz formal para tratar qualquer elemento do ecossistema RAFAELIA/RLL.

O objetivo é impedir que coisas de naturezas diferentes sejam misturadas como se fossem equivalentes.

A regra base é:

```text
símbolo ≠ hipótese ≠ dado ≠ evidência ≠ prova ≠ código ≠ execução ≠ auditoria
```

Cada coisa precisa receber:

- nome;
- família;
- natureza;
- origem;
- status epistêmico;
- risco;
- evidência;
- relação com outros artefatos;
- próxima ação.

---

## 2. Matriz principal

| Classe | Natureza | Tratamento formal | Risco se maltratada | Próxima ação típica |
|---|---|---|---|---|
| Símbolo | orientação/metáfora | explicar significado e limite | virar falsa prova | declarar como metáfora ou hipótese |
| Parábola | compressão narrativa | extrair invariante e camadas | encerrar debate sem evidência | mapear Sistema 1/Sistema 2 |
| Hipótese | proposição testável | definir falsificador | virar crença operacional | criar teste ou critério de refutação |
| Dado bruto | entrada observada | registrar origem e contexto | virar verdade automática | validar fonte e licença |
| Documento | artefato semântico | indexar pergunta, contexto, método | virar texto solto | criar nó no ledger |
| Log | evidência parcial | preservar timestamp e ambiente | ser tratado como prova total | cruzar com execução e commit |
| Código | unidade executável | testar, revisar e versionar | executar sem controle | CI, sandbox, rollback |
| Script sensível | execução com risco | isolar e auditar permissões | dano operacional | revisão de segurança |
| Dataset | coleção de dados | registrar origem, licença e finalidade | treino sem consentimento | Data Card / cadeia de custódia |
| Token | fragmento representacional | tratar como recorte semântico | apagar autoria por fragmentação | mapear derivação e finalidade |
| Embedding | representação vetorial | tratar como derivado semântico | capturar semântica sem governança | auditoria de uso e retenção |
| Peso de modelo | traço estatístico | tratar como estado derivado | negar contribuição de origem | registrar pipeline e fontes |
| Modelo | sistema derivado | documentar treino, dados e limites | caixa-preta sem governança | Model Card / avaliação |
| Saída de IA | resultado condicionado | marcar incerteza e origem provável | ser confundida com verdade | revisão humana/auditoria |
| Commit | registro de mudança | vincular motivo, arquivo e teste | mudança sem contexto | ligar ao ledger |
| Issue/PR | debate operacional | registrar decisão e pendência | dispersão decisória | fechar com critério |
| E-mail bloco | origem/custódia | aplicar Tail Protocol | perder cadeia temporal | vincular Drive/Calendar/GitHub |
| Evento Calendar | âncora temporal | registrar revisão, cor e link | virar lembrete solto | vincular ao bloco de evidência |
| Arquivo Drive | corpo documental | classificar sensibilidade e família | misturar privado/público | mover/rotular/ledger |
| Socket/runtime | canal reativo | definir protocolo, permissão e log | reflexo sem controle | sandbox e política |
| Hardware/edge | corpo físico | medir, testar e isolar | promessa sem benchmark | ensaio de bancada |
| TOKEN_VAZIO | lacuna conhecida | registrar falta e próxima busca | inventar preenchimento | abrir gap auditável |

---

## 3. Estados epistêmicos

Todo artefato deve receber um estado:

| Estado | Significado |
|---|---|
| `symbolic` | símbolo/metáfora útil |
| `hypothesis` | hipótese ainda não validada |
| `evidence` | evidência parcial ou documental |
| `validated` | passou por teste/revisão suficiente |
| `sensitive` | contém ou pode conter dado protegido |
| `operational` | executa ou altera estado |
| `deprecated` | substituído ou obsoleto |
| `gap` | lacuna explicitamente registrada |
| `blocked` | depende de permissão, dado ou ferramenta |
| `audit_required` | exige revisão antes de uso |

---

## 4. Campos mínimos de ledger

```csv
id,nome,familia,tipo,natureza,status,origem,evidencia,risco,relacoes,proxima_acao
```

Exemplo:

```csv
GOV-0028,Observador Recursivo Treinamento Governanca Privacidade,governance,documento,protocolo,validated,chat/GitHub,commit,baixo,GOV-0029;OMEGA-GA,ligar aos schemas
```

---

## 5. Regra de execução

Antes de executar qualquer coisa:

```text
1. Identificar natureza
2. Confirmar origem
3. Classificar risco
4. Verificar evidência
5. Definir sandbox
6. Registrar auditoria
7. Executar somente se permitido
8. Registrar resultado
9. Atualizar ledger
```

---

## 6. Regra de treinamento e embeddings

Antes de usar qualquer dado para treino, embedding, indexação vetorial ou análise semântica:

```text
1. Registrar origem
2. Verificar autorização/licença/finalidade
3. Classificar sensibilidade
4. Minimizar dados
5. Documentar transformação
6. Registrar hash ou fingerprint
7. Definir retenção
8. Permitir revisão ou exclusão quando aplicável
9. Separar uso exploratório de uso produtivo
```

Regra curta:

```text
representar não é autorizar;
vetorizar não é apagar origem;
treinar não é legitimar;
comprimir não é absolver governança.
```

---

## 7. Analogia operacional dos treinos

Um treino físico sem registro vira desgaste.

Um treino de modelo sem governança vira extração.

A diferença entre desenvolvimento e abuso está na cadeia:

```text
carga → resposta → recuperação → adaptação → revisão
```

No modelo:

```text
dado → representação → ajuste → avaliação → auditoria
```

Sem auditoria, só há aumento de carga.

Com auditoria, há evolução.

---

## 8. Invariante

A invariante desta matriz é:

> Cada coisa deve ser tratada segundo sua natureza antes de ser integrada ao sistema.

Em forma operacional:

```text
coisa observada
→ classe formal
→ origem
→ evidência
→ risco
→ relação
→ ação
→ auditoria
```

---

## 9. Fecho

RAFAELIA/RLL não deve crescer por acúmulo cego.

Deve crescer por relações governadas.

A pergunta para cada novo elemento é:

> Isto aumenta apenas o volume ou aumenta a qualidade das relações?

Se aumenta volume, entra como semente.

Se aumenta coerência, ganha relação.

Se ganha evidência, recebe peso.

Se suporta revisão, vira conhecimento governado.

---

## Retroalimentação

- **F_ok:** cria a régua formal para tratar símbolos, dados, embeddings, modelos, logs, código, socket, hardware e TOKEN_VAZIO.
- **F_gap:** falta transformar esta matriz em CSV/JSON validável por CI.
- **F_next:** criar `schemas/formal_treatment_record.schema.json` e fixtures de exemplo.
