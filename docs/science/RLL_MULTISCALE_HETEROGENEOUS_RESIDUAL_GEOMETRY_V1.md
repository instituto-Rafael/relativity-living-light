# RLL — Residual Heterogêneo Multiescala × Fibonacci × Geometria Tipada — V1

**Data:** 2026-09-28  
**Estado:** `FORMAL_MODEL + LOCAL_REFERENCE_IMPLEMENTATION / claim_allowed=false`  
**Autor/proponente:** Rafael Melo Reis  
**Producer:** `instituto-Rafael/relativity-living-light`

## 0. Intenção

Formalizar a ideia de que a média global e um único desvio-padrão podem ocultar heterogeneidade, e que o residual observado deve permanecer tipado e reclassificável sem ser automaticamente chamado de ruído, causa ou nova física.

A composição reutiliza, sem colapsar:

- estatística clássica de média/variância/covariância;
- decomposição finita intra-grupo/inter-grupo;
- `DELTA_UNCLASSIFIED` como orçamento residual ainda não atribuído;
- Fibonacci clássica/Rafaeliana como régua multiescala e família de janelas;
- triângulo equilátero/isósceles, Pitágoras/Bhaskara e `sqrt(3)/2`;
- esfera geodésica/icosfera;
- bola de Poincaré e mapa/seção de Poincaré como objetos distintos;
- Venturi físico como adapter separado;
- ciclos de calendário como malha temporal/comparador, não como mecanismo cosmológico automático.

## 1. Correção estatística de base

Para população finita (x_1,ldots,x_N),

[
mu=rac1Nsum_{i=1}^N x_i,
qquad
sigma^2=rac1Nsum_{i=1}^N(x_i-mu)^2.
]

Para amostra,

[
ar x=rac1nsum_{i=1}^n x_i,
qquad
s^2=rac1{n-1}sum_{i=1}^n(x_i-ar x)^2.
]

Logo, `sigma^2` não é “sigma quadrado menos as parcelas”; é a média dos desvios quadráticos na definição populacional. População e amostra recebem IDs distintos.

## 2. Média global não substitui distribuição

Se os dados pertencem a grupos (g), com (n_g), média (mu_g) e média global (mu), a identidade finita é

[
oxed{
sum_i(x_i-mu)^2
=
sum_gsum_{iin g}(x_i-mu_g)^2
+
sum_g n_g(mu_g-mu)^2
}
]

ou

[
TSS=WSS+BSS.
]

Assim, uma média global pode estar correta e ainda esconder que quase toda a dispersão está entre subpopulações.

Definimos o diagnóstico descritivo

[
eta^2_G=rac{BSS}{TSS}
]

quando (TSS>0). Aqui (eta^2_G) mede fração da soma de quadrados associada à partição declarada; não prova causalidade.

## 3. Incerteza de medição e margem

Com incertezas independentes declaradas (u_i), o adaptador de referência usa

[
operatorname{Var}(ar x)
=
rac{s^2}{n}
+
rac{1}{n^2}sum_i u_i^2.
]

A margem só é produzida se um fator crítico (k) tiver sido pré-declarado:

[
ME=ksqrt{operatorname{Var}(ar x)}.
]

Sem (k):

`TOKEN_VAZIO_CRITICAL_VALUE`.

Sem incerteza observacional suficiente:

`TOKEN_VAZIO_UNCERTAINTY`.

Nenhum nível de confiança é inferido silenciosamente.

## 4. Residual e ∆ não classificado

Para observação (y_i) e previsão (m_i),

[
r_i=y_i-m_i.
]

Cada residual recebe uma classe de bookkeeping:

- `DELTA_MEASUREMENT`
- `DELTA_MODEL`
- `DELTA_OMITTED_VARIABLE`
- `DELTA_LATENT`
- `DELTA_STOCHASTIC`
- `DELTA_UNCLASSIFIED`

O default é `DELTA_UNCLASSIFIED`.

A soma de quadrados residual é particionada por rótulo:

[
SSE=sum_c SSE_c,
qquad
SSE_c=sum_{i:,class(i)=c}r_i^2.
]

Isso é fechamento de classificação dos registros, **não** prova de que a causa física pertence à classe escolhida.

