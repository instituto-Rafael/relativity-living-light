# RLL Ω — Complementos multibase, resíduos e testes falsificáveis

**Estado:** formalização matemática aditiva. Esta nota **não** transforma o atlas `AX-F-*` já existente nem modifica os resultados adversos históricos do RLL.

## Origem e ligação

- Atlás falsificável sucessor: [27 itens AX-F](../../data/contracts/rll_cross_domain_falsification_atlas.v1.json); predecessores `AX-F-MAT-03` e `AX-F-MAT-05`.
- Ponte modular/geodésica anterior: [Ω7](OMEGA7_MODULAR_GEODESIC_TOROIDAL_FOCUS_20260818.md).
- Comparação real de representações 5-bit/6-bit: [Telex e Braille](../../NOVOexport/LOW_LEVEL_TEXT_ENCODING/TELEX_5BIT_FIXED_WINDOW_20261108/README.md).
- Schema canônico desta extensão: [rll_multibase_complement_falsification.v1.json](../../data/contracts/rll_multibase_complement_falsification.v1.json).

## Princípio de conservação

`valor_inteiro != escrita_posicional != resto_modular != escalar_multiplicativo != valor_físico`.
`zero_modular != TOKEN_VAZIO`: número `7` escrito na base 7 é `10_7` — não `07_7`, pois 7 não é um dígito válido nessa base. `7 mod 7=0` é um **resto** conhecido, e o par `(quociente=1, resto=0)` reconstrói o sete.

No alfabeto de base 100, escrevemos os dígitos entre colchetes para não confundir o **dígito de valor 70** `[70]_100` com a sequência de dois dígitos `[7,0]_100=700_10`.

```text
7_10     = 10_7        = [7]_100
7*10     = 70_10       = [70]_100 = 130_7
3*10     = 30_10       = [30]_100
70+30    = 100_10      = [1,0]_100
7*70     = 490_10      = [4,90]_100 = 1300_7
7*70     = (7+3)*70 - 3*70 = 700 - 210 = 490
Signed area: ab=(a+c)(b+d)-ad-cb-cd
```

## Atlas de proposições e contraprovas

