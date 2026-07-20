# FASE 28 — Mapa de Rotas Vetoriais Ω e Florestas de Conhecimento

> **Estado:** arquitetura estrutural executável  
> **Claim boundary:** `claim_allowed=false`  
> **Escopo:** mapa de regiões, rotas, frequências operacionais, vetores Ω7, árvores de conhecimento e gates para evolução futura em aprendizado de máquina.

---

## 1. Revisão do trabalho já existente

Esta fase não começa do zero. Ela articula quatro estruturas já presentes no RLL:

1. `src/rll/latentes.py` já oferece tokenização semântica em sete direções, suavização temporal, projeção toroidal determinística, score de candidatos, controles negativos e proveniência por artefato;
2. `src/rll/structural_integration.py` já oferece estados epistêmicos, políticas de dados imutáveis e decisão de prontidão por artefatos disponíveis;
3. `data/results/bootstrap/dense_behavior_features.json` já materializa uma camada inicial de features densas, ainda limitada ao estágio de sementes;
4. `data/omega_operational/rll_omega7_operational.json` já fornece as sete dimensões operacionais e identifica D3 e D7 como regiões estruturalmente fracas.

A FASE 28 conecta essas bases sem confundir:

```text
mapa de rotas != descoberta científica
vetor operacional != embedding aprendido
frequência de fluxo != frequência física
floresta de conhecimento != random forest treinada
feature disponível != dado autorizado para treinamento
```

---

## 2. Objetivo

Construir um mapa que permita responder, para cada componente do RLL:

```text
em qual região Ω ele vive?
de onde ele veio?
para onde ele pode evoluir?
qual fluxo documentado percorreu sua rota?
qual vetor operacional representa sua condição atual?
qual lacuna impede o próximo movimento?
qual árvore de conhecimento o contém?
quais gates faltam antes de qualquer uso em ML?
```

O resultado é uma floresta dirigida, acíclica e auditável.

---

## 3. Três contratos estruturais

### 3.1 Blueprint declarativo

```text
data/knowledge_forest/rll_route_forest_blueprint.json
schemas/rll_route_forest_blueprint.schema.json
```

O blueprint declara:

- sete regiões Ω;
- nós e seus estados epistêmicos;
- rotas entre nós;
- quatro árvores de conhecimento;
- scores convencionais D1–D7;
- doze gates de prontidão de ML;
- referências de origem;
- `training_allowed=false`.

### 3.2 Ledger append-only de fluxo

```text
data/knowledge_forest/rll_route_flow_events.jsonl
schemas/rll_route_flow_event.schema.json
```

Cada linha registra um evento observável:

```text
artifact_declared
validation_pass
gap_opened
route_linked
```

O ledger inicial possui 21 eventos.

### 3.3 Floresta compilada

```text
schemas/rll_route_forest.schema.json
tools/build_rll_route_forest.py
```

O compilador recalcula a floresta e produz:

```text
artifacts/route-forest/route_forest_report.json
artifacts/route-forest/ROUTE_FOREST_REPORT.md
artifacts/route-forest/rll_route_forest.graphml
artifacts/route-forest/CHECKSUMS.sha256
```

---

## 4. Sete regiões da invariante operacional

| Região | Direção | Conteúdo |
|---|---|---|
| R1 | D1 | origem, proveniência, linhagem e custódia |
| R2 | D2 | coerência semântica, aliases e famílias de modelos |
| R3 | D3 | unidades, domínios, transformações e geometria vetorial |
| R4 | D4 | runtime, workflows, gates, recibos e rollback |
| R5 | D5 | memória temporal, precedência, invalidação e supersessão |
| R6 | D6 | licença, privacidade, autorização, autoria e segurança |
| R7 | D7 | observáveis, controles, incerteza, falsificadores e saídas |

Uma região não é uma área física. É uma classe operacional distinguível.

---

## 5. Frequência de fluxo

A frequência de uma rota é definida por:

\[
f_r(W)=\sum_{e\in E_r(W)}w_e
\]