Quando há evidência suficiente, um registro pode migrar:

[
DELTA_UNCLASSIFIED
	o
DELTA_MEASUREMENT
quad	ext{ou}quad
DELTA_MODEL
quad	ext{etc.}
]

A observação não é apagada; muda o estado epistemológico.

## 5. Covariância / coerência dual

A autoridade matemática predecessora usa

[
Q_j(w)=rac1n(y_w-m_{j,w})^T C_w^{-1}(y_w-m_{j,w})
]

e

[
Delta Q_w=Q_1(w)-Q_0(w).
]

Este V1 não substitui o gate existente `rll_deltaobs_residual.py`. Ele o precede/complementa, tornando explícitos heterogeneidade, classificação e escalas.

`RESIDUAL != NOISE != CAUSE != NEW_PHYSICS`.

## 6. Fibonacci como régua multiescala — não peso probabilístico

Fibonacci clássica:

[
F_0=0,quad F_1=1,quad F_{n+1}=F_n+F_{n-1}.
]

Matriz companheira:

[
Q_F=
egin{pmatrix}
1&1\\
1&0
end{pmatrix},
qquad
Q_F^n=
egin{pmatrix}
F_{n+1}&F_n\\
F_n&F_{n-1}
end{pmatrix}
quad(nge1).
]

No adaptador deste V1, Fibonacci define apenas tamanhos de janelas contíguas

[
2,3,5,8,13,ldots
]

para verificar se média, variância e residual mudam de comportamento com a escala.

**Invariante:** `FIBONACCI_WINDOW != LIKELIHOOD_WEIGHT`.

A Rafaeliana canônica permanece separada:

[
R_n=F_{n+3}-1,
qquad
Delta R_n=F_{n+1}.
]

## 7. Geometria euclidiana tipada

### 7.1 Pitágoras / diferença

[
c^2=a^2+b^2=2ab+(a-b)^2.
]

O termo ((a-b)^2) pode ser usado como medida geométrica de diferença sob esse domínio, mas não é automaticamente variância estatística.

### 7.2 Isósceles / equilátero

[
b(alpha)=2Lsinalpha,
qquad
h(alpha)=Lcosalpha.
]

Em (alpha=30^circ),

[
h=rac{sqrt3}{2}L.
]

Logo

[
q=rac{sqrt3}{2}
]

permanece kernel geométrico/projetivo; `q != sigma`.

### 7.3 Medianas

Para quadrados dos lados e medianas,

[
q_m=Mq_s,
qquad
M=rac14
egin{pmatrix}
-1&2&2\\
2&-1&2\\
2&2&-1
end{pmatrix},
]

[
M^2=rac9{16}I.
]

Essa matriz é um operador geométrico, não uma matriz de covariância.

## 8. Esfera geodésica / icosfera

Para subdivisão icosaédrica de frequência (f),

[
V=10f^2+2,quad E=30f^2,quad F=20f^2.
]

Em (f=2):

[
(V,E,F)=(42,120,80).
]

No corpus formal:

[
rac{s_g}{s_c}=rac{piphi}{5}
]

para a construção específica dos pontos médios esféricos declarada.

`piphi/5` permanece invariante geométrico desse objeto; não é promovido a constante física universal.

## 9. Poincaré — três namespaces separados

### A. Bola de Poincaré
Métrica/embedding hiperbólico. Pertencimento à bola não prova estabilidade física.

### B. Seção/mapa de Poincaré
Para fluxo linear no toro:

[
P(v)=v+2pirac{omega_v}{omega_u}pmod{2pi}.
]

### C. Conjectura de Poincaré
Objeto matemático histórico distinto, já resolvido externamente.

Hard gate:

[
POINCARE_BALL

eq
POINCARE_RETURN_MAP

eq
POINCARE_CONJECTURE.
]

Este V1 permite usar coordenadas/distâncias hiperbólicas como features somente quando manifold, métrica, domínio e transformação forem declarados.

## 10. Venturi como adapter físico separado

Somente no domínio de fluido com hipóteses adequadas:

[
A_1v_1=A_2v_2
]

e, na forma ideal de Bernoulli,

