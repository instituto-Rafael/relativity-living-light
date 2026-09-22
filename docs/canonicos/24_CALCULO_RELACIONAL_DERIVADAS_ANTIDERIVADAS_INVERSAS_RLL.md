# 24 — Cálculo Relacional: Derivadas, Antiderivadas, Inversas e Meta-Relações RLL

**Data:** 2026-09-05  
**Estado:** `CANONICAL_CANDIDATE / MATHEMATICAL_BRIDGE / CLAIM_GATED`  
**Escopo:** integrar o cálculo relacional matemático da RAFAELIA ao RLL/MCRP sem converter analogia geométrica em evidência cosmológica.

## 0. Regra epistemológica

O RLL recebe deste pacote apenas relações matemáticas tipadas:

```text
DIRECT
INVERSE
DERIVATIVE
ANTIDERIVATIVE
EXCLUSIVE / NULL-ALTERNATIVE
COMPOSITION
CORRELATION
INVARIANT
META-RELATION
```

Nenhuma igualdade entre constantes geométricas, modulares ou Fibonacci é evidência observacional de cosmologia.

## 1. Ponte com a equação canônica RLL

O modelo canônico usa

\[
E^2(a)=\Omega_r a^{-4}+\Omega_m a^{-3}+\Omega_\Lambda
+\Omega_{s0}g(a)+\Omega_{B0}a^{-4}+\Omega_{P0}a^{-4},
\]

com

\[
\boxed{g(a)=f(a)+(1-f(a))a^{-3}}.
\]

A transição logística é

\[
f(z)=\frac1{1+\exp((z-z_t)/w_t)},
\qquad
a=\frac1{1+z}.
\]

Este documento expande as relações diferenciais e inversas já implícitas nessa formulação.

## 2. Derivada da transição logística

Em redshift:

\[
\boxed{
\frac{df}{dz}=-\frac1{w_t}f(1-f)
}.
\]

Como

\[
\frac{dz}{da}=-\frac1{a^2},
\]

segue

\[
\boxed{
\frac{df}{da}=\frac{f(1-f)}{w_t a^2}
}.
\]

A segunda derivada é

\[
\boxed{
\frac{d^2f}{da^2}
=f(1-f)
\left[
\frac{1-2f}{w_t^2a^4}
-\frac{2}{w_ta^3}
\right]
}.
\]

Essas expressões podem ser usadas para sensibilidade, curvatura da transição e verificação de implementações numéricas.

## 3. Derivadas do setor de superposição

Para

\[
g(a)=f(a)+(1-f(a))a^{-3},
\]

já se obtém

\[
\boxed{
g'(a)=f'(a)(1-a^{-3})-3(1-f)a^{-4}
}.
\]

A segunda derivada é

