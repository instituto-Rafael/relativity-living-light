# RLL — Protocolo dos Sete Cercos + Observador–Observado em Três Janelas — V1

**Data:** 2026-09-17  
**Estado:** `HYPOTHESIS_PROTOCOL`  
**Autoridade de implementação:** `instituto-Rafael/relativity-living-light`  
**claim_allowed:** `false`  
**Regra:** `SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM`  
**Regra:** `TOKEN_VAZIO != 0`

---

## 1. Intenção

Este protocolo operacionaliza duas sementes de trabalho sem promovê-las a fato físico:

1. todo resultado RLL deve atravessar sete cercos — **proveniência, contexto, evidência, contradição, incerteza, reprodução e rollback**;
2. fenômenos dinâmicos podem ser inspecionados por três janelas predeclaradas — **entrada, meio e saída/fim** — comparando estatísticas robustas entre as janelas sem escolher retrospectivamente a janela “melhor”.

A imagem `yin-yang / twins / observador–observado` é preservada como **metáfora de simetria, contraponto e dupla leitura**. Ela não constitui evidência de mecanismo quântico.

---

## 2. Proveniência e fronteira de fonte

### 2.1 Fonte autoral

A formulação foi declarada pelo autor em sessão de 2026-09-17 e autorizada para gravação no RLL.

### 2.2 Rotas canônicas consultadas

- RAFAELIA `START HERE` — router de cadeia de custódia; conteúdo privado não é copiado para este repositório.
- RAFAELIA livro-memória central — ponte longitudinal; conteúdo privado não é copiado.
- `data/governance/RLL_EVIDENCE_EVOLUTION_MATRIX_V1.json` — já contém os sete cercos como `guards`.
- `knowledge_ecosystem/session_operating_system.yml` — já exige incerteza, contradição, falsificação e rollback sem promover analogia a fato físico.

### 2.3 Estado de origem

`DECLARED_BY_AUTHOR -> FORMALIZED_AS_HYPOTHESIS_PROTOCOL`

Nenhuma frase privada da sessão é necessária para reproduzir o contrato público.

---

## 3. Os sete cercos

Cada observação, execução ou comparação deve preencher os sete blocos abaixo. Lacuna não preenchida vira `TOKEN_VAZIO`, nunca inferência automática.

| Cerco | Pergunta mínima | Evidência mínima |
|---|---|---|
| **proveniência** | De onde veio o dado/artefato? | fonte, versão/commit, hash quando aplicável, timestamp ou janela temporal |
| **contexto** | Em que escala, instrumento, unidade e domínio a leitura vale? | escopo, unidades, sistema, condições e fronteiras |
| **evidência** | O que foi realmente observado ou executado? | receipt, teste, log, tabela, série ou artefato verificável |
| **contradição** | O que conflita com a leitura atual? | referência do conflito + estado `OPEN/RESOLVED/SUPERSEDED` |
| **incerteza** | O que não é conhecido ou é sensível ao método? | erro, dispersão, covariância ou `TOKEN_VAZIO` explícito |
| **reprodução** | Outra execução pode reconstruir o resultado? | dados fixados, configuração, seed quando houver e procedimento |
| **rollback** | Como desfazer a mudança sem apagar história/evidência? | âncora anterior + procedimento aditivo/reversível |

### Invariantes

```text
NEGATIVE_EVIDENCE != GLOBAL_FALSIFICATION
REPRODUCTION != UNIVERSAL_TRUTH
ROLLBACK_PRESERVES_CONTRADICTORY_EVIDENCE
TOKEN_VAZIO != ZERO
```

---

## 4. Observador e observado

Para impedir mistura entre metáfora e mecanismo, representamos a medição como:

\[
y = M(x;\theta_M,c) + \varepsilon
\]

onde:

- `x` = estado/variável do sistema sob estudo;
- `M` = processo de medição/instrumentação;
- `theta_M` = parâmetros/calibração do instrumento;
- `c` = contexto experimental/observacional;
- `epsilon` = ruído/erro/resíduo observado.

Neste protocolo, **observador** significa sistema de medição + protocolo + seleção declarada de dados. Não significa que uma consciência humana seja necessária para produzir um resultado físico.

A metáfora `observador ↔ observado` é útil para perguntar se o instrumento, o corte temporal ou a seleção alteram a leitura. A resposta deve vir de controles e dados, não da metáfora.

---

## 5. Correções de fronteira quântica

### 5.1 Elétron

O protocolo **não** presume que um elétron execute uma órbita clássica mensurável como um planeta em torno de um núcleo. Quando aplicado a domínio quântico, as três janelas descrevem **registros de preparação/interação/detecção ou séries de observáveis**, não uma trajetória clássica inventada.

### 5.2 Gato de Schrödinger

O experimento mental de Schrödinger não autoriza o claim “o gato está literalmente vivo até uma pessoa olhar”. Neste documento, ele serve somente como lembrete de que **estado modelado, interação de medida, registro e inferência devem ser separados**.

### 5.3 Aceleradores

Em aceleradores/colisores, `entrada–meio–saída` só é válido depois que os três locators forem operacionalmente definidos — por exemplo, por subsistema detector, timestamp, posição reconstruída ou fase do pipeline. Não se presume uma “melhor de três” física sem critério anterior aos dados.

---

## 6. Três janelas predeclaradas

Defina antes da execução:

```text
W0 = entrada / pré-evento / preparação
W1 = meio / interação / transição
W2 = saída-fim / pós-evento / detecção
```

Cada janela precisa de:

