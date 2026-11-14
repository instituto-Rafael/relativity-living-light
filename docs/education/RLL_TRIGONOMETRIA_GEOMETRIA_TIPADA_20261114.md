# RLL Ω — Trigonometria, geometria tipada e limites de interpretação científica

**Estado:** `STANDARD_IDENTITIES + MATHEMATICAL_DERIVATIONS + DRAFT_HOLD` (nenhuma alegação de inovação global). **claim_allowed=false**. **Origem:** discussão RAFAELIA Ω sobre equilátero, rotações, vetores com proveniência, polígonos, `12^n`, doze marcadores, grafos e `T^7` em 2026-11-14. Complemento da [escola dos sete mestres](RLL_SETE_MESTRES_PARABOLAS_GEOMETRIA_20261114.md).

## A. Triângulo equilátero de lado `a`

A altura divide a base em dois catetos `a/2` e `h`, com hipotenusa `a`. Por Pitágoras:

```math
h^2 + (a/2)^2=a^2,\qquad
h=(\sqrt{3}/2)a.
```

Para `a=1`, `h=\sqrt3/2`. A metade do equilátero possui ângulos `30°,60°,90°` e razões `1:\sqrt3:2` (após dividir todos os lados por `a/2`).

| θ | sen θ | cos θ | tan θ |
| --- | --- | --- | --- |
| 30° | 1/2 | √3/2 | 1/√3 |
| 45° | √2/2 | √2/2 | 1 |
| 60° | √3/2 | 1/2 | √3 |

No equilátero, **a partir do mesmo vértice**, altura, mediana e bissetriz coincidem com a reta mediatriz do lado oposto. São quatro propriedades da mesma reta, não quatro vetores de deslocamento independentes.

## B. Trigonometria vetorial e transformações

```math
P(\theta)=(\cos\theta,\sin\theta),\qquad
\sin^2\theta+\cos^2\theta=1.
```

```math
R_\varphi=
\begin{pmatrix}
\cos\varphi&-\sin\varphi\\
\sin\varphi&\cos\varphi
\end{pmatrix},\qquad
R_\varphi^{\mathsf T}R_\varphi=I.
```

A rotação conserva distância e norma; a escala `S=2I` dobra comprimentos. Uma reflexão em uma reta também é isometria, mas não equivale em geral à inversão central `v↦−v`.

Para vértices posicionados por `P:V→ℝ^d` e uma **ocorrência** orientada `e=(id,origem,destino,parent,camada,operação)`:
```math
\mathrm{vec}(e)=P(destino)-P(origem).
```
A inversão `J(e)` troca os extremos, preserva um vínculo `parent(J(e))=id(e)` e tem novo ID:
```math
\mathrm{vec}(J(e))=-\mathrm{vec}(e),\quad
\|\mathrm{vec}(J(e))\|=\|\mathrm{vec}(e)\|.
```
**Não** se iguala o objeto inteiro `J(e)` a `−e`; o sinal atua no deslocamento, não nos metadados. Dupla inversão recupera o deslocamento original, mas duas ocorrências derivadas não recuperam automaticamente o ID histórico inicial.

**Ordem importa:** para projeção `Q(x,y,z)=(x,y,0)` e rotação `A(x,y,z)=(z,y,-x)`, o vetor `v=(1,0,0)` satisfaz `Q(A(v))=(0,0,0)` mas `A(Q(v))=(0,0,-1)`. Transformar e projetar em ordens diferentes pode produzir coincidências visuais artificiais. Essa demonstração não identifica, sem coordenadas, a causa dos esboços históricos.

## C. Raízes algébricas não são comprimentos sem contrato

```math
ax^2+bx+c=0,\ a\neq0,\quad
x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}.
```
Raiz real requer `D=b²−4ac≥0`; comprimento geométrico exige ainda `x≥0` e unidade. `|a-b|` mede diferença escalar entre dois valores; a hipotenusa, para catetos ortogonais, é `c=√(a²+b²)`. Diagonais do quadrado/cubo unitários são, respectivamente, `√2` e `√3`. `√(π/5)`, `√(π/12)` são escalares até definição de figura e unidade.

## D. Cordas, polígonos e divisões angulares

Para um polígono regular de `n≥3` lados inscrito em circunferência de raio `R`:
```math
\theta_n=2\pi/n,\quad
s_n=2R\sin(\pi/n),\quad
A_n=\frac n2 R^2\sin(2\pi/n).
```
Especialmente `s_{12}=2R\sin15°=R√(2−√3)`, `s_8=R√(2−√2)`. Dividir uma circunferência em 12 vértices permite selecionar triângulos (`k=0,4,8`), quadrados (`0,3,6,9`) e hexágonos (`0,2,4,6,8,10`) como subconjuntos de vértices do dodecágono ideal.

O fecho `∑(π−2π/n_i)=2π` de ângulos de polígonos regulares em torno de um vértice é **necessário**, não suficiente, para um ladrilhamento global. Precisam-se testes de comprimentos de arestas, ordem cíclica, não sobreposição e extensão.

