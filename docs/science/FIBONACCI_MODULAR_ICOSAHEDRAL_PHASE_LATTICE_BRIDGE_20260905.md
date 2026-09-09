# RLL: ponte modular, icosaédrica e de fase 420

**Data:** 2026-09-05  
**Estado:** \(\texttt{METHODS\_BRIDGE + CLAIM\_GATED}\)  
**Claim científico novo:** não promovido  
**claim_allowed:** \(\texttt{false}\)

## 1. Fonte e escopo

A fonte matemática é o PR 67 de papers:

https://github.com/rafaelmeloreisnovo/papers/pull/67

Ele contém uma nota formal, um ledger de claims, um verificador Python e
um receipt de execução.

Esta nota é uma ponte de método. Ela não é extensão da equação
cosmológica RLL.

\[
\text{método geométrico}
 \not\Rightarrow\text{termo físico}
 \not\Rightarrow\text{modelo validado}.
\]

Ela não altera \(H(z)\), \(\Omega_i\), priors, likelihoods,
covariâncias, \(\chi^2\), AIC/BIC ou resultados RLL.

## 2. Entrada matemática declarada

A ponte pode citar, no domínio estritamente matemático:

- \(0_{\bmod m}\neq TOKEN\_VAZIO\).

- Para \(R_n=F_{n+3}-1\), translação modular preserva
  \(d_m(R_n,R_k)=d_m(F_{n+3},F_{k+3})\).

- A janela \((F_n,\ldots,F_{n+6})\pmod m\) está em
  \((\mathbb Z_m)^7\).

- Sua normalização é um subgrupo finito de
  \(T^7=(\mathbb R/\mathbb Z)^7\), não o toro contínuo inteiro.

- No triângulo central de uma face icosaédrica, a razão arco–corda é
  \(\pi\phi/5\).

- A malha 420 é o refinamento comum de grades de fase 60 e 7.

Essas relações são identidades ou enumerações finitas. Não são
observáveis RLL.

## 3. Uso permitido

A ponte pode ser usada para:

- declarar uma convenção de coordenadas para um fixture discreto;

- testar invariância em código geométrico com hash e baseline;

- representar fases, desde que módulo, orientação e escala sejam
  declarados;

- propor uma feature exploratória antes de um experimento
  pré-registrado.

## 4. Uso bloqueado

A ponte não pode ser usada para:

- inserir um novo termo em \(H(z)\) ou na ação EFT;

- afirmar curvatura física, atratores físicos ou uma lei de primos;

- alegar melhoria de RLL contra \(\Lambda\)CDM ou CPL;

- promover uma analogia geométrica a mecanismo físico.

## 5. Gate para ponte física

Antes de qualquer promoção, são necessários:

1. variável física explícita, com unidade;

2. mapa discreto para essa variável;

3. equação dinâmica, parâmetros e condições iniciais;

4. observável quantitativo pré-registrado;

5. dataset, seleção, likelihood, covariância e ambiente;

6. baseline \(\Lambda\)CDM e concorrentes adequados;

7. ablação com e sem a feature;

8. falsificador definido antes do ajuste;

9. artifacts, hashes, logs e reprodução independente.

Sem todos os itens, a estrutura permanece fora do registry de fórmulas
canônicas.

## 6. TOKEN_VAZIO e falsificação

Os estados abertos são:

- TV-RLL-MODICO-001: falta mapa com unidade entre fase e variável.

- TV-RLL-MODICO-002: falta derivação dinâmica de um termo RLL.

- TV-RLL-MODICO-003: falta previsão quantitativa fora de amostra.

- TV-RLL-MODICO-004: faltam likelihood, covariância e baseline.

- TV-RLL-MODICO-005: falta reprodução cross-host.

- TV-RLL-MODICO-006: novidade permanece bloqueada sem revisão
  primária de anterioridade.

A ponte falha como mecanismo físico se os resultados forem explicados
pela aritmética e geometria declaradas, ou se não melhorar previsão
pré-registrada em comparação adversarial.

## 7. Relações internas

Esta nota complementa:

- "docs/science/MODULAR_FOLD_GAP_RULER_NUCLEAR_BRIDGE_20260902.md";

- "docs/research/OMEGA7_MODULAR_GEODESIC_TOROIDAL_FOCUS_20260818.md";

- "docs/RLL_TRACEABILITY_MAP.md".

O índice de fórmulas canônicas permanece inalterado.

## R3

**F_ok:** matemática finita foi roteada como método sem alterar claims
cosmológicos.

**F_gap:** faltam mapa dimensional, dinâmica, observável e likelihood.

**F_next:** só um experimento pré-registrado, com baseline e artifacts,
pode decidir se existe valor além da geometria.
