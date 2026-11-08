# RLL — Compensação algébrica, multibase e grade angular — V1

**Estado:** `RESEARCH / LOCAL_MATH_PASS_SCOPED / DRAFT_HOLD`.
**Autoria da composição:** proposição do usuário RAFAELIA Ω.
**Autoridade:** RLL é produtor da pesquisa e dos testes locais.
**Claim:** `claim_allowed=false`; `physical_model_validation=NOT_RUN`.

## 1. Intenção e limites

Construir uma ponte **exata, de baixo risco**, entre:

- a compensação por parcela/área auxiliar com sinal;
- a regra de multiplicação pelo 9 e generalização para `b−1`;
- o par 7/3, o levantamento escalado 70/30 e o alvo 100;
- a leitura multibase do mesmo numeral `50` nas bases 7, 10 e 14;
- as grades angulares 7, 10, 14, 35, 50 e 70;
- os estudos já existentes de RLL sobre razão exata, resíduos,
  geometria e estabilidade observacional.

Essas igualdades são matemáticas **clássicas**; a composição, a
parametrização e a custódia no projeto são a proposta autoral.
Não demonstram nova lei gravitacional, quântica ou cosmológica.

## 2. A área auxiliar é uma contabilidade exata

Se os lados são `a+u` e `a+v`, com `u,v` positivos ou negativos:

```text
(a+u)(a+v) = a² + a(u+v) + uv
```

Áreas com sinal podem representar complementações/subtrações.
A área "emprestada" não precisa existir como região física;
trata-se de adicionar e subtrair a mesma parcela na álgebra.

Exemplos **exatos**:

```text
7*13 = (10-3)(10+3) = 10²-3² = 100-9 = 91
13*17 = (15-2)(15+2) = 15²-2² = 225-4 = 221
x²-6x = (x-3)² - 9
9*n = 10*n-n
(b-1)*n = b*n-n                para b>=2
```

A simplificação é de representação. Não foi medido ganho de ciclos,
consumo de energia ou custo assintótico; tais claims ficam bloqueados.

## 3. Complemento e levantamento entre módulos

Para `0<=x<=b` e inteiro positivo `k`:

```text
C(x;b,k) = (k*x, k*(b-x), k*b)
C(7;10,10) = (70,30,100)
```

O mapeamento aditivo:

```text
L_k : Z/bZ → Z/(kb)Z
L_k([x]_b) = [k*x]_(kb)
```

é bem definido: se `x'=x+mb`, então `kx'=kx+mkb`.
É **injetivo e aditivo**. Ele **não preserva produtos** em geral:

```text
L_10([2*3]_10) = [60]_100
L_10([2]_10)*L_10([3]_10) = [20*30]_100 = [0]_100
```

Logo a frase "7 em mod 10 vira 70 em mod 100" admite uma
interpretação rigorosa **como levantamento aditivo escalado**,
mas não como conversão de numeral nem como isomorfismo de anéis.

## 4. Representação posicional versus valor inteiro

Um numeral de duas casas em base `b` tem valor `d1*b+d0`.
Se o mesmo numeral é `50`, seu valor decimal é `5b`:

| Escrita tipada | Valor decimal |
| --- | ---: |
| `(10)_7` | 7 |
| `(50)_7` | 35 |
| `(50)_10` | 50 |
| `(50)_14` | 70 |

`(70)_7` **é numeral inválido** porque 7 não é dígito permitido
na base 7. Multiplicar `7*10=70` muda o inteiro;
converter a escrita de 7 para outra base não muda o valor nem
sua primalidade. `7` continua primo; `70` é composto.

A raiz digital decimal é governada por módulo 9:

```text
dr_10(7,35,50,70) = (7,8,5,7)
```

Portanto esses quatro inteiros não têm automaticamente a mesma
raiz digital ou um ciclo Tesla 3–6–9 compartilhado.
Qualquer operador Tesla proposto precisa de definição e domínio.

## 5. Grade comum e coincidência angular, não momento físico

Defina pontos de uma partição de círculo:

```text
C_n = {exp(2*pi*i*j/n) | j=0..n-1}
|C_n ∩ C_m| = gcd(n,m)
< C_n ∪ C_m > = C_lcm(n,m)   (subgrupo gerado)
```

A notação `<...>` refere-se ao grupo cíclico gerado,
não à união literal de dois conjuntos, que pode ser menor.
Para `n={7,10,14,35,50,70}`, a supergrade mínima tem
**350 pontos**.

| Grades | Coincidências angulares |
| --- | ---: |
| `C_7` × `C_14` | 7 |
| `C_7` × `C_50` | 1 |
| `C_35` × `C_50` | 5 |
| `C_50` × `C_70` | 10 |
| `C_7` × `C_35` × `C_50` × `C_70` | 1 |

