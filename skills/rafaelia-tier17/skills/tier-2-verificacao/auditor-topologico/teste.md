# Teste — auditor-topologico

## T1 — positivo estrutural
- Dado um input com evidência explícita e uma lacuna explícita,
- quando `auditor-topologico` processa o caso,
- então a saída deve preservar ambas e produzir `F_next` verificável.

## T2 — negativo / anti-alucinação
- Dado um claim sem receipt/evidência suficiente,
- então `claim_allowed` deve permanecer `false` e a lacuna deve ser `TOKEN_VAZIO`.

## Estado neste pacote
`MATERIALIZED_NOT_EXECUTED` — estes testes são especificações; execução automatizada é F_next.
