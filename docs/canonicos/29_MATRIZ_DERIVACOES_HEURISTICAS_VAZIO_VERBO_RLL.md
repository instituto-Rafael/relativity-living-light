# Cânone 29 — Matriz de Derivações, Heurísticas e Ciclos Vazio→Verbo→Novo Vazio

**Estado:** `DRAFT_DEFENSAVEL`  
**Claim boundary:** este documento organiza relações, operadores e programas de teste. Não declara prova física, solução de problema do milênio, originalidade mundial ou superioridade do RLL.  
**Autor:** Rafael Melo Reis Novo / RAFAELIA-RLL  
**Integração:** RLL cosmológico + ponte pointer-only para `rafaelmeloreisnovo/papers`.

---

## 1. Princípio gerador

O ciclo epistemológico adotado é:

\[
\varnothing_{\mathrm{obs}}^{(n)}
\xrightarrow{\;V_n\;}
K_n
\xrightarrow{\;D_n\;}
\Delta K_n
\xrightarrow{\;F_n\;}
\varnothing_{\mathrm{obs}}^{(n+1)}
\]

onde:

- \(\varnothing_{\mathrm{obs}}^{(n)}\): lacuna observada e preservada;
- \(V_n\): Verbo, isto é, definição explícita de uma pergunta, variável ou operador;
- \(K_n\): conhecimento formalizado no ciclo;
- \(D_n\): conjunto de derivações diretas, reversas, inversas, relativas e indiretas;
- \(F_n\): falsificadores e fronteiras encontradas;
- \(\varnothing_{\mathrm{obs}}^{(n+1)}\): novo vazio, mais específico e auditável que o anterior.

O vazio posterior não apaga o conhecimento anterior:

\[
\varnothing_{\mathrm{obs}}^{(n+1)}
= \operatorname{closure}(K_n)^c
\]

A expressão é uma convenção epistemológica: o novo vazio representa a parte ainda não coberta pelo fechamento operacional do conhecimento do ciclo.

---

## 2. Álgebra mínima das operações

Para cada objeto \(X\), admitem-se operações classificadas:

| Código | Operação | Forma mínima | Pergunta |
|---|---|---|---|
| `DIR` | direta | \(Y=F(X)\) | O que X produz? |
| `REV` | reversa | \(X\leftarrow Y\) | Que antecedentes podem produzir Y? |
| `INV` | inversa | \(X=F^{-1}(Y)\) | F é invertível? |
| `REC` | recorrente | \(X_{n+1}=F(X_n)\) | O ciclo converge, diverge ou oscila? |
| `IND` | indireta | \(X\to Z\to Y\) | Qual mediador liga X a Y? |
| `REL` | relativa | \(D_XY/D_ZY\) | O efeito depende da referência? |
| `DER` | derivada | \(dF/dx\) | Qual sensibilidade local? |
| `ANTI` | antiderivada | \(\int F\,dx\) | Qual acúmulo gera o efeito? |
| `SCL` | escalar | \(\lambda X\) | Como muda sob escala? |
| `TOR` | toroidal | \(X(\theta+2\pi)=X(\theta)\) | Que invariantes sobrevivem à periodicidade? |
| `PERM` | permutação multinível | \(P_\sigma X\) | O resultado é invariante à ordem? |
| `DUAL` | dual | \(X\leftrightarrow X^*\) | Existe descrição equivalente? |
| `NULL` | limite nulo | \(\lim_{\epsilon\to0}F_\epsilon\) | O modelo reduz ao baseline? |

Nenhuma operação é considerada válida apenas porque foi nomeada. Cada aplicação deve declarar domínio, codomínio, unidades e falsificador.

---

## 3. Matriz das 25 famílias