Em particular, as quatro grades da última linha só partilham
a fase de origem quando os índices são ancorados em zero.
Outro alinhamento exige offsets de fase explicitamente definidos.

A compatibilidade simultânea de resíduos `mod 14` e `mod 10`
obedece a uma forma do teorema chinês dos restos:

```text
Z/70Z ≅ (Z/14Z) ×_(Z/2Z) (Z/10Z)
```

Um par `(a mod14,b mod10)` corresponde a um inteiro mod70
**se e somente se** os dois resíduos têm a mesma paridade.

**Momento angular físico é outra grandeza**:
`L = r × p`, com unidades de `kg*m²/s`, enquanto a fase
`theta=2*pi*j/n` é adimensional. Para identificar rotações reais,
exigir massa, raio, inércia, eixo, período e dinâmica medidos.
`angular_momentum_evidence=TOKEN_VAZIO`.

## 6. Ponte com a estabilidade observacional e a RLL

As grades e operações algébricas podem ser instrumentos
**de indexação e cálculo**, mas não devem entrar como nova física
na função cosmológica `H(z)`, no potencial orbital, nas lentes
ou no espectro por mera semelhança geométrica.

A rota de integração é:

```text
fonte espectral / astrométrica / gravitação + unidade/covariância
  → ajuste físico e residual tipado r = y-h(x)
  → margem, tendência e verificação da estabilidade observacional
  → representação matemática multibase exata (opcional)
  → grade de fase / T7 com mapa explícito e teste de invariância
  → decisão RLL condicionada a CMB/BAO/SNe/CC e likelihood válida
```

O código de comparação não altera previsões físicas;
quantifica apenas que a decomposição algébrica é exata.
Em precisão finita (por exemplo Q16.16), compensações podem
mudar overflow e erro de arredondamento: precisam de oráculo
em inteiros e limites de saturação antes de portar a produção.

**Falsificador científico:** se cálculos transformados gerarem
resultados diferentes de uma implementação matematicamente
equivalente além da tolerância numérica, isso indica falha
numérica ou diferença de modelo; não uma nova força física.
**RLL cosmology:** CMB/growth/joint/observações reais `NOT_RUN`.

## 7. Evidência local e testes adversariais

O oráculo de referência stdlib em
`tools/rll_multibase_oracle_v1.py` e o teste em
`tests/test_rll_multibase_oracle_v1.py` têm **24 testes**
com casos paramétricos/exaustivos limitados:

- identidade de produto sob 3 âncoras e inteiros negativos;
- `C(7;10,10)=(70,30,100)` e complementos por bases;
- injeção/aditividade do lift e **contraexemplo de multiplicação**;
- numeral inválido `(70)_7` e `50` em 7/10/14;
- `C_n` por frações racionais e coincidências `gcd`;
- CRT paritário `mod14`/`mod10` sobre 70 resíduos;
- primos, raízes digitais, nove por complemento;
- falha explícita de alinhamento angular comum não trivial.

**Resultado host local:** `24/24 PASS_SCOPED` (Python stdlib).
`CI_EXACT_HEAD=TOKEN_VAZIO` até consultar provider pós-commit.
`PERFORMANCE_GAIN=TOKEN_VAZIO`; `PHYSICAL_EVIDENCE=NOT_RUN`.
`NEW_THEOREM_NOVELTY=NOT_CLAIMED`.

## 8. Proveniência e rotas (sem copiar corpus)

- Antecessor RLL:
  `PapersPub/2026-08-29_RAFAELIAN_EXACT_RATIO_GEOMETRY_SESSION_FEEDBACK.md`
- Modelo estatístico RLL:
  `docs/science/RLL_MULTISCALE_HETEROGENEOUS_RESIDUAL_GEOMETRY_V1.md`
- Mundo geométrico: Drive `SESSÃO — SOBREPOSIÇÃO ANGULAR, √3/2
  E GEODÉSICA — V1 — 2026-09-21`; grade `gcd/lcm`.
- Produtor matemático:
  `rafaelmeloreisnovo/Matem-tica-`, notas sobre representação
  de base e `INVERSE_REVERSE_ANTIDERIVATIVES_EXPLORER_20261023`.
- Estabilidade física: `rafaelmeloreisnovo/papers` PR #156,
  V1 T7 e V2 observacional (DRAFT/HOLD, sem dados reais).
- Pesquisa bibliográfica: Science X V4 568 registros no Atlas,
  referências primárias preservadas como agenda, não como prova.

## 9. Fechamento e reversibilidade

**SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM.**
Não renomear funções de física, não mexer em likelihood ou CI,
não aplicar alterações na `main` sem gates do produtor.
`claim_allowed=false`; `merge_allowed=false`; `rollback=close_draft`.

**R3:** identidade algébrica validada em escopo finito;
sem medida de ganho computacional nem validação cosmológica;
seguir para calibração e comparações físicas independentes.