\[
\boxed{
g''(a)=f''(a)(1-a^{-3})+6f'(a)a^{-4}+12(1-f)a^{-5}}.
\]

Portanto a geometria local de `g` pode ser analisada por sinal de `g'`, zeros de `g'`, sinal de `g''` e pontos de inflexão, sem interpretar automaticamente essas estruturas como novos fenômenos físicos.

## 4. Equação de estado efetiva: direta e inversa

A relação canônica é

\[
\boxed{
w_{eff}(a)=-1-\frac{a}{3}\frac{g'(a)}{g(a)}}.
\]

A relação inversa diferencial é

\[
\boxed{
\frac{g'(a)}{g(a)}=-\frac{3(1+w_{eff}(a))}{a}
}.
\]

Integrando entre `a0` e `a`:

\[
\boxed{
\ln\frac{g(a)}{g(a_0)}
=-3\int_{a_0}^{a}\frac{1+w_{eff}(u)}{u}\,du
}.
\]

Logo

\[
\boxed{
g(a)=g(a_0)\exp\left[-3\int_{a_0}^{a}\frac{1+w_{eff}(u)}{u}\,du\right]}.
\]

Isto fornece o par tipado:

```text
g(a) --DERIVATIVE--> w_eff(a)
w_eff(a) --ANTIDERIVATIVE--> g(a) up to normalization g(a0)
```

## 5. Sensibilidade direta aos parâmetros

Mantendo os demais termos fixos:

\[
\boxed{\frac{\partial E^2}{\partial\Omega_{s0}}=g(a)}.
\]

Para `E>0`:

\[
\boxed{\frac{\partial E}{\partial\Omega_{s0}}=\frac{g(a)}{2E(a)}}.
\]

No limite nulo

\[
\Omega_{s0}=0,
\]

o setor adicional desaparece, mas a derivada paramétrica `g(a)` continua definindo a direção local em que o modelo se afasta do nulo. Essa é uma ponte natural para Fisher information, perfil de likelihood e testes de identificabilidade.

## 6. Hipóteses exclusivas/nested do RLL

A comparação deve distinguir:

```text
H0: Omega_s0 = 0
H1: Omega_s0 free
```

`H0` é um submodelo aninhado de `H1`; não é um universo sem relação matemática com ele.

Uma promoção de claim exige comparar:

```text
likelihood
Delta chi2
AIC/AICc/BIC
posterior or profile interval
boundary behavior at Omega_s0=0
stability across seeds/data combinations
```

A palavra `exclusive` aqui significa hipótese/modelo mutuamente selecionado no teste; não XOR físico.

## 7. Distância cosmológica como antiderivada de H(z)

Em geometria espacial plana, a distância comóvel é

\[
\boxed{D_C(z)=c\int_0^z\frac{du}{H(u)}}.
\]

Logo

\[
\boxed{\frac{dD_C}{dz}=\frac{c}{H(z)}}.
\]

Como

\[
D_L(z)=(1+z)D_C(z),
\]

segue a relação direta

\[
\boxed{D_L(z)=(1+z)c\int_0^z\frac{du}{H(u)}}.
\]

E a inversa formal

\[
\boxed{
H(z)=
\frac{c}{\displaystyle\frac{d}{dz}\left[D_L(z)/(1+z)\right]}
}.
\]

**Boundary:** a inversão por derivação amplifica ruído observacional. Em dados reais, regularização/smoothing e propagação de covariância são obrigatórios; a fórmula exata não autoriza uma reconstrução numérica ingênua.

## 8. CPL como par derivada–antiderivada

Para o adversário CPL:

\[
\boxed{w(z)=w_0+w_a\frac{z}{1+z}}.
\]

A derivada é

\[
\boxed{\frac{dw}{dz}=\frac{w_a}{(1+z)^2}}.
\]

O fator de densidade escura usado no pipeline é

\[
X(z)=(1+z)^{3(1+w_0+w_a)}
\exp\left(-\frac{3w_a z}{1+z}\right).
\]

Ele satisfaz

\[
\boxed{
\frac{d\ln X}{dz}=\frac{3(1+w(z))}{1+z}
}.
\]

Portanto

\[
\boxed{
X(z)=X(0)\exp\left[3\int_0^z\frac{1+w(u)}{1+u}\,du\right]
}.
\]

Esta é uma conexão direta para comparar RLL e CPL no mesmo vocabulário diferencial/integral.

## 9. Relação direta/inversa com dinâmica de grafo

Para uma camada de grafo

\[
\dot x=-Lx+f(t),
\]

a solução direta é

\[
\boxed{
x(t)=e^{-Lt}x(0)+\int_0^t e^{-L(t-s)}f(s)\,ds
}.
\]

A força inversa é

\[
\boxed{f(t)=\dot x+Lx}.
\]

No estado estacionário e no subespaço compatível:

\[
\boxed{x_*=L^\dagger f}.
\]

Qualquer interpretação de `f`, `x` ou `L` como campo físico do RLL requer contrato observacional próprio.

## 10. Integração com a geometria midpoint sem fusão de domínios

O pacote matemático externo ao RLL define

\[
T(c)=\frac{1+3c}{2(1+c)}
\]

com coordenada projetiva

\[
z(c)=\frac{c-1}{c+1/2}
\]

e identidade

\[
\boxed{z(T(c))=z(c)/4}.
\]

Isto pode servir como **heurística de renormalização** ou família de kernels/priors a ser testada, mas permanece proibido escrever:

```text
midpoint contraction 1/4 => cosmological truth
pi*phi/5 => dark-energy constant
42 icosphere vertices => 42 cosmological attractors
```

Uma ponte só existe se um observable, likelihood e falsificador forem definidos.

## 11. Rafaeliana/Fibonacci como cálculo discreto

A Rafaeliana inteira

\[
R_n=F_{n+3}-1
\]

satisfaz

\[
\boxed{R_n=\sum_{k=0}^{n+1}F_k},
\qquad
\boxed{\Delta R_n=F_{n+1}}.
\]

No RLL isso pode ser usado como régua discreta, índice de escala, discretização experimental ou prior computacional. Não é justificativa física para o modelo cosmológico.

## 12. Correção do ponto fixo histórico

Para a recorrência real

\[
x_{n+1}=\frac{\sqrt3}{2}x_n-\pi\sin279^\circ,
\]

o ponto fixo com constantes reais exatas é

\[
\boxed{x_*\approx23.16046864479797}.
\]

O valor histórico `23.158` deve ser tratado como `LEGACY_QUANTIZED_OR_ROUNDED` até reconstrução do contrato Q16 correspondente. O RLL não deve usar `23.158` como constante matemática exata.

## 13. Meta-relation registry for RLL

Cada relação cross-domain deve registrar:

```text
id
source_object
source_domain
target_object
target_domain
relation_type
assumptions
exact_or_approximate
observable
likelihood_or_test
evidence_pointer
falsifier
claim_state
```

Estados mínimos:

```text
FORMAL_IDENTITY
DERIVED
HEURISTIC
CORRELATION_ONLY
EMPIRICAL_SUPPORT
CONTRADICTION
TOKEN_VAZIO
```

## 14. Research hypotheses opened by this integration

### RLL-RC-H1 — identifiability of transition derivatives

Can `f'(a)`/`g'(a)` be constrained independently of a generic `w0-wa` background with current combined data?

### RLL-RC-H2 — inverse distance reconstruction

Can a regularized reconstruction of

\[
H(z)=c/[d(D_L/(1+z))/dz]
\]

recover injected RLL transition signatures without false structure from smoothing?

### RLL-RC-H3 — curvature of g(a)

Do zeros/sign changes of `g''(a)` define a stable, parameter-identifiable transition feature across posterior samples?

### RLL-RC-H4 — null-direction score

Does the score direction

\[
\partial E^2/\partial\Omega_{s0}=g(a)
\]

remain linearly independent from CPL/GEDE/IDE directions over the observed redshift window?

These are testable hypotheses, not claims of success.

## 15. Non-equivalence gates

```text
MATHEMATICAL DERIVATION != DATA SUPPORT
DATA FIT != CAUSAL MECHANISM
NUMERIC COINCIDENCE != CROSS-DOMAIN INVARIANT
INVERSE FORMULA != STABLE INVERSE PROBLEM
HEURISTIC RENORMALIZATION != COSMOLOGICAL RENORMALIZATION
RLL != SOLUTION OF AN OPEN PROBLEM BY ANALOGY
```

## R3

```text
F_ok:
  RLL derivative/integral/inverse vocabulary formalized;
  g, f, w_eff, distances and CPL connected rigorously;
  geometry/Fibonacci imported only as typed heuristics;
  23.158 discrepancy explicitly bounded.

F_gap:
  numerical derivative validation against pipeline;
  Fisher/profile identifiability study;
  regularized H(z) inverse reconstruction;
  prior-art map for proposed cross-domain operators.

F_next:
  executable symbolic/numeric KAT;
  integrate relation registry into traceability map;
  test RLL-RC-H1..H4 on real-data pipeline.
```