- locator temporal, espacial ou lógico;
- largura da janela;
- variável observada;
- unidade;
- regra de inclusão/exclusão;
- instrumento/fonte;
- motivo da escolha.

Se qualquer locator não estiver definido, o estado é `TOKEN_VAZIO_WINDOW_LOCATOR` e nenhum claim comparativo é promovido.

---

## 7. Min–mediana–max e dispersão

Para `N` eventos/repetições e variável `q`, em cada janela `W_j`:

\[
S_j(q) = [\min(q_j),\;\operatorname{median}(q_j),\;\max(q_j)]
\]

Como `min` e `max` são sensíveis a outliers, o protocolo recomenda também:

\[
R_j(q) = [Q_1(q_j),\;Q_3(q_j),\;MAD(q_j)]
\]

Comparações básicas:

\[
\Delta_{01}=\operatorname{median}(q_1)-\operatorname{median}(q_0)
\]

\[
\Delta_{12}=\operatorname{median}(q_2)-\operatorname{median}(q_1)
\]

\[
\Delta_{02}=\operatorname{median}(q_2)-\operatorname{median}(q_0)
\]

Esses deltas medem mudança observada entre janelas; **não identificam por si só mecanismo causal**.

---

## 8. Regra contra “melhor de três” pós-hoc

Se existir escolha de uma janela “melhor”, a função de seleção deve ser registrada **antes** da leitura dos resultados:

\[
W^* = \arg\min_{W_j} L(W_j;\mathcal{C}_{pre})
\]

ou equivalente predefinido, onde `C_pre` contém os critérios declarados antes da execução.

Selecionar `W*` depois de observar qual janela favorece uma hipótese gera `POST_HOC_SELECTION_RISK` e mantém `claim_allowed=false`.

---

## 9. Twins / yin-yang / equidistância

A formulação autoral sugere uma leitura dual/pareada. A versão operacional mínima é:

- `V+` = leitura direta;
- `V-` = leitura de controle/contraponto;
- ambos devem usar a mesma unidade e um mapa de comparação declarado;
- “equidistância” só pode ser afirmada depois de definir a métrica `d(V+,V-)`.

Exemplo abstrato:

\[
D = d(V_+,V_-)
\]

Sem definição de `d`, “equidistante” permanece `TOKEN_VAZIO_EQUIDISTANCE_METRIC`.

As expressões autorais **“Twins on a ‡”** e **“4 de 5 em três”** permanecem preservadas como sementes ainda não operacionalizadas:

```text
TOKEN_VAZIO_TWINS_ON_DAGGER
TOKEN_VAZIO_4_OF_5_IN_THREE
```

Nenhum significado adicional é inventado.

---

## 10. Contradições que o protocolo deve capturar

1. janela escolhida depois de ver o resultado;
2. mudança de unidade ou instrumento entre janelas sem normalização;
3. fonte temporalmente desalinhada;
4. variável derivada tratada como observação direta;
5. erro/covariância ausente tratado como zero;
6. trajetória clássica atribuída a observável quântico sem modelo válido;
7. metáfora de observação promovida a mecanismo físico;
8. reprodução que muda dataset/configuração sem registrar delta;
9. rollback que apaga evidência negativa.

Qualquer item acima deve produzir `CONTRADICTION` ou `CLAIM_BLOCKED` até resolução documentada.

---

## 11. Falsificadores do próprio protocolo

O protocolo é rejeitado ou revisado se:

- as três janelas não puderem ser definidas sem arbitrariedade material;
- resultados mudarem de forma dominante com pequenas mudanças de locator sem explicação;
- a repetição não reproduzir ao menos o estado/ordem de grandeza declarada dentro das incertezas;
- a função de medição dominar o sinal e isso não puder ser modelado ou controlado;
- o protocolo aumentar cherry-picking em vez de reduzi-lo.

---

## 12. Aplicação transdisciplinar permitida

A estrutura `W0/W1/W2 + sete cercos` pode ser usada como **protocolo de observação**, desde que o domínio declare seus próprios locators e unidades:

- séries temporais ambientais/METAR/Climate Engine;
- simulações e campos de fluidos;
- eventos instrumentais;
- séries de partículas/detectores;
- séries cosmológicas/computacionais;
- pipelines de software e validação.

O mesmo formato entre domínios **não implica mecanismo físico comum**.

---

## 13. Contrato mínimo de execução

```text
DEFINE   -> declarar hipótese, variável, W0/W1/W2 e critérios antes do resultado
MEASURE  -> fixar fonte, unidades, hashes/versões e baseline
ANALYZE  -> min/mediana/max + dispersão + resíduos + contradições
IMPROVE  -> menor alteração reversível capaz de reduzir a incerteza
CONTROL  -> reprodução independente/segunda execução + receipt + rollback
CLAIM    -> somente se o gate específico permitir
```

Saída obrigatória por rodada:

```text
provenance
context
evidence
contradiction
uncertainty
reproduction
rollback
R3
claim_allowed
```

---

## 14. R3

```text
F_ok   = sete cercos já existem no RLL e agora ganham protocolo explícito de observação W0/W1/W2.
F_gap  = locators físicos concretos, métrica de equidistância e semântica de “Twins on a ‡ / 4 de 5 em três” permanecem TOKEN_VAZIO.
F_next = testar o contrato primeiro em um dataset/artefato já versionado, preservando baseline e sem promover claim físico.
```

---

## 15. Fronteira final

**Este documento formaliza um método de observação e auditoria. Não demonstra colapso quântico por consciência, não demonstra trajetórias clássicas de elétrons, não estabelece um mecanismo comum entre aceleradores, átomos, clima e cosmologia e não confirma a hipótese RLL.**