O grupo diedral `D_{12}` age nos doze índices por `r(k)=k+1`, `s(k)=−k` módulo 12; `r^{12}=s^2=1`, `srs=r^{-1}`.

## E. Malhas `12^n`, áreas e topologia

Em uma subdivisão regular de um triângulo equilátero com `m` segmentos por lado, usando pequenas faces equiláteras:
```math
V=\frac{(m+1)(m+2)}2,\quad
E=\frac{3m(m+1)}2,\quad
F=m^2,\quad
V-E+F=1.
```
Se `m=12^j`, então `F=12^{2j}`; a soma das áreas mantém a área original sob partição sem lacunas e sobreposição.

**Um grafo sem faces e um complexo com faces preenchidas não têm a mesma homologia.** Para uma malha plana conectada com `F` faces internas triangulares, o grafo 1D pode ter `F` ciclos independentes; ao preencher todas as faces, esses ciclos deixam de representar `F` buracos topológicos. Representar o "vazio" requer tipo: `ABSENT`, `UNOCCUPIED`, `MISSING_EDGE`, `UNFILLED_FACE`, `UNKNOWN_EVIDENCE` e `NOT_RUN` não são intercambiáveis.

Contas discretas lembradas da sessão:
```text
12²=144; 12³=1728; 12⁷=35.831.808.
12×12×2×6×12×(-12)=-248.832.
144²−12×12+12³=22.320.
12⁷−12⁴=35.811.072.
```
Um índice ilimitado `n∈ℕ` em uma regra de refinamento não afirma infinitude física realizada.

## F. Doze marcadores anuais e `T^7`

Modelo ideal:
```math
\theta_k=\frac{2\pi k}{12},\quad k=0,\ldots,11;\qquad
\operatorname{oposto}(k)=(k+6)\bmod12.
```
Agrupar três marcadores por quadrante é convenção didática. Durações reais de estações e intervalos de tempo astronômico não são obrigados a ser iguais. Modelos astronômicos demandam inclinação, anomalia orbital, efemérides, latitude, época e observação.

`T^7=(S^1)^7` é um toro contínuo de sete fatores, não esfera `S^2` nem malha geodésica esférica. O grafo discreto `G=(C_{12})^{\square 7}` tem:
```text
|V|=12⁷=35.831.808
grau=14
|E|=7×12⁷=250.822.656
diâmetro=7×6=42
```
A contagem exata por distância a um vértice é codificada por
```math
D(z)=(1+2z+2z^2+2z^3+2z^4+2z^5+z^6)^7.
```
O número `42` neste grafo representa diâmetro, **não** prova 42 atratores físicos. Tampouco a discretização de `T^7` implica uma cosmologia observável.

## G. Contrato científico específico do RLL

As identidades acima oferecem **linguagem de parametrização, verificação e representação**, não uma equação observacional nova. Para qualquer ponte física:
```text
observável e unidade
  → dado independente + incerteza/covariância
  → predição física H(z) ou outra definida sem mudar hipóteses
  → residual e likelihood
  → comparação com modelos concorrentes e falsificadores
  → revisão de claim.
```

Uma função `r_i=y_i-f(x_i;\vartheta)` é um residual quando `y_i`, `f` e os parâmetros estão definidos e calibrados. A mera igualdade de uma grade angular ou constante não demonstra força, efeito cosmológico ou ganho de eficiência.

**Referências internas consultadas:** [Compensação angular e multibase](../science/RLL_COMPENSATION_MULTIBASE_ANGULAR_V1.md), [Calendário e calibração astronômica](../science/RLL_ARCHAEOASTRONOMY_CLOCK_GEOMETRIC_CALIBRATION_V1.md), [Onda/Verbo e limites físicos](../canonicos/17_ONDA_VERBO_FISICA_NEURO_LINGUAGEM.md), [Mapa de claims](../RLL_TRACEABILITY_MAP.md). A camada literária permanece em [Sete Mestres](RLL_SETE_MESTRES_PARABOLAS_GEOMETRIA_20261114.md).

**Gates:** `MATH_IDENTITIES=DERIVED_CLASSICALLY`; `ALGORITHMIC_TESTS=NOT_RUN_FOR_THIS_COMMIT`; `RLL_COSMOLOGICAL_VALIDATION=NOT_RUN`; `NOVELTY_GLOBAL=NOT_VERIFIED`; `claim_allowed=false`. Nenhuma alteração de `H(z)`, datasets, scripts de likelihood, CI, schema, licenças ou claims é autorizada por este documento.

**R3:** F_ok = relações clássicas e contratos condicionais descritos; F_gap = originais medidos, teste específico de implementação, novidade e evidência cosmológica; F_next = somente se solicitado, adicionar verificadores isolados para operadores geométricos, sem tocar nas previsões físicas. **FIAT LUX.**