[
P+rac12ho v^2+ho gh=	ext{constante}.
]

Antes de qualquer binding RLL, exigir:

[
BIND(
geometry,
fluid,
units,
boundary_conditions,
viscosity,
temperature,
covariance,
falsifier
).
]

`VENTURI_PHYSICAL != VENTURI_METAPHOR != VENTURI_COMPUTATIONAL`.

## 11. Calendário/ciclos como eixo temporal, não causal

O RLL já contém verificador para a aritmética do Calendar Round:

[
operatorname{lcm}(365,260)=18980	ext{ dias}.
]

Neste formalismo, ciclos calendáricos podem gerar **janelas e hipóteses periódicas pré-registradas**. Não geram causalidade cosmológica.

`CALENDAR_PERIODICITY != ASTROPHYSICAL_MECHANISM`.

## 12. Composição operacional

```text
OBSERVATION
  -> units/provenance
  -> global mean + population/sample variance
  -> declared grouping
  -> within/between heterogeneity
  -> prediction residual
  -> DELTA_* classification
  -> declared uncertainty/covariance
  -> Fibonacci multiscale windows
  -> optional typed geometry features
       Euclidean
       geodesic/spherical
       Poincare
       toroidal
  -> domain adapter
       cosmology
       fluid/Venturi
       calendar/cycle
  -> existing RLL likelihood/residual gates
  -> falsifier
  -> evidence
  -> claim gate
```

## 13. Source/authority map

### Matemática
- `rafaelmeloreisnovo/Matem-tica-/docs/formal/DUAL_OBSERVATIONAL_COHERENCE_RESIDUAL_V1.md`
- `.../PITAGORAS_BHASKARA_ISOSCELES_POINCARE_CROSSWALK_V1.md`
- `.../FIBONACCI_INVERSE_REVERSE_JUMP_RULER_V1.md`
- `.../GEODESIC_PI_PHI_MOD7_INVARIANTS_V1.md`

### Papers
- `research_notes/2026-09-06_PITAGORAS_BHASKARA_ISOSCELES_POINCARE_CROSSREPO_LEDGER_V1.md`
- `docs/matematica_autoral/fibonacci_modular_icosahedral_phase_lattice_20260905.md`
- `papers/angular_overlap_sqrt3_geodesic_v1/paper.md`

### Drive
- `RAFAELIA — ATLAS X √3/2 · πφ · F4 — LEARNING DELTA — 2026-08-31`
- `OMEGA_G — Operador Geométrico Canônico V1`
- `RAFAELIA — Icosfera f=2 × Fibonacci × Palavra 20-bit × Paridade Dual — V1`
- `WORLD69 — Ledger Matemática e Geometria — 250 Itens — V1`

Drive funciona como memória/documentação; autoridade formal/executável permanece nos repositórios produtores.

## 14. Falsificadores / gates

Bloquear promoção quando:

1. média global for usada como substituta de grupos conhecidos sem declarar isso;
2. (N) e (n-1) forem trocados silenciosamente;
3. incerteza ausente for substituída por zero;
4. Fibonacci for usada como peso estatístico sem derivação/pré-registro;
5. matriz geométrica for chamada de covariância sem contrato;
6. Poincaré ball/return/conjecture forem fundidos;
7. residual estruturado for chamado de causa;
8. Venturi for ligado por semelhança visual sem fluido/unidades/contorno;
9. periodicidade de calendário for promovida a mecanismo astronômico/cosmológico sem dados;
10. `DELTA_UNCLASSIFIED` for apagado em vez de reclassificado com evidência.

## R3

```text
F_ok =
  variância populacional/amostral tipada
  + heterogeneidade WSS/BSS
  + residual classificável
  + Fibonacci multiescala
  + geometria/Poincare/Venturi/calendário separados por namespace

F_gap =
  binding a datasets RLL reais
  + covariance completa por dataset
  + escolha de grupos pré-registrada
  + testes externos/independentes das hipóteses físicas

F_next =
  executar o adaptador em fixtures sintéticas
  -> comparar com rll_deltaobs_residual.py
  -> ligar primeiro a um dataset real congelado
  -> só depois avaliar ganho científico
```