| ID | Tipo | Tese / hipótese | Critério de teste ou refutação | Estado |
|---|---|---|---|---|
| MB7-01 | IDENTIDADE | 7(decimal)=10(base7)=[7](base100) | converter e reconstruir; qualquer diferença reprova | PROVAVEL_FORMAL |
| MB7-02 | REGRA_SINTATICA | 07 não é numeral posicional válido na base 7 | parser restrito base7 precisa rejeitar algarismo 7 | PROVAVEL_FORMAL |
| MB7-03 | RESIDUO | 7 mod 7=0 e divmod(7,7)=(1,0), zero conhecido ≠ valor ausente | demonstração divisão euclidiana; parser nulo distinto do resto | PROVAVEL_FORMAL |
| MB7-04 | NAO_INJETIVIDADE | Só o resto 0 mod7 não reconstrói 7,14,21; o quociente é necessário | colisão r(7)=r(14)=0 | PROVAVEL_FORMAL |
| MB7-05 | COMPLEMENTO | (7+3)*10=70+30=100, com escalas declaradas | teste aritmético inteiro exato | PROVAVEL_FORMAL |
| MB7-06 | VAI_UM_BASE100 | [70]_100+[30]_100=[1,0]_100, com dígito 70 como símbolo unitário | somar e reconstruir valor decimal | PROVAVEL_FORMAL |
| MB7-07 | MULTIPLICACAO | 7*70=490_10=[4,90]_100=1300_7 | mesmo inteiro reconstruído em todas as bases | PROVAVEL_FORMAL |
| MB7-08 | PRIMALIDADE | Trocar de base preserva primalidade do valor 7; multiplicar por 10 cria 70, composto | divisibilidade do valor não é dependente da escrita | PROVAVEL_FORMAL |
| MB7-09 | COMPENSACAO | (a+c)*b-c*b=a*b para inteiros assinados | verificar identidade distributiva e overflow em representações limitadas | PROVAVEL_FORMAL |
| MB7-10 | AREA_ASSINADA | (a+c)(b+d)-ad-bc-cd=ab para inteiros | expandir polinômio e cancelar as três parcelas extras | PROVAVEL_FORMAL |
| MB7-11 | CAMBIO_BASE_E_REM | Para b>1: n=b*floor(n/b)+(n mod b), 0≤r<b, inclusive n=0 | sweep exato multibase, 0 não é TOKEN_VAZIO | PROVAVEL_FORMAL |
| MB7-12 | ANGULO_MODULAR | Sob θ=2π(n mod b)/b, 7,35,50,70 têm o mesmo ângulo em b=7,10,14 | comparar resíduos em cada base; já falha na base7 para 50 | REFUTADA_CONTRAPROVA |
| MB7-13 | ANGULO_VS_FISICA | Coincidência do resíduo modular determina momento angular físico igual | escolher mesmo índice modular, mas momenta diferentes: r×p | REFUTADA_CONTRAPROVA |
| MB7-14 | REPETENDO | 1/7 é periódico em base10 (142857), mas finito em base7 (0.1_7) | divisão racional/repetendo; valor 1/7 invariável | PROVAVEL_FORMAL |
| MB7-15 | DIGITO_SOMA | Σ dígitos de n em base b ≡ n mod (b-1), para b≥2 | congruência com b≡1 mod(b−1) | PROVAVEL_FORMAL |
| MB7-16 | OTIMIZACAO | Complementação reduz operações/latência de multiplicações arbitrárias com primos | comparar mesmo inteiros, instruções, temporários, overflow, latência e mediana com controle | HIPOTESE_BENCHMARK |
| MB7-17 | COMPRESSAO | Mudar base e empacotar dígitos sempre comprime mais o texto-fonte | inclua tabela e escapes; comparação Braille 6 bits vs 5 bits em janelas iguais | REFUTADA_CONTRAPROVA_LOCAL |
| MB7-18 | GEOMETRIA_FISICA | Representação modular multibase prediz novas órbitas ou conservação angular física | exigir mapa dimensional, estado, modelo dinâmico, observáveis e previsão fora da amostra | TOKEN_VAZIO_FISICA |
| MB7-19 | REPRESENTACAO_07 | [0,7]_100 e [7]_100 têm mesmo valor 7, mas [7,0]_100 vale 700 | testar dígitos posicionais e zeros à esquerda, sem ambiguidade | PROVAVEL_FORMAL |
| MB7-20 | ESCALA_GERAL | x+k=B ⇒ tx+tk=tB, mas isso não implica que x=tx | demonstrar conservação e distinção de escala com t>1 | PROVAVEL_FORMAL |

### Matriz angular adimensional — não confundir com momento angular físico

Para a definição **escolhida** `theta_b(n)=2π*(n mod b)/b`, os restos são:

| Base | 7 | 35 | 50 | 70 |
|---|---:|---:|---:|---:|
| 7 | 0 | 0 | 1 | 0 |
| 10 | 7 | 5 | 0 | 0 |
| 14 | 7 | 7 | 8 | 0 |

Logo, a proposição de que os quatro números sempre têm a mesma fase nessa definição é **refutada por contraprova exata**. Essa contraprova não impede explorar outra projeção angular, desde que o mapa seja definido **antes** de olhar o resultado. Não autoriza a inferência de momento angular físico `L=r×p` sem posição, momento, unidade e modelo.

### Provas vs conjecturas vs hipóteses empíricas

- Identidade e regra posicional: um contraexemplo computável dentro das hipóteses refuta uma afirmação **falsa**, mas o teste finito não substitui uma demonstração para todos os inteiros.
- Eficiência e compressão: testáveis empiricamente com protocolos e corpus de valores congelados, contagem de operações e custo das tabelas. Ganho só em um exemplo não demonstra otimização universal.
- Física: a mudança de base numérica não altera a gravidade. Para ligar aritmética modular à órbita ou estabilidade RLL, precisamos de mapa dimensional, condições, equações, comparação de hipóteses e dados fora da amostra.

## Execução de verificação formal

`python3 tests/test_rll_multibase_complement_falsification_v1.py` — 20 testes stdlib. Inclui sweep de números em bases 7/10/14/100, correção de empréstimo para operandos assinados, repetendo e quadrinhos `[70]` vs `[7,0]`.

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`; `claim_allowed=false`; `merge_allowed=false`. Testes formais não executam G4/G5, não medem cosmologia e não autorizam física nova. Rollback: reverter somente este commit aditivo ou fechar a PR #1169 sem merge.