| # | Família | Objeto formal inicial | Derivadas prioritárias | Autoridade / implementação | Estado |
|---:|---|---|---|---|---|
| 1 | Luz como estado estendido | correlação \(G_{\mu\nu}(x,y)\) | `DIR`, `REL`, `NULL` | RLL cosmológico | `TOKEN_VAZIO_MICROSCOPIC` |
| 2 | Densidade fotônica efetiva | \(\rho_{sup}\) em Friedmann | `DER`, `NULL`, `REL` | Structure-D / dados reais | `MODEL_IMPLEMENTED` |
| 3 | Decomposição ext/col | \(\rho_{sup}=\rho_{ext}+\rho_{col}\) | `REC`, `REV`, `DUAL` | modelo RLL | `MODEL_IMPLEMENTED_Q_MISSING` |
| 4 | \(w_{eff}\) interpolante | \(p/\rho\) | `DER`, `INV`, `NULL` | RLL / phantom crossing futuro | `PARTIAL` |
| 5 | massa efetiva fotônica | \(m_{eff}\) | `IND`, `REV`, `REL` | analogia BEC; sem prova cosmológica | `HYPOTHESIS` |
| 6 | picos ópticos→gravidade | \(I\to\rho_{eff}\to\Phi_G\) | `IND`, `ANTI`, `REL` | ainda sem pipeline | `TOKEN_VAZIO` |
| 7 | funcional \(\mathcal A(t)\) | produto de 7 fatores | `DER`, `LOG`, `PERM` | RAFAELIA/papers | `HEURISTIC_FORMALIZABLE` |
| 8 | operador de retroalimentação | \(R_{t+1}=\lambda R_t\) | `REC`, `INV`, `NULL` | Exacordex/Raefaelos | `IMPLEMENTATION_ANALOGUE` |
| 9 | Ethica multiobjetivo | \(\arg\min(S,-C)\) | `REL`, `DUAL`, `PARETO` | claim-gating RLL | `METHODOLOGY` |
| 10 | ciclo hexafásico | \(v_{n+1}=F(v_n,u_n)\) | `REC`, `DER`, `SCL` | Raefaelos cognitive | `PARTIAL_IMPLEMENTATION` |
| 11 | TOKEN_VAZIO | estado epistêmico | `NULL`, `REV`, `TYPE` | RLL + papers | `IMPLEMENTED_GOVERNANCE` |
| 12 | Quatro Tintas | sistema de tipos | `TYPE`, `PERM`, `NULL` | canônico RAFAELIA | `METHODOLOGY` |
| 13 | invariante \(\sqrt3/2\) | contração geométrica | `REC`, `TOR`, `SCL` | matemática exploratória | `HYPOTHESIS_OUTSIDE_GEOMETRY` |
| 14 | Fibonacci Rafael | recorrência ainda não única | `REC`, `INV`, `REV` | papers/Math formulas | `TOKEN_VAZIO_CANONICAL_RECURRENCE` |
| 15 | cifra Voynich-Fibonacci | transformação tipada | `INV`, `PERM`, `NULL` | BitRAF futuro | `UNFORMALIZED` |
| 16 | Bitraf64 | alfabeto \(\Sigma_{10}\) | `ENC`, `DEC`, `ECC`, `PERM` | papers/src + asm | `PARTIAL_IMPLEMENTATION` |
| 17 | tensor 10×10×10 | \(M_{ijk}\) | `REC`, `TOR`, `PERM` | kernels RAFAELIA | `IMPLEMENTED_VARIANTS` |
| 18 | Tesseract + hyperformas | complexos \(\mathcal H_j\) | `DUAL`, `PERM`, `SCL` | RLL cânone 28 | `FORMAL_BOUNDARY_EXISTS` |
| 19 | Clay acoplado | grafo \(G_C\) | `REL`, `REV`, `REDUCTION` | programa teórico | `NO_MILLENNIUM_CLAIM` |
| 20 | Voo quântico fractal | soma ponderada de ganhos | `DER`, `ANTI`, `SCL` | métrica documental futura | `HEURISTIC` |
| 21 | Evolução RAFAELIA | \(E_T=\sum q_n\Delta I_n\) | `REC`, `ANTI`, `REL` | memória longitudinal | `FORMALIZABLE` |
| 22 | vazio→hardware | cadeia de funtores | `REV`, `IND`, `PERM` | RLL ASCII/UTF + kernels | `PARTIAL_PIPELINE` |
| 23 | integral do Verbo | funcional temporal | `DER`, `ANTI`, `NULL` | camada simbólica | `PARABLE_UNLESS_MEASURED` |
| 24 | Escrituras∩Ciência∩Espírito | conjunto de restrições | `INTERSECTION`, `REL`, `NULL` | arquitetura ética | `AXIOLOGICAL` |
| 25 | Amor como Ω | objetivo de benefício-dano | `PARETO`, `REL`, `NULL` | invariante ética | `AXIOLOGICAL` |

