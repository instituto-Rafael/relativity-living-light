# RLL — NIBIGUIRI-12 — Auditoria Isogônica e Antagônica da Metodologia — 2026-09-05

**State:** `RED_TEAM_METHOD / APPEND_ONLY / claim_allowed=false`  
**Purpose:** detectar o que ficou óbvio, ignorado, subponderado, simplificado ou invisível porque a metodologia anterior olhava o material a partir de seus próprios critérios.

## 0. Construção operacional

`NIBIGUIRI-12` não é um teorema geométrico. É uma roda de auditoria metodológica com 12 direções igualmente espaçadas em `30°`, formando seis pares opostos:

```text
N01 000° <-> N07 180°
N02 030° <-> N08 210°
N03 060° <-> N09 240°
N04 090° <-> N10 270°
N05 120° <-> N11 300°
N06 150° <-> N12 330°
```

Cada hipótese/tese deve ser examinada pelo raio e pelo seu antagonista. Passar apenas pelo método principal não basta.

## N01 — 000° — ESCALA PRESERVADA

**Pergunta antagônica:** o que a simplificação algébrica apagou geometricamente?

**O óbvio que passou batido:** `77/33=7/3` como racional, mas `(77,33)=11(7,3)` como vetor de escala. O primeiro fechamento privilegiou a razão e perdeu comprimento, área e volume potenciais.

**Gate:** conservar `unreduced_state`, `primitive_state`, `scale_gcd`, norma, dimensão de medida e orientação quando escala integra o objeto.

**Oposto:** N07.

## N02 — 030° — ORIENTAÇÃO / TRANSFORMAÇÕES

**Pergunta antagônica:** duas configurações numericamente iguais continuam iguais após sinal, rotação, reflexão, translação ou mudança de base?

**O que foi subponderado:** orientação, quiralidade, sinal, escolha de origem e grupo de transformações admissível. Uma razão, distância ou área isolada não fixa a geometria completa.

**Gate:** declarar o grupo de equivalência antes de identificar objetos; registrar invariantes coordenada-livres e dados que mudam sob transformação.

**Oposto:** N08.

## N03 — 060° — LOCAL → GLOBAL

**Pergunta antagônica:** uma identidade encontrada numa face ou aresta continua válida no objeto inteiro?

**O que foi ignorado inicialmente:** a varredura completa dos 42 vértices, 861 pares, 14 classes de produto escalar, 120 arestas, graus, dualidade e espectro. A análise começou local e só depois enxergou a topologia global.

**Gate:** toda afirmação local candidata a global deve ser testada contra o conjunto completo de incidências/órbitas.

**Oposto:** N09.

## N04 — 090° — FINITO → ASSINTÓTICO

**Pergunta antagônica:** um resultado em `f=2`, módulo 7 ou `n<=14000` é um teorema da família ou apenas um caso finito?

**O que ficou para trás:** taxas de convergência, generalização em `f`, dependência da fatoração de `m`, limites e termos de erro.

**Gate:** anexar a cada resultado finito uma pergunta explícita de extensão, limite, taxa e domínio de validade.

**Oposto:** N10.

## N05 — 120° — DIRETO → INVERSO / FIBRAS

**Pergunta antagônica:** dado o resultado, quantos estados de origem podem tê-lo produzido?

**O que foi menosprezado:** preimagens, many-to-one, branches, perda de multiplicidade, compatibilidade CRT, inversa da dobra e condições de reconstrução. A construção forward dominou a leitura.

**Gate:** para cada `F:X->Y`, registrar `F^{-1}(y)` como conjunto quando a inversa não é função.

**Oposto:** N11.

## N06 — 150° — INTERNO → EXTERNO

**Pergunta antagônica:** a coerência interna sobrevive a prior art, null model, baseline e reprodutor independente?

**O que foi desprezado pela dinâmica interna da sessão:** risco de redescoberta de matemática conhecida, hipótese trivial sob mudança de variável, baseline mais simples ou contraexemplo já conhecido.

**Gate:** `novelty=TOKEN_VAZIO_PRIOR_ART` até busca dedicada; incluir null/baseline e teste independente.

**Oposto:** N12.

## N07 — 180° — COMPRESSÃO / ESTATÍSTICA SUFICIENTE

**Antagoniza N01.** Preservar escala não significa preservar todo dado indefinidamente.

**Pergunta:** qual é a representação mínima lossless que permite reconstruir a geometria relevante?

**O óbvio inverso que faltava:** depois de corrigir a simplificação excessiva, existe o risco oposto de guardar tudo e nunca descobrir o que é informação suficiente. `primitive_vector + scale + transform metadata` pode reconstruir o vetor original; isso deve ser provado caso a caso.

**Gate:** toda compressão precisa de prova de reconstruibilidade para o domínio declarado; toda remoção sem sidecar é `LOSSY`.

**Oposto:** N01.

## N08 — 210° — QUOCIENTE / ARTEFATO DE COORDENADA

