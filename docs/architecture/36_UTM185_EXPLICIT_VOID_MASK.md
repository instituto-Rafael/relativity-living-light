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
d_{\mathbb B}(0,q)=2\,\operatorname{artanh}(\|q\|),
\qquad \|q\|<1.
\]

Logo, `embedding = 0` **não** pode significar automaticamente “ausente” e sua
distância aos demais pontos não é infinita. Ausência e geometria precisam ser
dois canais diferentes:

```text
coordinates[i]  = ponto válido na bola
valid_mask[i]   = true | false
```

## Contrato implementado

A implementação usa logits

\[
\ell_i=-d_{\mathbb B}(q,k_i)/\tau
\]

somente onde `valid_mask[i]=true`. Posições inválidas recebem peso exatamente
zero. Se todas as posições forem inválidas:

```text
state=TOKEN_VAZIO_ALL_MASKED
weights=0
context=0
```

Isso é uma falha fechada, não uma inferência inventada.

## O que foi provado localmente

- a origem possui distância finita;
- a identidade radial `d(0,q)=2 atanh(||q||)` é satisfeita;
- coordenada zero e ausência são estados distintos;
- itens mascarados não alteram o contexto;
- pesos válidos somam um;
- pontos na borda ou fora da bola são rejeitados;
- shape inconsistente é rejeitado.

## O que não foi provado

- superioridade sobre máscara booleana convencional;
- benefício em perplexidade, acurácia ou memória;
- integração com um tokenizer real;
- execução no dispositivo Termux;
- estabilidade em treino;
- vantagem científica do modelo RLL.

## Próximo gate

Comparar, sob o mesmo dataset e seed:

1. atenção euclidiana com máscara booleana;
2. atenção hiperbólica com a mesma máscara;
3. embedding nulo sem máscara, como controle negativo.

Métricas mínimas:

```text
loss
perplexity ou métrica da tarefa
latência
memória
NaN/Inf
peso total atribuído a posições ausentes
```

A hipótese só avança se a geometria hiperbólica produzir diferença reproduzível
além do custo adicional e sem confundir ausência com o ponto de origem.