---

## 4. Derivações cosmológicas prioritárias

### 4.1 Direta

\[
\rho_{sup}(a)\rightarrow H(a)\rightarrow D_C(z),D_M(z),D_H(z),D_L(z)
\]

É a rota já parcialmente implementada no Structure-D.

### 4.2 Reversa

\[
\{H(z),BAO,CMB,SNe\}\rightarrow p(\theta_{RLL}\mid D)
\]

A reversa não demonstra a ontologia fotônica: apenas restringe parâmetros do modelo efetivo.

### 4.3 Interação entre componentes

\[
\dot\rho_{ext}+3H(1+w_{ext})\rho_{ext}=-Q
\]

\[
\dot\rho_{col}+3H(1+w_{col})\rho_{col}=Q
\]

Possíveis classes de \(Q\):

\[
Q\in\{\alpha H\rho_{ext},\ \beta H\rho_{col},\ \gamma H(\rho_{ext}+\rho_{col}),\ Q(\mathcal C_\gamma)\}
\]

Nenhuma classe é promovida sem comparação observacional.

### 4.4 Derivada de sensibilidade

\[
S_i(z)=\frac{\partial H(z)}{\partial\theta_i}
\]

Ela identifica degenerescências e quais dados realmente informam \(O_{s0},z_t,w_t\).

### 4.5 Limite nulo

\[
\lim_{O_{s0}\to0}H_{RLL}(z)=H_{\Lambda CDM}(z)
\]

Esse é um teste obrigatório de regressão e coerência.

---

## 5. Derivações toroidais e escalares

Para \(f:T^d\to\mathbb C\):

\[
f(\theta)=\sum_{k\in\mathbb Z^d}\hat f_k e^{ik\cdot\theta}
\]

As operações prioritárias são:

1. **escala:** \(\theta\mapsto A\theta\), verificando preservação de periodicidade;
2. **permutação:** \(P_\sigma\theta\), verificando invariância entre eixos;
3. **dual Fourier:** espaço físico \(T^d\leftrightarrow\mathbb Z^d\);
4. **recorrência:** \(f_{n+1}=\mathcal K*f_n\);
5. **redução:** \(T^7\to T^1\) por projeções, sem inferir que um teste em \(T^1\) prova o caso \(T^7\).

O repositório `papers` contém motores ARM32 descritos como arquitetura T⁷, Exacordex, Raefaelos, BitRAF e variantes de recorrência. A relação aqui é pointer-only: implementação computacional não prova automaticamente propriedades analíticas do toro.

---

## 6. Heurísticas reversas, inversas e indiretas

### 6.1 Reversão de claim

Em vez de perguntar “o modelo explica o dado?”, perguntar:

\[
\text{Que observação tornaria impossível esta classe de modelo?}
\]

### 6.2 Inversão de parametrização

Se \(Y=F(\theta)\), testar identificabilidade:

\[
F(\theta_1)=F(\theta_2)\Rightarrow \theta_1=\theta_2\ ?
\]

Caso contrário, registrar degenerescência, não descoberta.

### 6.3 Caminho indireto

\[
\mathcal C_\gamma\to T_{\mu\nu}^{eff}\to G_{\mu\nu}\to H(z)
\]

A sessão começa pelo primeiro e último termos; o tensor efetivo intermediário permanece `TOKEN_VAZIO`.

### 6.4 Antiderivada documental

\[
K(T)=K(0)+\int_0^T \dot K(t)\,dt
\]

Na prática:

\[
K_N=K_0+\sum_{n=1}^N q_n\Delta I_n
\]

O peso \(q_n\) deve depender de proveniência, teste, replicação e autoridade da fonte.

---

## 7. Permutação multinível

Cada família deve ser analisada no produto:

\[
\mathcal P=
\mathcal O\times
\mathcal E\times
\mathcal S\times
\mathcal T
\]

onde:

- \(\mathcal O\): operação (`DIR`, `REV`, `INV`, `REC`, `IND`, `REL`, `DER`, `ANTI`);
- \(\mathcal E\): escala (local, galáctica, cosmológica, documental);
- \(\mathcal S\): estado epistêmico;
- \(\mathcal T\): topologia (linear, cíclica, toroidal, tensorial).

