# UTM-185 — Máscara explícita de vazio na atenção hiperbólica

## Estado

```text
module_id=UTM-185
source_label=Tokenizer com máscara de vazio
implementation_state=PARTIAL_LOCAL_SOFTWARE_PROOF
device_receipt=TOKEN_VAZIO_TERMUX_PENDING
model_training_result=TOKEN_VAZIO_NOT_RUN
claim_allowed=false
```

## Correção geométrica

O ponto `0` é válido na bola de Poincaré. Para curvatura unitária,

\[
d_{\mathbb B}(0,q)=2\,\operatorname{artanh}(\|q\|),\qquad \|q\|<1.
\]

Logo, `embedding = 0` não pode significar automaticamente “ausente”. Ausência e geometria são canais distintos:

```text
coordinates[i] = ponto válido na bola
valid_mask[i]  = true | false
```

## Contrato implementado

A implementação usa logits `-d(q,k_i)/tau` somente onde `valid_mask[i]=true`. Posições inválidas recebem peso exatamente zero. Se todas forem inválidas:

```text
state=TOKEN_VAZIO_ALL_MASKED
weights=0
context=0
```

Isso é falha fechada, não inferência inventada.

## Evidência preservada

- origem com distância finita;
- coordenada zero distinta de ausência;
- itens mascarados não alteram o contexto;
- pesos válidos somam um;
- borda `||x|| >= 1` é rejeitada;
- shape inconsistente é rejeitado.

## TOKEN_VAZIO preservados

- execução Termux/dispositivo físico;
- integração com tokenizer/modelo real;
- estabilidade de treino;
- melhoria de perplexidade/qualidade;
- superioridade sobre máscara booleana convencional.

## F_next

Comparar, com mesmo dataset e seeds: atenção euclidiana + máscara; atenção hiperbólica + mesma máscara; embedding nulo sem máscara como controle negativo. Medir loss, métrica da tarefa, latência, memória, NaN/Inf e peso atribuído a ausentes.