onde:

- \(W\) é uma janela versionada;
- \(E_r(W)\) é o conjunto de eventos ligados à rota \(r\) nessa janela;
- \(w_e\) é um peso inteiro explícito do evento.

Na primeira janela:

```text
window_id = SNAPSHOT-20260720
window_kind = structural_snapshot
unit = events_per_snapshot
```

Portanto:

```text
frequency != Hertz
frequency != probability
frequency != popularity
frequency != user behavior
frequency != physical oscillation
```

Ela mede somente quantos eventos auditáveis atravessaram uma rota dentro do snapshot declarado.

---

## 6. Vetores operacionais

Cada nó carrega sete scores inteiros:

\[
s_i\in\{0,1,2,3,4\}
\]

com a convenção:

```text
0 = absent
1 = gap
2 = partial
3 = ready_for_test
4 = verified
```

O vetor normalizado é:

\[
\vec v_n=
\left(
\frac{s_1}{4},
\frac{s_2}{4},
\ldots,
\frac{s_7}{4}
\right)
\]

Ele descreve a posição operacional do nó nas sete direções.

Não representa:

- embedding neural;
- estado quântico;
- vetor físico de posição ou velocidade;
- evidência de verdade;
- probabilidade de sucesso.

### 6.1 Delta de uma rota

Para uma rota \(a\rightarrow b\):

\[
\Delta\vec v_{a\rightarrow b}=\vec v_b-\vec v_a
\]

O delta mostra quais dimensões ganham ou perdem maturidade operacional durante a travessia.

### 6.2 Centroide regional

Para uma região com \(N_R\) nós:

\[
\vec c_R=
\frac{1}{N_R}
\sum_{n\in R}\vec v_n
\]

O centroide resume a condição da região sem apagar os vetores individuais.

---

## 7. As quatro árvores

## 7.1 T-GOVERNANCE

**Raiz:** `N-GOV-ROOT`

Contém:

- contrato executável dos workflows;
- registro de schemas com claim boundary;
- avaliação Ω7.

Sua função é governar e auditar. Ela não é dataset de treinamento.

```text
ml_role = governance_only
ml_state = NOT_APPLICABLE
```

## 7.2 T-SCIENCE

**Raiz:** `N-SCI-ROOT`

Contém:

- camada de features densas;
- lacuna do registro dimensional;
- lacuna do pacote de falsificadores;
- lacuna do ledger temporal append-only.

Ela mostra que uma feature útil ainda depende de unidade, memória, baseline, incerteza e falsificador.

```text
ml_role = candidate_dataset
ml_state = NOT_READY
```

## 7.3 T-LATENTES

**Raiz:** `N-LAT-ROOT`

Contém:

- matriz semântica em sete direções;
- projeção toroidal determinística;
- score e controles negativos.

Ela pode produzir candidatos a features, mas ainda não constitui dataset autorizado ou modelo treinado.

```text
ml_role = feature_source
ml_state = FEATURE_ENGINEERING_ONLY
```

## 7.4 T-ML-EVOLUTION

**Raiz:** `N-ML-ROOT`

Contém:

- candidatos de feature engineering;
- lacuna de direitos e licenças;
- lacuna de holdout, leakage, baseline e model card.

É a árvore que impede o salto indevido de feature para treinamento.

```text
ml_role = training_candidate
ml_state = FEATURE_ENGINEERING_ONLY
training_allowed = false
```

---

## 8. Doze gates para aprendizado de máquina

Uma árvore somente pode chegar a `TRAINING_ELIGIBLE` quando todos os gates estiverem fechados:

1. proveniência completa;
2. direitos e licença;
3. dados brutos imutáveis;
4. definição explícita do alvo;
5. schema das features;
6. contrato de divisão treino/validação/teste;
7. teste de leakage;
8. modelo baseline;
9. análise de incerteza;
10. revisão de vieses;
11. model card;
12. revisão independente.

Mesmo após os doze gates, a execução ainda depende de autorização humana e política de uso aplicável.

