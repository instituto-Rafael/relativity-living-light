# RLL — Censo Total de Permutações, Vazio Tipado e Recuperação NIBIGUIRI V1

**Data:** 2026-10-04  
**Estado:** `BOUNDED_PERMUTATION_CENSUS / APPEND_ONLY / claim_allowed=false`  
**Escopo:** interação atual + fontes matemáticas já ligadas ao RLL.  
**Regra:** `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`.

## 0. Objetivo

Consolidar, sem apagar versões anteriores, os elementos numéricos, geométricos,
modulares, radicais, de base e de vazio discutidos nesta sequência e submetê-los
a uma gramática explícita de permutação.

Este documento **não** declara que toda combinação tem significado físico.
Ele registra candidatos, identidades, aproximações, contradições, lacunas e
relações de representação para permitir falsificação posterior.

Também não atribui causalidade a ausências. Um item que só reaparece nesta
interação é classificado como `USER_REINTRODUCED` ou `OBSERVED_UNINDEXED`, não
automaticamente como "ignorado" ou "esquecido".

## 1. Proveniência mínima

Autoridades cruzadas já existentes:

- Matemática formal:
  - `PITAGORAS_BHASKARA_ISOSCELES_POINCARE_CROSSWALK_V1.md`
  - `GLOBAL_CONTEXT_SEMANTIC_DYNAMICS_CLOSURE_V4.md`
  - `CROWN_15_30_45_PI12_PI5_GEODESIC_REFLECTION_CROSSWALK_V1.md`
  - matriz MF-0001..MF-0251.
- Papers:
  - `RAFAELIA_GEODESIC_TOROIDAL_14D_VISUAL_SYNTHESIS_2026-09-12.md`
  - `radial_partition_5_6_7_8_geometry_v1/paper.md`
  - `2026-09-19_EIGHT_CONNECTED_GEOMETRY_PREDECESSOR_CROSSWALK_V1.md`.
- RLL:
  - `RLL_GEOMETRIC_DISPERSION_FALSE_POSITIVE_GATE_V1.md`
  - `RLL_REPDIGIT_3_7_GEOMETRY_MOLDS_V1.md`.

## 2. Inventário atômico desta sessão

O executor usa 37 átomos numéricos/simbólicos.

### 2.1 Primos e fatores

```text
2, 3, 5, 7, 11, 13, 37
```

Relações exatas:

```text
21   = 3*7
42   = 2*3*7
1001 = 7*11*13
111111 = 3*7*11*13*37
```

### 2.2 Compostos, moldes e repdigits

```text
10, 12, 14, 18, 21, 30, 42, 50, 70,
33, 77, 333, 777, 999
```

### 2.3 Irracionais, radicais e escalas

```text
pi
phi = (1+sqrt(5))/2
sqrt(5)
sqrt(pi)
sqrt(phi)
sqrt(3)/2
sqrt(3/2)
3/2
sqrt(5)/pi
sqrt(pi/5)
sqrt(pi/12)
sqrt(pi)/pi
sqrt(phi)/pi
sqrt(pi)/phi
sqrt(phi/pi)
sqrt(pi/phi)
```

Fronteira obrigatória:

```text
sqrt(3)/2 != sqrt(3/2) != 3/2
```

## 3. Divisões repdigit 7/3 e 3/7

### 3.1 Família 7...7 / 3

```text
7/3     = 2 + 1/3
77/3    = 25 + 2/3
777/3   = 259
```

Para prefixos sucessivos de dígito 7, o resto obedece:

```text
r_(n+1) = (10*r_n + 7) mod 3
        = (r_n + 1) mod 3
```

Órbita:

```text
1 -> 2 -> 0 -> 1
```

O zero é fechamento modular, não ausência.

### 3.2 Família 3...3 / 7

```text
3/7     = 0 + 3/7
33/7    = 4 + 5/7
333/7   = 47 + 4/7
```

O prefixo obedece:

```text
r_(n+1) = (10*r_n + 3) mod 7
        = (3*r_n + 3) mod 7
```

A órbita do prefixo iniciado em zero é:

```text
3 -> 5 -> 4 -> 1 -> 6 -> 0 -> 3
```

Há ainda um ponto fixo:

```text
T(2)=2
```

Portanto o grafo funcional de `Z_7` é:

```text
{2} fixo
+
(3,5,4,1,6,0) ciclo de seis estados
```

Isso não transforma automaticamente os seis estados em um hexágono físico.

### 3.3 Gate de representação

```text
77/33   = 7/3
777/333 = 7/3
```

com:

```text
gcd(77,33)=11
gcd(777,333)=111
```

Qualquer operador que alegue depender somente da razão deve satisfazer:

```text
F(77,33)=F(777,333)=F(7,3)
```

