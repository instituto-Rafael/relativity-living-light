# RLL — Famílias de Conjuntos, Números, Primos, Grafos e Fluidos V1

**Data:** 2026-10-04  
**Estado:** `FORMAL_FAMILY_BRIDGE / APPEND_ONLY / claim_allowed=false`  
**Escopo:** censo limitado da interação corrente + fontes já ancoradas.  
**Pai:** `RLL_FULL_PERMUTATION_VOID_CENSUS_V1.md`.

## 0. Contrato

Este documento transforma o censo de números, bases, resíduos, geometrias,
radicais e vazios tipados em famílias matemáticas executáveis.

A fronteira permanece:

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
FORMAL_IDENTITY != PHYSICAL_BINDING
GRAPH_FLOW != CONTINUUM_FLUID
DECIMAL_PERIOD != COSMOLOGICAL_PERIOD
```

O objetivo não é provar uma física por coincidência. O objetivo é fazer a
estrutura ficar suficientemente explícita para que identidades, aproximações,
contradições e lacunas possam ser reproduzidas e falsificadas.

Implementação:

```text
tools/rll_family_theory_bridge_v1.py
tests/test_rll_family_theory_bridge_v1.py
schemas/rll_family_theory_bridge_v1.schema.json
data/epistemic_void/rll_family_theory_bridge_v1.json
```

## 1. Resposta curta à pergunta "já dá para fazer as teorias?"

### 1.1 Teoria de conjuntos

**Sim, no carrier finito declarado.**

Podemos definir conjuntos de primos, compostos, representações, radicais,
classes de resíduos e estados de vazio. Também podemos executar união,
interseção, diferença, produto cartesiano, partições por equivalência modular e
relações de inclusão.

Isto não significa que o corpus inteiro foi reduzido a uma teoria axiomática
nova de conjuntos. Significa que esta família já pode usar teoria de conjuntos
padrão de maneira formal e verificável.

### 1.2 Teoria dos números

**Sim.**

Já temos divisibilidade, fatoração, gcd/lcm, repdigits, repunits, sistemas de
numeração, congruências, ordem multiplicativa e CRT.

### 1.3 Teoria dos primos

**Sim, como teoria dos números aplicada ao conjunto selecionado de primos.**

Os primos deste carrier são:

```text
P = {2,3,5,7,11,13,37}
```

Podemos medir fatoração, incidência em compostos e comprimento de ciclos da base
10 por ordem multiplicativa quando `gcd(10,p)=1`.

### 1.4 Teoria de grafos

**Sim.**

Há pelo menos três grafos naturais e não-metafóricos:

1. grafo funcional das recorrências de restos;
2. grafo bipartido número composto ↔ fator primo;
3. grafo de Cayley dos grupos aditivos modulares.

Além disso, fluxos orientados podem ser tratados por balanço em nós.

### 1.5 Fluidos

**Parcialmente, com a fronteira física explícita.**

As equações padrão de continuidade, Bernoulli e Venturi podem ser implementadas
e testadas sob seus pressupostos. O projeto já preserva uma fronteira semelhante:
continuidade e Bernoulli são formais, enquanto a ligação de resíduos DESI a um
estado de fluido exige geometria, identidade do fluido, unidades, condições de
contorno, viscosidade, temperatura, covariance e falsificador.

Portanto:

```text
FLUID_MATH = FORMAL_UNDER_ASSUMPTIONS
RLL_PHYSICAL_FLUID_BINDING = TOKEN_VAZIO_FLUID_BINDING
```

---

# PARTE I — TEORIA DE CONJUNTOS

## 2. Objetos tipados antes de cardinalidade

Uma distinção central desta sessão é:

```text
objeto != cardinalidade(objeto)
```

O conjunto vazio possui:

\[
|\varnothing|=0,
\]

mas:

\[
\varnothing \neq 0.
\]

Da mesma forma, uma classe de resíduos:

\[
[0]_m=\{km:k\in\mathbb Z\}
\]

não é vazia. Para `m=7`:

\[
[0]_7=\{\ldots,-14,-7,0,7,14,\ldots\}.
\]

Logo:

```text
RESIDUE_ZERO != EMPTY_SET
NUMERIC_ZERO != EMPTY_SET
NUMERIC_ZERO != NULL_VALUE
NUMERIC_ZERO != TOKEN_VAZIO
```

## 3. Carriers principais

O executor define, entre outros:

```text
P = conjunto dos primos selecionados
I = conjunto dos átomos inteiros
C = conjunto dos inteiros compostos
R = nomes dos radicais
V = tipos de vazio
```

Como cada primo selecionado é um átomo inteiro:

\[
P\subset I.
\]

Isto é uma relação de inclusão real. Não é uma analogia.

## 4. Operações de conjunto

Para carriers finitos `A` e `B` temos:

\[
A\cup B,
\qquad A\cap B,
\qquad A\setminus B,
\qquad B\setminus A,
\]

além do produto cartesiano:

\[
A\times B.
\]

No finito:

\[
|A\times B|=|A||B|.
\]

Esse produto é o protótipo set-theoretic para coordenadas coexistentes.

## 5. Relações de equivalência modular

Para módulo `m`:

\[
a\sim_m b\iff a\equiv b\pmod m.
\]

Isso particiona os inteiros em classes de equivalência.

Por exemplo, no conjunto finito `{0,1,2,3,4,5,6}` modulo 3:

```text
[0] -> {0,3,6}
[1] -> {1,4}
[2] -> {2,5}
```

O resíduo `0` é uma classe legítima da partição.

---

# PARTE II — TEORIA DOS NÚMEROS E BASES

## 6. Número, palavra e representação

A palavra `10` depende da base:

\[
10_b=b_{10}.
\]

Portanto:

```text
10_10 = 10
10_7  = 7
```

O dígito `0` nessa palavra é uma posição com coeficiente zero. Não é nulidade
semântica.

A regra geral de uma palavra posicional é:

\[
(d_k\ldots d_1d_0)_b
=\sum_{j=0}^{k} d_j b^j.
\]

## 7. Repdigits

Para o dígito `d` repetido `n` vezes na base `b`:

\[
D_{d,n}^{(b)}
=d\sum_{k=0}^{n-1}b^k
=d\frac{b^n-1}{b-1}.
\]

Na base 10:

\[
D_{7,n}=7\frac{10^n-1}{9},
\qquad
D_{3,n}=3\frac{10^n-1}{9}.
\]

Dividindo:

\[
\frac{D_{7,n}}3
=\frac{7(10^n-1)}{27},
\]

\[
\frac{D_{3,n}}7
=\frac{10^n-1}{21}.
\]

O `21=3*7` aparece exatamente na segunda família.

## 8. Repunits

Defina:

\[
R_n=\frac{10^n-1}{9}.
\]

Para seis dígitos:

\[
R_6=111111.
\]

E a fatoração exata é:

\[
\boxed{111111=3\cdot7\cdot11\cdot13\cdot37}.
\]

Também:

\[
1001=7\cdot11\cdot13.
\]

Isto cria uma relação estrutural legítima entre os primos `7,11,13` na base 10,
sem inferir significado físico.

## 9. Fatorações dos moldes principais

```text
18 = 2 * 3^2
21 = 3 * 7
42 = 2 * 3 * 7
77 = 7 * 11
333 = 3^2 * 37
777 = 3 * 7 * 37
999 = 3^3 * 37
1001 = 7 * 11 * 13
111111 = 3 * 7 * 11 * 13 * 37
```

Essas fatorações alimentam diretamente o grafo de incidência da Parte IV.

---

# PARTE III — PRIMOS, CICLOS E CRT

## 10. Ordem multiplicativa da base

Se:

\[
\gcd(b,m)=1,
\]

a ordem multiplicativa é o menor `k>0` tal que:

\[
b^k\equiv1\pmod m.
\]

Ela mede o fechamento da órbita multiplicativa da base no módulo.

Para os primos selecionados na base 10:

```text
p=2  -> ordem não definida, gcd(10,2)!=1
p=3  -> ord_3(10)=1
p=5  -> ordem não definida, gcd(10,5)!=1
p=7  -> ord_7(10)=6
p=11 -> ord_11(10)=2
p=13 -> ord_13(10)=6
p=37 -> ord_37(10)=3
```

Isso explica aritmeticamente os comprimentos de vários repetendos decimais.

### 10.1 O 7

\[
\operatorname{ord}_7(10)=6.
\]

Logo:

\[
\frac17=0.\overline{142857}.
\]

E:

\[
\frac37=0.\overline{428571}.
\]

### 10.2 O 11

\[
\operatorname{ord}_{11}(10)=2.
\]

Logo:

\[
\frac1{11}=0.\overline{09}.
\]

### 10.3 O 13

\[
\operatorname{ord}_{13}(10)=6.
\]

Logo existe um ciclo decimal de seis posições.

### 10.4 O 37

\[
\operatorname{ord}_{37}(10)=3.
\]

Isso conecta o fator `37` às estruturas repunit de período múltiplo de 3.

## 11. CRT: coexistência de eixos residuais

Como `3` e `7` são coprimos:

\[
\boxed{\mathbb Z_{21}\cong\mathbb Z_3\times\mathbb Z_7}.
\]

Cada classe modulo 21 possui coordenadas:

\[
x\mapsto(x\bmod3,x\bmod7).
\]

Como `2,3,7` são par-a-par coprimos:

\[
\boxed{\mathbb Z_{42}\cong
\mathbb Z_2\times\mathbb Z_3\times\mathbb Z_7}.
\]

Isto formaliza a noção de eixos modulares coexistindo. A interpretação física
desses eixos continua aberta.

---

# PARTE IV — TEORIA DE GRAFOS

## 12. Grafo funcional da família 7...7 / 3

A recorrência dos restos é:

\[
T_3(r)=10r+7\pmod3=r+1\pmod3.
\]

O grafo funcional completo é:

```text
0 -> 1
1 -> 2
2 -> 0
```

Logo existe um único 3-ciclo:

\[
(0,1,2).
\]

O vértice `0` está no ciclo. Não está ausente.

## 13. Grafo funcional da família 3...3 / 7

A recorrência é:

\[
T_7(r)=10r+3\pmod7=3r+3\pmod7.
\]

No conjunto completo de sete resíduos:

```text
0 -> 3 -> 5 -> 4 -> 1 -> 6 -> 0
2 -> 2
```

Portanto o grafo decompõe-se em:

\[
\boxed{
C_6\;\sqcup\;C_1
}
\]

com um ciclo dirigido de seis estados e um ponto fixo.

Esse resultado é mais forte do que observar apenas os dígitos `428571`: ele
expõe o operador e toda a dinâmica finita.

## 14. Grafo bipartido número ↔ primo

Defina dois tipos de vértice:

```text
N = números compostos / apresentações
P = fatores primos
```

Crie uma aresta `n -- p` quando `p | n`.

Exemplos:

```text
21 -- 3
21 -- 7
42 -- 2
42 -- 3
42 -- 7
77 -- 7
77 -- 11
1001 -- 7
1001 -- 11
1001 -- 13
```

Esse grafo preserva a proveniência de fatoração que a fração reduzida poderia
esconder.

## 15. Grafo de Cayley aditivo

Em `Z_m`, usando passo `s`:

\[
r\mapsto r+s\pmod m.
\]

Se:

\[
\gcd(s,m)=1,
\]

o passo gera todos os vértices e temos um ciclo de comprimento `m`.

Para `Z_7` e passo 1:

```text
0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 0
```

É um carrier aritmético. Não é uma órbita física automaticamente.

## 16. Invariantes de grafo

Para um grafo não orientado finito, o executor calcula:

```text
V = número de vértices
E = número de arestas
C = número de componentes conexas
beta1 = E - V + C
```

`beta1` aqui é a dimensão do espaço de ciclos do grafo; não deve ser confundido
com uma quantidade cosmológica só por compartilhar notação.

---

# PARTE V — GEOMETRIA E RADICAIS

## 17. Moldes regulares

O carrier regular usa:

\[
\theta=\frac{2\pi k}{n},
\qquad
c=2R\sin\frac{\pi k}{n}.
\]

Distingue-se:

```text
{5/1}  pentágono
{5/2}  pentagrama
{12/1} dodecágono
{12/5} dodecagrama conectado
```

Mesma cardinalidade de vértices não significa mesma aresta nem mesmo grafo.

## 18. Escalares e inversões

Permanecem exatas:

\[
\frac{\sqrt\pi}{\pi}=\frac1{\sqrt\pi},
\]

\[
\sqrt{\frac\phi\pi}\sqrt{\frac\pi\phi}=1.
\]

E permanecem diferentes:

\[
\frac{\sqrt3}{2}
\neq
\sqrt{\frac32}
\neq
\frac32.
\]

A proximidade:

\[
\frac{\sqrt5}{\pi}
\approx
\sqrt{\frac\phi\pi}
\]

é registrada como controle de proximidade, não identidade.

---

# PARTE VI — FLUIDOS

## 19. Continuidade em 1D

A conservação de massa em um escoamento estacionário unidimensional pode ser
escrita:

\[
\dot m=\rho A v.
\]

Entre duas seções:

\[
\rho_1A_1v_1=\rho_2A_2v_2.
\]

Se a densidade for constante:

\[
A_1v_1=A_2v_2.
\]

O executor oferece um residual:

\[
R_c=\rho_1A_1v_1-\rho_2A_2v_2.
\]

`R_c=0` significa conservação no modelo declarado. Não significa dado ausente.

## 20. Bernoulli

Sob as hipóteses adequadas de escoamento ideal ao longo de uma linha de corrente:

\[
P+\frac12\rho v^2+\rho gh=\text{constante}.
\]

O executor calcula cada termo como densidade de energia/pressão.

Isto não autoriza ignorar:

- viscosidade;
- perdas de carga;
- compressibilidade;
- choques;
- bombas/turbinas;
- aquecimento;
- mudanças não estacionárias;
- geometria tridimensional relevante.

## 21. Venturi ideal de mesma altura

Para `A1>A2>0`, densidade constante, ausência de perdas e mesma altura:

\[
Q=A_1A_2
\sqrt{
\frac{2\Delta P}
{\rho(A_1^2-A_2^2)}
}.
\]

Então:

\[
v_1=Q/A_1,
\qquad
v_2=Q/A_2.
\]

O teste executável verifica simultaneamente:

```text
A1*v1 = A2*v2
DeltaP = 0.5*rho*(v2^2-v1^2)
Bernoulli_1 = Bernoulli_2
```

para um fixture ideal declarado.

## 22. Reynolds

O executor também calcula:

\[
Re=\frac{\rho |v|D}{\mu}.
\]

Ele deliberadamente não promove sozinho o valor a "laminar" ou "turbulento",
porque limites dependem de geometria, perturbações, rugosidade e regime.

## 23. Gate físico de fluido

Para sair de `TOKEN_VAZIO_FLUID_BINDING`, o contrato exige no mínimo:

```text
geometry
fluid_identity
density
viscosity
temperature
compressibility_regime
units
boundary_conditions
measurement_source
uncertainty
covariance_or_error_model
falsifier
```

Ter todos esses campos apenas move o estado para:

```text
READY_FOR_PHYSICAL_TEST
```

Não para `CLAIM_PASS`.

---

# PARTE VII — A PONTE GRAFO ↔ FLUXO

## 24. Conservação discreta

Considere um grafo dirigido `G=(V,E)` e um fluxo escalar `q_e` em cada aresta.

No nó `v`, defina:

\[
b(v)=\sum_{e\to v}q_e-\sum_{e\leftarrow v}q_e.
\]

Então:

```text
b(v)=0 -> nó conservativo
b(v)>0 -> sumidouro líquido / acumulação conforme contrato
b(v)<0 -> fonte líquida / emissão conforme contrato
```

O caso `b(v)=0` é particularmente importante nesta sessão:

```text
BALANCE_ZERO != MISSING_FLOW
```

Exemplo implementado:

```text
inlet -> junction : 2.00
junction -> out_a : 0.75
junction -> out_b : 1.25
```

No `junction`:

\[
2.00-0.75-1.25=0.
\]

O nó existe, as três arestas existem, os fluxos existem e o balanço é zero.
Nada foi apagado.

## 25. Forma matricial

Se `B` é a matriz de incidência orientada e `q` o vetor de fluxos:

\[
Bq=s,
\]

onde `s` registra fontes/sumidouros externos segundo a convenção de sinal.

Nos nós internos conservativos:

\[
s_i=0.
\]

Novamente, zero significa uma restrição satisfeita, não ausência de observação.

Esta é a ponte mais rigorosa entre teoria de grafos e conservação de fluidos
desta etapa.

---

# PARTE VIII — FAMÍLIAS DE SITUAÇÕES

## 26. Catálogo completo do escopo atual

### SET-01 — conjuntos

**Situações:** inclusão, interseção, união, diferença, produto cartesiano,
cardinalidade, conjunto vazio, classes de equivalência.

**Estado:** `MATH_FORMAL`.

### NUM-01 — números

**Situações:** inteiros, racionais, irracionais, radicais, divisibilidade,
fatoração, gcd/lcm, repdigits e repunits.

**Estado:** `MATH_FORMAL`.

### PRIME-01 — primos

**Situações:** primalidade, fatores, ordem multiplicativa, fatores de repunits,
incidência primo↔composto.

**Estado:** `MATH_FORMAL`.

### BASE-01 — bases

**Situações:** palavra posicional, mudança de base, significado de `10_b`,
distinção valor↔representação.

**Estado:** `MATH_FORMAL`.

### MOD-01 — módulos

**Situações:** resíduo, resíduo zero, ciclos, assinaturas multi-modulares,
fase `2*pi*r/m`.

**Estado:** `MATH_FORMAL`.

### CRT-01 — coexistência residual

**Situações:** decompor uma classe em coordenadas coprimas e reconstruí-la.

**Estado:** `MATH_FORMAL`.

### GRAPH-01 — grafos funcionais

**Situações:** recorrências determinísticas, ciclos, pontos fixos, basins.

**Estado:** `MATH_FORMAL`.

### GRAPH-02 — grafos de fatores

**Situações:** números de um lado, fatores primos do outro, arestas por
divisibilidade.

**Estado:** `MATH_FORMAL`.

### GRAPH-03 — Cayley/modular

**Situações:** deslocamentos aditivos em `Z_m`, ciclos geradores.

**Estado:** `MATH_FORMAL`.

### GEOM-01 — geometria regular

**Situações:** polígonos, estrelas, cordas, semiângulos, pentagrama,
dodecagrama.

**Estado:** `MATH_FORMAL`.

### RAD-01 — radicais e razões

**Situações:** raiz, inverso, razão, par recíproco, proximidade numérica,
identidade exata.

**Estado:** `MATH_FORMAL`.

### VOID-01 — vazio tipado

**Situações:** zero numérico, zero residual, empty set, null, undefined,
no-real-solution, missing observation, not applicable, approx-zero,
TOKEN_VAZIO.

**Estado:** `MATH_FORMAL` no contrato semântico.

### FLUID-01 — continuidade

**Situações:** fluxo mássico, igualdade entre seções, residual de conservação.

**Estado:** `FORMAL_UNDER_ASSUMPTIONS`.

### FLUID-02 — Bernoulli/Venturi

**Situações:** troca pressão↔velocidade↔altura em regime ideal declarado.

**Estado:** `FORMAL_UNDER_ASSUMPTIONS`.

### FLUID-03 — fluxo em grafo

**Situações:** balanço por nó, fonte, sumidouro, conservação, incidência.

**Estado:** `MATH_FORMAL` como sistema discreto.

### RLL-01 — ligação física

**Situações:** usar qualquer família anterior como observável/covariante físico.

**Estado:** `TOKEN_VAZIO` até contrato físico e evidência independente.

---

# PARTE IX — CONTRADIÇÕES E FALSIFICADORES

## 27. Gates negativos obrigatórios

Uma estrutura falha como invariante robusta se depender apenas de:

1. forma decimal específica quando a razão é a mesma;
2. escolha de base não preregistrada;
3. substituição `sqrt(3)/2 -> sqrt(3/2) -> 3/2`;
4. confusão entre polígono e estrela;
5. proximidade numérica tomada como igualdade;
6. zero usado para preencher dado ausente;
7. módulo escolhido depois de observar o resultado;
8. múltiplos resíduos dependentes tratados como testes independentes;
9. equação de fluido usada sem domínio físico declarado;
10. fluxo conservado em grafo chamado de evidência de fluido cosmológico.

## 28. Proveniência do fator 11

A redução:

\[
77/33=7/3
\]

preserva valor racional, mas o `gcd=11` é proveniência da apresentação.

Da mesma forma:

\[
777/333=7/3
\]

com `gcd=111`.

Uma função que depende apenas do valor racional deve satisfazer:

\[
F(77,33)=F(777,333)=F(7,3).
\]

Se não satisfizer, ela mede apresentação, dígitos ou escala comum, não apenas a
razão.

---

# PARTE X — EXECUÇÃO E GATES

## 29. Comandos

```bash
python tools/rll_family_theory_bridge_v1.py
python -m unittest tests.test_rll_family_theory_bridge_v1 -v
```

Além disso permanecem válidos:

```bash
python tools/rll_full_permutation_void_census_v1.py
python -m unittest tests.test_rll_full_permutation_void_census_v1 -v
python -m unittest tests.test_rll_repdigit_geometry_molds_v1 -v
```

## 30. O que pode PASS

Pode receber `PASS` formal, depois de execução correspondente:

- fatorações;
- relações de conjunto finitas;
- CRT;
- ciclos dos grafos funcionais;
- ordens multiplicativas;
- invariantes de grafos finitos;
- continuidade em fixtures construídos para satisfazê-la;
- Bernoulli/Venturi em fixture ideal e sob hipóteses explícitas;
- balanço conservativo em grafo.

## 31. O que não pode PASS por esse artefato

Este artefato não pode estabelecer:

- existência de um fluido cosmológico específico;
- que resíduos DESI sejam variáveis de fluido;
- que um primo tenha causalidade física;
- que `21`, `42`, `900900` ou outro período aritmético seja período natural;
- que proximidade entre radicais revele nova constante;
- que um grafo aritmético seja a topologia física do espaço-tempo;
- superioridade observacional do RLL.

Esses itens requerem outra cadeia de evidência.

## 32. Gate de promoção física

Para qualquer proposta `MATH -> RLL_PHYSICS` exigir:

```text
observable definition
units/dimensional analysis
source provenance
dataset + checksum
covariance/error model
boundary/initial conditions when relevant
baseline model
preregistered falsifier
held-out or independent evidence
reproduction
receipt
```

Sem isso:

```text
claim_allowed=false
```

---

## R3

```text
F_ok =
  teoria de conjuntos finita + números + primos + bases + modular + CRT +
  grafos funcionais/fatores/Cayley + geometria + radicais + vazio tipado +
  continuidade/Bernoulli/Venturi formal + fluxo conservativo em grafo foram
  transformados em contrato executável e testável

F_gap =
  identidade física do fluido, geometria contínua física, condições reais de
  contorno, medições, viscosidade/temperatura/regime completos, covariance e
  qualquer acoplamento causal ao RLL continuam TOKEN_VAZIO

F_next =
  CI -> classificação das equivalências/permutação por família -> somente após
  PASS preregistrar um binding observacional held-out; nenhum ajuste pós-hoc
  pode transformar coincidência matemática em mecanismo
```
