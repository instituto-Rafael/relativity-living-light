# RLL — Ponte metodológica: Fibonacci modular, icosaedro e malha de fase 420

**Data:** 2026-09-05  
**Estado:** \(\texttt{METHODS\_BRIDGE + CLAIM\_GATED}\)  
**Claim científico novo:** não promovido  
**claim_allowed:** \(\texttt{false}\)  
**Autoridade matemática:** [papers — nota formal e verificador](https://github.com/rafaelmeloreisnovo/papers/blob/main/docs/matematica_autoral/fibonacci_modular_icosahedral_phase_lattice_20260905.md)

## 1. Escopo e autoridade

Esta nota registra uma ponte de método, não uma extensão da equação cosmológica RLL.

A fonte matemática contém:

1. a distância circular \(d_m\) em \(\mathbb Z_m\);
2. a identidade Rafaeliana \(R_n=F_{n+3}-1\);
3. ciclos e enumerações finitas módulo 7;
4. a inclusão do reticulado finito \((\mathbb Z_m)^7\) em \(T^7\);
5. o triângulo esférico central de uma face icosaédrica;
6. o refinamento comum de fases \(\operatorname{lcm}(60,7)=420\);
7. um verificador Python de biblioteca padrão e um receipt de execução.

O que esta ponte não faz:

\[
\text{método geométrico}
\not\Rightarrow
\text{termo físico}
\not\Rightarrow
\text{modelo cosmológico validado}.
\]

A nota não altera \(H(z)\), \(\Omega_i\), priors, likelihoods, covariâncias, resultados \(\chi^2\), AIC/BIC ou qualquer claim do RLL.

---

## 2. Resultados matemáticos que podem ser citados com domínio explícito

### 2.1. Classe zero e ausência de evidência

\[
0_{\bmod m}\neq TOKEN\_VAZIO.
\]

- \(0_{\bmod m}\) é uma coordenada/resíduo definido.
- \(TOKEN\_VAZIO\) marca definição, dado ou evidência insuficiente.

Esta separação é diretamente compatível com o contrato epistemológico RLL.

### 2.2. Isometria modular da Rafaeliana inteira

Para

\[
R_n=F_{n+3}-1,
\]

a translação modular por \(-1\) preserva a distância de menor arco:

\[
d_m(R_n,R_k)=d_m(F_{n+3},F_{k+3}).
\]

O resultado é uma identidade em ciclos finitos. Ele não seleciona uma escala física, uma geometria do espaço-tempo ou uma trajetória cosmológica.

### 2.3. Janela discreta em \(T^7\)

\[
\tau_m(n)=(F_n,\ldots,F_{n+6})\pmod m
\in(\mathbb Z_m)^7.
\]

Após normalização por \(m\), esse conjunto é um subgrupo finito de

\[
T^7=(\mathbb R/\mathbb Z)^7.
\]

A formulação correta preserva a diferença entre grade discreta e toro contínuo:

\[
\iota_m((\mathbb Z_m)^7)\subset T^7.
\]

### 2.4. Razão arco–corda icosaédrica

Na construção declarada de pontos médios geodésicos de uma face icosaédrica:

\[
s_{\mathrm{chord}}=\frac R\phi,
\qquad
s_{\mathrm{geo}}=\frac{\pi R}{5},
\]

\[
\frac{s_{\mathrm{geo}}}{s_{\mathrm{chord}}}
=
\frac{\pi\phi}{5}
\approx1.016640738463052.
\]

O valor é uma razão geométrica adimensional no modelo esférico. Não é uma constante física, uma densidade, uma energia ou uma frequência RLL.

### 2.5. Malha de fase 420

As grades de 30 e 36 graus são acomodadas pela malha 60; somando a divisão 7-fold, o refinamento comum mínimo é

\[
\operatorname{lcm}(60,7)=420.
\]

Isso define uma resolução de fase, não 420 objetos físicos. O módulo deve acompanhar qualquer fase: por exemplo, \(140\bmod100=40\) corresponde a \(144^\circ\), enquanto \(7\bmod70\) corresponde a \(36^\circ\).

---

## 3. Lugar permitido no RLL

No estado atual, a ponte pode ser usada apenas como:

| Uso | Permitido? | Condição |
|---|---|---|
| convenção de coordenada para um fixture discreto | sim | declarar módulo, orientação, escala e regra de normalização |
| teste de invariância em código geométrico | sim | incluir fixture, hash, baseline e resultado |
| visualização de fases | sim | marcar como representação, não observável |
| feature exploratória em um modelo | condicional | pré-registro, unidades, ablação e baseline |
| novo termo em \(H(z)\) ou na ação EFT | não | falta derivação dimensional e justificativa dinâmica |
| evidência de curvatura física, atratores ou nova lei de primos | não | TOKEN_VAZIO de mecanismo, previsão e dados |
| melhoria de RLL contra \(\Lambda\)CDM/CPL | não | exigir likelihood compartilhada, covariância e comparação quantitativa |

---

## 4. Gate de promoção para qualquer ponte física

Uma proposta que transforme a geometria acima em componente RLL deve conter todos os itens abaixo antes de entrar em um pipeline científico:

1. variável física inequívoca e unidade;
2. mapa explícito da coordenada discreta para essa variável;
3. equação dinâmica, parâmetros livres e condições iniciais;
4. observável quantitativo pré-registrado;
5. dataset, seleção, likelihood, covariância e ambiente de execução;
6. baseline \(\Lambda\)CDM e concorrentes apropriados;
7. ablação que compare o modelo com e sem a feature;
8. critério de falsificação definido antes do ajuste;
9. artifactos, hashes, logs e reprodução independente.

Sem esses itens, a ponte deve permanecer em matemática/metodologia e não atingir o registry de fórmulas canônicas.

---

## 5. Falsificadores e TOKEN_VAZIO

| ID | Estado atual | Saída exigida |
|---|---|---|
| TV-RLL-MODICO-001 | TOKEN_VAZIO | mapa com unidade entre fase/reticulado e variável física |
| TV-RLL-MODICO-002 | TOKEN_VAZIO | derivação dinâmica que justifique um termo RLL |
| TV-RLL-MODICO-003 | TOKEN_VAZIO | previsão quantitativa fora de amostra |
| TV-RLL-MODICO-004 | TOKEN_VAZIO | likelihood/covariância e baseline comparável |
| TV-RLL-MODICO-005 | TOKEN_VAZIO | reprodução cross-host da pipeline completa |
| TV-RLL-MODICO-006 | BLOCKED | qualquer alegação de novidade sem revisão de anterioridade e literatura primária |

A ponte é falsificada como mecanismo físico se sua saída for inteiramente explicada pela aritmética modular e geometria já declaradas, ou se ela não melhorar uma previsão pré-registrada em comparação adversarial.

---

## 6. Relação com documentos existentes

- "docs/science/MODULAR_FOLD_GAP_RULER_NUCLEAR_BRIDGE_20260902.md": contém a regra de separação entre modularidade e física; esta nota fornece uma instância formal mais estreita.
- "docs/research/OMEGA7_MODULAR_GEODESIC_TOROIDAL_FOCUS_20260818.md": mantém a fronteira entre \(T^7\), geometria local e interpretação física.
- "docs/RLL_TRACEABILITY_MAP.md": indexa a autoridade da nota e seus gates.
- "docs/FORMULAS_CANONICAS_INDEX.md": permanece inalterado porque não há nova fórmula física canônica.

## R3

**F_ok:** a matemática derivada foi incorporada ao RLL como método rastreável, sem contaminar equações ou claims cosmológicos.  
**F_gap:** não existe mapa dimensional, dinâmica, observável ou likelihood que conecte a estrutura a dados RLL.  
**F_next:** somente um experimento pré-registrado com baseline e artefatos pode decidir se a ponte tem qualquer valor além da geometria.
