# RLL Effective Execution Queue V1

## Estado

```text
source_queue      = IMMUTABLE_HISTORY
successor_receipt = APPEND_ONLY_EVIDENCE
effective_queue   = DERIVED_PROJECTION
claim_allowed     = false
```

## Problema corrigido

A fila canônica de 6 de agosto de 2026 preserva corretamente o estado observado no instante de sua criação. Depois, o receipt pós-merge comprovou:

```text
7/7 workflows success
924 Python tests passed
3 subtests passed
0 failures
```

O receipt promoveu somente:

```text
RLL-P0-POSTMERGE-CI-RECEIPT
P / TOKEN_VAZIO_POSTMERGE_FULL_SUITE_RECEIPT
→
E / PASS_POSTMERGE_FULL_SUITE_RECEIPT
```

Reescrever o JSON histórico apagaria a genealogia. Ignorar o receipt deixaria a fila efetiva obsoleta. A solução é uma projeção derivada:

```text
fila imutável
+ receipts sucessores validados
→ itens resolvidos
+ dependências satisfeitas
+ bloqueios restantes
+ próximos gates executáveis
```

## Invariantes

1. O receipt precisa apontar para um item existente por `supersedes_queue_item`.
2. `promotion.from` deve coincidir exatamente com classe e estado originais.
3. `promotion.to` deve coincidir com classe e estado declarados no receipt.
4. Somente receipts de classe `E` ou `C` fecham um item.
5. Um estado contendo `TOKEN_VAZIO` não fecha o gate.
6. Dois receipts não podem resolver o mesmo item na mesma projeção.
7. `claim_allowed=false` permanece invariável.
8. Tornar um item `ready` não prova sua execução; apenas demonstra que as dependências formais foram satisfeitas.
9. Gates físicos continuam exigindo autoridade física. Container, CI ou texto não substituem receipt de aparelho.
10. Resultados negativos e estados anteriores permanecem visíveis.

## Uso

```bash
python tools/rll_execution_queue_effective.py \
  data/governance/RLL_EXECUTION_QUEUE_20260806_V1.json \
  --receipt results/governance/RLL_POSTMERGE_CI_RECEIPT_20260806_V1.json \
  --output results/governance/RLL_EXECUTION_QUEUE_EFFECTIVE_20260806_V1.json
```

O resultado esperado inicia a fila efetiva com:

```text
resolved:
  RLL-P0-POSTMERGE-CI-RECEIPT

next_ready[0]:
  RLL-P0-TERMUX-PHYSICAL-REPLAY
```

Outros itens P1 podem aparecer como prontos em paralelo quando dependem apenas do receipt pós-merge. A ordem de `next_ready` preserva prioridade `P0 → P1 → P2` e a ordem original dentro da mesma prioridade.

## Fronteira científica

Esta melhoria não executa:

- replay físico Termux;
- nova run Pantheon;
- Pantheon full covariance;
- nested sampling;
- revisão científica independente.

Ela impede dois erros opostos:

```text
receipt existente tratado como se não existisse
≠
receipt de software promovido como evidência científica
```

## Falsificadores

A projeção deve bloquear se:

- o receipt apontar para ID desconhecido;
- `claim_allowed=true` aparecer na fila ou no receipt;
- o estado anterior não coincidir;
- a promoção final divergir do receipt;
- a classe final não for `E` ou `C`;
- o estado final continuar `TOKEN_VAZIO`;
- houver receipts duplicados para o mesmo gate;
- o próximo gate declarado não existir.

## R₃

- **F_ok:** fila histórica e receipt coexistem sem sobrescrita; dependências podem ser liberadas por prova explícita.
- **F_gap:** replay físico e resultados científicos permanecem abertos.
- **F_next:** executar `RLL-P0-TERMUX-PHYSICAL-REPLAY` em aparelho real e anexar novo receipt, sem simulação.