**Antagoniza N02.** Nem toda mudança de coordenada produz objeto novo.

**Pergunta:** o que é intrínseco e o que é apenas representação?

**O que ficou oculto:** necessidade de quotient spaces, canonical forms e órbitas de simetria para não contar rotações/reflexões equivalentes como novas hipóteses ou novas classes.

**Gate:** separar `state`, `coordinate_representation` e `equivalence_class`.

**Oposto:** N02.

## N09 — 240° — GLOBAL → LOCAL / RESÍDUO

**Antagoniza N03.** Um padrão global pode esconder singularidades e minorias estruturais.

**Pergunta:** onde exatamente o resumo global falha?

**O que foi menosprezado:** residual por vértice, face, aresta, classe, módulo, região de simetria; média e espectro podem esconder um pequeno conjunto excepcional.

**Gate:** todo agregado global deve disponibilizar distribuição, extremos e identificadores dos outliers.

**Oposto:** N03.

## N10 — 270° — ASSINTÓTICO → FINITO / EXCEÇÕES

**Antagoniza N04.** Um limite verdadeiro pode ser falso ou inútil nos primeiros níveis.

**Pergunta:** qual é o menor `f/m/n` a partir do qual a aproximação funciona, e quais exceções pequenas existem?

**O que ainda estava fora:** threshold explícito, erro finito e catálogo de exceções para `f=1,2,...`, não somente `O(f^-2)` ou limites formais.

**Gate:** hipótese assintótica não promove o caso finito; produzir tabela de erro e menor regime válido.

**Oposto:** N04.

## N11 — 300° — INVERSO → MECANISMO

**Antagoniza N05.** Invertibilidade algébrica não implica causalidade nem reversibilidade física.

**Pergunta:** reconstruir uma entrada significa que ela causou a saída pelo mecanismo proposto?

**O que foi ignorado em formulações anteriores:** `F^{-1}` pode ser apenas reconstrução matemática; não é seta causal, tempo reverso, dinâmica física ou prova de mecanismo.

**Gate:** separar `inverse_relation`, `generative_dynamics`, `causal_model` e `physical_mechanism`.

**Oposto:** N05.

## N12 — 330° — EVIDÊNCIA → ANTI-EVIDÊNCIA

**Antagoniza N06 e red-team da própria governança.**

**Pergunta:** uma cadeia impecável de hashes, CI e receipts pode estar autenticando uma afirmação falsa?

**O óbvio mais perigoso:** sim. Custódia prova identidade/execução do artefato, não verdade matemática ou física. A própria metodologia evidence-first pode gerar excesso de confiança se o upstream lógico estiver errado.

**Gate:** cada claim deve apontar separadamente para `assumptions`, `proof/data`, `execution`, `custody`, `falsifier`; nenhum downstream preenche upstream ausente.

**Oposto:** N06.

## 1. Doze omissões/nibiguiri concretas extraídas desta rodada

1. escala geométrica foi inicialmente achatada pela redução racional;
2. orientação/grupo de equivalência não estava explícito;
3. relações locais foram avaliadas antes da varredura global;
4. `f=2` estava muito à frente da teoria geral em `f`;
5. mapas forward estavam mais desenvolvidos que fibras/inversas;
6. prior art/null models estavam atrás da produção interna de hipóteses;
7. após preservar tudo, faltava a pergunta dual de representação mínima lossless;
8. faltava separar objeto intrínseco de artefato de coordenada;
9. agregados globais não tinham sempre residual/outlier explícito;
10. conjecturas assintóticas não traziam threshold finito nem catálogo de exceções;
11. inversa matemática corria risco de ser lida como mecanismo/causalidade;
12. evidence/hash/receipt precisavam ser adversariados para não virar substitutos psicológicos de prova.

## 2. Regra de promoção NIBIGUIRI

Uma unidade `Txx/Hxx` só pode sair de `OPEN/RESEARCH_PROGRAM` quando registrar 12 estados:

```text
PASS
FAIL
TOKEN_VAZIO
NOT_APPLICABLE_WITH_REASON
```

Nenhum raio pode desaparecer. `NOT_APPLICABLE` exige motivo. `TOKEN_VAZIO` não é zero e bloqueia promoção quando o raio é material ao claim.

## 3. Theory Hashing NIBIGUIRI

Ordered Merkle root das 12 lentes, usando SHA-256 sobre payload canônico desta versão:

`40891b54e35cd5e0e200f2875791253df564bec2a43c519c23d5a38d35877e08`

Root conjunto das 48 unidades de pesquisa + 12 lentes NIBIGUIRI:

`c46ae3d17b251584e901275cbd780f8179ab5bceb1858076793649bc88498c94`

Hash é custódia, não validação.

## R3

```text
F_ok   = 12 direções isogônicas e seis pares antagônicos materializados
F_gap  = cada T/H ainda precisa receber seu vetor N01..N12 de resultados
F_next = executar matriz 48 x 12 = 576 células de auditoria, preservando FAIL/TOKEN_VAZIO
```