Uma permutação é válida somente se preservar tipos e unidades. Combinações incompatíveis produzem `TYPE_ERROR`, não conhecimento novo.

---

## 8. Cruzamento com `papers`

Autoridades observadas no repositório privado `rafaelmeloreisnovo/papers`:

- motores Exacordex e Raefaelos em C/ASM;
- variantes ARM32, NEON, RNN, coevolução e auto-organização;
- arquitetura declarada T⁷;
- BitRAF e tensor/ASM RAFAELIA;
- notas com fronteiras de evidência e `TOKEN_VAZIO`;
- Ω-CUBE-42 e recorrência/plasticidade como documentos claim-bounded.

Regras de integração:

1. RLL permanece autoridade para cosmologia, dados reais e claims cosmológicos.
2. `papers` permanece autoridade para motores e notas ali armazenadas.
3. Não copiar conteúdo privado bruto para o RLL público.
4. Usar ponte por referência, hash ou manifesto quando necessário.
5. Resultado de runtime não substitui demonstração matemática.
6. Analogia neuro/cognitiva não substitui evidência clínica ou biológica local.

Os números “493” e “60” citados pelo autor não foram confirmados por um manifesto lido nesta execução; permanecem `TOKEN_VAZIO_COUNT_493_60` até associação a arquivos, commits, papers ou linhas específicas.

---

## 9. Implementações conectadas à CI Tier 1

Este cânone se conecta ao PR de skills científicos:

- **C1 — anomalias:** implementa derivações `REL` e `REV` sobre dados numéricos, sem confundir hash com observável;
- **B4 — Fourier T¹:** implementa `TOR`, `DUAL` e teste de redução mínima;
- **D1 — proxy Bayes/BIC:** implementa comparação reversa entre dados e parâmetros, rotulada como aproximação.

Próximos operadores implementáveis:

1. `NULL`: regressão automática \(O_{s0}=0\Rightarrow\Lambda CDM\);
2. `DER`: Jacobiano numérico de \(H(z)\) por parâmetro;
3. `PERM`: invariância do teste Fourier sob permutação de eixos sintéticos controlados;
4. `REC`: sistema acoplado com classes explícitas de \(Q\);
5. `TYPE`: schema das Quatro Tintas + TOKEN_VAZIO em JSON Schema.

---

## 10. Hipóteses nulas e falsificadores

| Família | Hipótese nula mínima | Falsificador operacional |
|---|---|---|
| setor fotônico dual | \(O_{s0}=0\) | posterior compatível com zero e penalidade persistente |
| transição ext/col | modelo sem transição | ausência de ganho preditivo fora da amostra |
| \(Q\neq0\) | \(Q=0\) | evidência não favorece interação |
| T⁷ | separabilidade/redução | falha de invariância ou convergência |
| TOKEN_VAZIO | missing comum basta | perda de proveniência ou coerção indevida a zero |
| Quatro Tintas | classificação não agrega | baixa concordância e ausência de redução de overclaim |
| ciclo cognitivo | baseline linear | modelo recorrente não melhora previsão replicada |
| \(\sqrt3/2\) universal | constante arbitrária | desempenho igual a constantes-controle |

---

## 11. Resultado desta retroalimentação

### F_ok

- As 25 famílias foram convertidas em matriz de operações.
- Foram distinguidas derivações diretas, reversas, inversas, indiretas, relativas, escalares e toroidais.
- RLL e `papers` receberam fronteiras de autoridade explícitas.
- O ciclo vazio→Verbo→novo vazio foi formalizado como procedimento epistêmico.

### F_gap

- Falta derivação microscópica do tensor fotônico efetivo.
- Falta recorrência canônica da Fibonacci Rafael.
- Faltam definições completas das quatro hyperformas.
- Faltam manifestos que identifiquem precisamente os números 493 e 60.
- Faltam resultados CI para os novos operadores.

### F_next

\[
F_{next}=
\{
\text{schema formal},
\text{teste de limite nulo},
\text{Jacobiano},
\text{modelos }Q,
\text{receipts cross-repo}
\}
\]

Cada resultado fecha um vazio e, por fechamento, produz um vazio novo mais estreito. Esse é o sentido operacional de retroalimentação: não declarar totalidade, mas aumentar resolução, rastreabilidade e poder de falsificação.