---

## 9. Estados de prontidão

| Estado | Significado |
|---|---|
| `NOT_APPLICABLE` | árvore de governança, sem papel de treino |
| `NOT_READY` | estrutura ainda insuficiente para feature engineering confiável |
| `FEATURE_ENGINEERING_ONLY` | features podem ser estudadas, mas treino permanece bloqueado |
| `BASELINE_READY` | baseline controlado pode ser preparado |
| `HUMAN_AUTHORIZATION_REQUIRED` | gates técnicos quase completos, falta autorização explícita |
| `TRAINING_ELIGIBLE` | todos os gates estruturais passaram e treinamento foi autorizado |

Nenhum desses estados afirma qualidade preditiva.

---

## 10. Resultado inicial compilado

A primeira floresta coerente contém:

```text
regions        = 7
trees          = 4
nodes          = 17
routes         = 13
event_records  = 21
weighted_flow  = 21
cycles         = 0
orphans        = 0
max_depth      = 3
state          = STRUCTURAL_MAP_READY_ML_BLOCKED
claim_allowed  = false
```

A ausência de ciclos é importante porque cada árvore representa dependência e evolução dirigida. Retroalimentações futuras devem ocorrer entre snapshots ou ledgers temporais, não por ciclos silenciosos dentro da mesma árvore compilada.

---

## 11. Controles de consistência

O compilador rejeita:

- região ausente ou fora da ordem R1–R7;
- direção diferente de D1–D7;
- nó sem árvore;
- nó presente em mais de uma árvore;
- pai pertencente a outra árvore;
- rota com endpoint inexistente;
- rota sem evento;
- evento apontando para rota inexistente;
- ciclo;
- órfão não declarado como raiz;
- caminho absoluto ou com `..`;
- treinamento com gate aberto;
- árvore de governança autorizada para treino;
- promoção de `claim_allowed=true`.

---

## 12. Próximas rotas naturais

### D3 — Integridade dimensional

Materializar:

```text
data/contracts/rll_dimensional_invariants.json
```

Cada feature deve declarar unidade, domínio, transformação e compatibilidade.

### D5 — Memória temporal

Materializar:

```text
results/state_transition_ledger.jsonl
```

A floresta precisa evoluir por snapshots preservando os estados anteriores.

### D6 — Direitos

Materializar:

```text
data/contracts/dataset_rights_manifest.schema.json
```

Nenhuma feature pode entrar em treino sem licença, privacidade, autoria, finalidade e retenção explícitas.

### D7 — Falsificação e avaliação

Materializar:

```text
data/contracts/rll_falsifier_bundle.json
```

Depois, definir holdout, leakage, baseline, incerteza e model card.

---

## 13. Invariante preservada

A floresta pode crescer, mas cada crescimento deve preservar:

```text
identidade do nó
origem da informação
região operacional
relação explícita
janela temporal
frequência auditável
vetor reproduzível
claim boundary
direitos e autorização
memória do estado anterior
```

Em forma operacional:

\[
\mathcal F_{t+1}
=
\operatorname{Compile}
\left(
\mathcal B_t,
\mathcal E_t,
\mathcal G_t
\right)
\]

onde:

- \(\mathcal B_t\) é o blueprint;
- \(\mathcal E_t\) é o ledger de eventos;
- \(\mathcal G_t\) são os gates válidos;
- \(\mathcal F_{t+1}\) é uma nova floresta versionada.

A compilação deve ser determinística para a mesma entrada.

---

## Retroalimentação R3

```text
F_ok   = regiões, rotas, vetores, frequências e árvores tornaram-se executáveis
F_gap  = direitos, dimensionalidade, memória temporal e avaliação ML permanecem abertas
F_next = versionar snapshots, fechar D3/D5/D6/D7 e só então preparar baseline controlado
```

**A floresta de conhecimento não nasce quando se acumula informação. Ela nasce quando cada ramo conhece sua origem, seu limite, sua relação e a condição ética para continuar crescendo.**