Se não satisfizer, o efeito é dependente da representação.

## 4. Bases: zero como ponto, não como nulo

A string posicional:

```text
10_b = b
```

Logo:

```text
10_10 = 10
10_7  = 7
```

Em uma base `b`, o dígito `0` ocupa uma posição com coeficiente zero. Ele não
significa que o objeto ou a observação estejam ausentes.

Em aritmética modular:

```text
[0]_p = {...,-2p,-p,0,p,2p,...}
```

Assim, `0 mod p` é uma classe de equivalência válida.

## 5. Moldes geométricos

Para um círculo de raio `R`, polígono/estrela regular `{n/k}`:

```text
theta_step = 2*pi*k/n
half_step  = pi*k/n
chord      = 2*R*sin(pi*k/n)
components = gcd(n,k)
cycle_len  = n/gcd(n,k)
```

Molde base:

```text
{5/1}  pentágono
{5/2}  pentagrama
{7/1}  heptágono
{11/1}
{12/1} dodecágono
{12/5} dodecagrama conectado
{13/1}
{18/1}
{21/1}
{42/1}
```

Não colapsar:

```text
{5/1} != {5/2}
{12/1} != {12/5}
```

## 6. Escalares 5, 12, pi e phi

Definições:

```text
s5  = sqrt(pi/5)
s12 = sqrt(pi/12)
```

Identidades:

```text
s5^2  = pi/5  = 36 graus
s12^2 = pi/12 = 15 graus
s5/s12 = sqrt(12/5)
```

Ponte Crown formal:

```text
cos(30°)*sqrt(pi/12)
-------------------- = sqrt(5)/2
sin(30°)*sqrt(pi/5)
```

Pentagrama:

```text
phi = (1+sqrt(5))/2
diagonal/lado = phi
sqrt(5)=2*phi-1
```

Outros escalares candidatos:

```text
sqrt(5)/pi
sqrt(pi)/pi = 1/sqrt(pi)
sqrt(phi)/pi
sqrt(pi)/phi
sqrt(phi/pi)
sqrt(pi/phi)
```

Reciprocidade exata:

```text
sqrt(phi/pi) * sqrt(pi/phi) = 1
```

Aproximação observada, mas não identidade:

```text
sqrt(5)/pi ~= sqrt(phi/pi)
```

A diferença relativa é inferior a 1%, portanto é um ótimo controle de falso
positivo: proximidade numérica não autoriza equivalência sem prova.

## 7. Espiral e z

Fonte histórica preservada:

```text
z_n = r0*(sqrt(3)/2)^n * exp(i*n*pi*phi)
```

Então:

```text
sqrt(phi)/z_n
```

é um operador que inverte amplitude e fase em relação a `z_n`, enquanto:

```text
z_n/sqrt(phi)
```

é outra transformação. Não são escalares fixos quando `z` varia.

Qualquer uso de `z` precisa declarar:

```text
domínio
unidade
índice n
r0
fase
observável
```

Caso contrário:

```text
Z_PHYSICAL_BINDING = TOKEN_VAZIO
```

## 8. Gramática de permutação

Para os 37 átomos, o executor percorre todas as **duplas ordenadas distintas**
e aplica:

```text
a+b
a-b
a*b
a/b   (b != 0)
```

Contagem:

```text
37*36*4 = 5328 candidatos binários ordenados
```

A ordenação é preservada mesmo para operadores comutativos porque o censo
mantém a proveniência da posição.

Operadores unários:

```text
square(a)
inverse(a)
sqrt(a), para a>=0
```

Como os 37 átomos desta versão são positivos:

```text
37*3 = 111 candidatos unários
```

Censo modular:

```text
moduli =
{2,3,5,7,10,11,12,13,14,18,21,30,42,50,70}
```

Com 21 átomos inteiros no catálogo:

```text
21*15 = 315 pares atom/modulus
```

Período aritmético conjunto:

```text
lcm(2,3,5,7,10,11,12,13,14,18,21,30,42,50,70)
= 900900
```

`900900` é um carrier aritmético, não um período físico.

## 9. O que significa "permutar tudo"

Não significa aceitar todos os 5754 candidatos como fórmulas.

O pipeline é:

```text
ATOM
-> OPERATOR
-> CANDIDATE
-> NORMALIZE
-> EQUIVALENCE/NEARNESS
-> DOMAIN CHECK
-> UNIT CHECK
-> SOURCE CHECK
-> NEGATIVE CONTROL
-> HOLDOUT
-> EVIDENCE
-> CLAIM GATE
```

Estados possíveis:

```text
IDENTITY_EXACT
DERIVED_EXACT
REPRESENTATION_EQUIVALENT
APPROX_NEAR_NOT_EQUAL
DIAGNOSTIC_CANDIDATE
CONTRADICTION
NEGATIVE_EVIDENCE
TOKEN_VAZIO_*
NOT_APPLICABLE
REJECTED
```

## 10. Taxonomia do vazio

Nesta versão há dez estados que não podem ser silenciosamente fundidos:

```text
NUMERIC_ZERO
RESIDUE_ZERO
EMPTY_SET
NULL_VALUE
TOKEN_VAZIO
UNDEFINED
NO_REAL_SOLUTION
MISSING_OBSERVATION
NOT_APPLICABLE
APPROX_ZERO
```

### 10.1 Relações

```text
NUMERIC_ZERO == NUMERIC_ZERO
NUMERIC_ZERO ~ APPROX_ZERO      somente sob tolerância declarada
NUMERIC_ZERO ↔ RESIDUE_ZERO     relacionados por contexto, não idênticos
NUMERIC_ZERO != EMPTY_SET
NUMERIC_ZERO != NULL_VALUE
NUMERIC_ZERO != TOKEN_VAZIO
NUMERIC_ZERO != UNDEFINED
NUMERIC_ZERO != MISSING_OBSERVATION
```

`NO_REAL_SOLUTION` também não é zero. Exemplo: discriminante negativo pode
indicar ausência de interseção real sem implicar valor numérico zero.

### 10.2 "Igual ao vazio", "diferente do vazio", "aproximado do vazio"

Só são expressões válidas após tipar o vazio.

- `x = 0`: igualdade numérica.
- `x mod p = 0`: pertencimento à classe residual zero.
- `x = ∅`: igualdade set-theórica com conjunto vazio.
- `x is NULL`: ausência de valor em um esquema.
- `x = TOKEN_VAZIO_*`: lacuna tipada; não possui valor numérico implícito.
- `|x| < epsilon`: aproximadamente zero sob uma tolerância explícita.
- expressão indefinida: não comparável a zero até resolver domínio.

## 11. Recuperação NIBIGUIRI

Classes desta passagem:

```text
USER_REINTRODUCED
  sqrt(pi)/pi
  sqrt(phi)/z
  permutações sqrt/pi/phi/z

OBSERVED_UNINDEXED_IN_THIS_PR_BEFORE
  taxonomia completa de vazio
  carrier conjunto de todos os módulos desta sequência
  gramática binária/unária completa

NEGATIVE_EVIDENCE / FALSE-POSITIVE CONTROLS
  sqrt(5)/pi ~= sqrt(phi/pi) mas !=
  77/33 e 777/333 devem ser invariantes para operador de razão
  sqrt(3)/2 != sqrt(3/2) != 3/2
  pentágono != pentagrama
  dodecágono != dodecagrama

TOKEN_VAZIO
  ligação física de z
  ligação cosmológica de escalares
  papel causal dos módulos
  base canônica de log(log(999))
  mapeamento físico G14 -> parâmetros RLL
```

Não foi inferida a causa "ignorado", "esquecido", "desprezado" ou
"menosprezado" sem evidência de processo. Quando a causa é desconhecida:

```text
CAUSA_DESCONHECIDA
```

## 12. Gate acadêmico anti-falso-positivo

Nenhum candidato originado por permutação avança somente porque:

- resulta em número pequeno;
- resulta em zero;
- aproxima outro escalar;
- compartilha dígitos;
- compartilha cardinalidade;
- fecha uma órbita modular;
- possui aparência geométrica semelhante.

Para promoção, exigir conforme aplicável:

```text
fonte congelada
definição antes do resultado
domínio e unidade
covariância
controle negativo
correção de multiplicidade ou teste omnibus
holdout
efeito + incerteza
reprodução independente
```

O fato de existirem milhares de combinações torna o controle de multiplicidade
mais importante, não menos.

## 13. Executável

```bash
python tools/rll_full_permutation_void_census_v1.py
python -m unittest tests.test_rll_full_permutation_void_census_v1 -v
```

O executor não despeja todas as 5328 combinações no repositório; ele as gera
deterministicamente. Isso preserva auditabilidade sem inflar o corpus.

## R3

```text
F_ok =
  sessão consolidada; 37 átomos tipados; 5328 candidatos binários;
  111 unários; 315 modulares; zero/vazio separados; geometrias e
  identidades preservadas; aproximações não promovidas

F_gap =
  significados físicos, causalidade cosmológica, unidade de z e vínculos
  observacionais permanecem TOKEN_VAZIO; "ignorado/esquecido" não pode ser
  inferido como causa sem evidência

F_next =
  executar CI do censo; depois usar equivalência/near-duplicate clustering
  para reduzir milhares de candidatos a classes independentes antes de
  qualquer teste observacional, evitando multiplicidade artificial
```
