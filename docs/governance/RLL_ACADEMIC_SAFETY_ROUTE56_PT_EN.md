# RLL Academic Safety Route56 — PT/EN

## Intenção / Intent

Este contrato transforma a navegação de oito direções em uma **malha de confronto acadêmico**. Ele não transforma geometria, emojis ou recorrência simbólica em evidência física.

The contract turns eight-direction navigation into an **academic cross-examination mesh**. Geometry, emojis, and symbolic recurrence are addresses, not scientific evidence.

## 8 direções / 8 directions

| k | θ | símbolo | PT | EN | domínio de auditoria |
|---:|---:|---|---|---|---|
| 0 | 0° | ↑ | cima | up | SOURCE_AUTHORITY |
| 1 | 45° | ↗️ | cima-direita | up-right | METHOD_VALIDITY |
| 2 | 90° | ➡️ | direita | right | DATA_PROVENANCE |
| 3 | 135° | ↘️ | baixo-direita | down-right | EXECUTION_REPRODUCIBILITY |
| 4 | 180° | ⬇️ | baixo | down | FALSIFICATION |
| 5 | 225° | ↙️ | baixo-esquerda | down-left | DEPENDENCE_BIAS |
| 6 | 270° | ⬅️ | esquerda | left | HISTORY_VERSIONING |
| 7 | 315° | ↖️ | cima-esquerda | up-left | CLAIM_GOVERNANCE |

Convenção: θ cresce no sentido horário a partir de ↑.

## Por que 56

O centro **não** entra na permutação. Entre oito direções distintas:

`P(8,2) = 8 × 7 = 56`.

Cada direção tem sete saídas e sete entradas. Há 56 rotas direcionadas, não 28 pares não-direcionados.

## Quatro classes geométricas

- 16 rotas vizinhas/tangenciais: giro mínimo 45°;
- 16 ortogonais: 90°;
- 16 cruzamentos oblíquos: 135°;
- 8 antipodais: 180°.

Essas classes servem para navegação e cobertura. **Não são pesos de evidência.**

## 6 POIs por rota

Cada rota passa por seis checkpoints conceituais:

`SOURCE → ARTEFACT → METHOD → EXECUTION → EVIDENCE → CLAIM`

Logo a malha possui `56 × 6 = 336` células de controle. Uma célula é um requisito/checkpoint, não uma alegação de que existe evidência material em todos os 336 pontos.

## Centro: UP / HOLD / DOWN

- **UP_READY**: elegível para o próximo estágio de validação; não significa teoria confirmada.
- **HOLD_TOKEN_VAZIO**: informação material insuficiente.
- **DOWN_BLOCKED**: fail-closed porque ao menos um gate crítico está bloqueado; não significa refutação global.

No estado atual do RLL, o centro esperado é `DOWN_BLOCKED` porque o E0 ainda bloqueia promoção metodológica.

## Ponte quadrática 45° → √3/2

Para um triângulo retângulo com catetos `a,b` e hipotenusa `h`:

`h²=a²+b²`.

Defina o resíduo entre hipotenusa e um cateto:

`d=h-a`.

Como `h=a+d`:

`(a+d)²=a²+b²`

e portanto:

`d²+2ad=b²`.

Esta é a forma de **completação quadrática / área auxiliar**: o quadrado residual `d²` mais duas áreas retangulares `ad` recompõem exatamente a área `b²`.

A mesma identidade fatorada é:

`(h-a)(h+a)=b²`.

No caso isósceles de 45°, usando `a=b=1`:

`h=√2`, `d=√2-1`

e:

`(√2-1)(√2+1)=1`.

Assim a diferença entre cateto e hipotenusa não é descartada: ela vira um resíduo geométrico exato.

Agora entra:

`√3/2=cos(30°)`.

Ela não é ângulo nativo da malha de 45°, mas pode atuar **sobre o resíduo** como segunda projeção:

`p=(√3/2)d=(√6-√3)/2`

`q=(1/2)d=(√2-1)/2`

e:

`p²+q²=d²`.

Portanto a ponte correta é:

`45° → resíduo d → projeção 30°/60° do resíduo`.

Isso define uma relação geométrica exata sem usar `√3/2` como peso de evidência física ou científica.

Na normalização por hipotenusa `h=1`, os catetos são `√2/2` e o resíduo é `1-√2/2`.

Na circunferência unitária, os oito triângulos isocêntricos adjacentes continuam tendo ângulo central 45°, corda `√(2-√2)` e área `√2/4`.

## Projeção espelhada 12 sobre cada eixo de 45°

A ponte quadrática não termina no primeiro passo de 30°. O resíduo

`d=√2-1`

é projetado em **seis passos para um lado** e **seis passos para o lado espelhado**:

`+30°, +60°, +90°, +120°, +150°, +180°`

`-30°, -60°, -90°, -120°, -150°, -180°`.

Para cada deslocamento assinado `φ`:

`p_φ=d cosφ`

`q_φ=d sinφ`

e:

`p_φ²+q_φ²=d²`.

O primeiro passo recupera a ponte anterior:

`cos30°=√3/2`, `sin30°=1/2`.

O espelho preserva a componente paralela e troca o sinal da componente transversal:

`p_{+φ}=p_{-φ}`

`q_{+φ}=-q_{-φ}`.

No passo `±180°`, os dois percursos assinados são diferentes como rota, embora coincidam no mesmo raio geométrico antipodal.

### Contagens

Por eixo-base de 45°:

`6 + 6 = 12` rotas trianguladas assinadas.

Para os oito eixos-base:

`8 × 12 = 96` projeções direcionais locais.

Aplicando a projeção aos 56 caminhos Route56:

`56 × 12 = 672` projeções orientadas.

Mantendo os 6 POIs acadêmicos:

`56 × 12 × 6 = 4032` células de controle projetadas.

### Fechamento angular

A composição da malha de 45° com a malha de 30° gera:

`gcd(45°,30°)=15°`.

Portanto a união global fecha em:

`360° / 15° = 24`

direções geométricas únicas.

Isto é uma consequência exata da combinação das duas grades angulares; não é um peso de evidência nem uma confirmação física.

## Fronteira de produção

A execução estrutural do Route56 prova somente que:

1. as 56 rotas estão completas e sem auto-laços;
2. PT/EN/emojis são endereços totais;
3. as classes angulares são consistentes;
4. cada rota carrega 6 checkpoints;
5. o grafo aponta para o evidence bridge e para o E0 reais;
6. o claim permanece fail-closed quando os gates científicos não permitem promoção.

Ela **não** prova a cosmologia RLL.

`SOURCE != ARTEFACT != METHOD != EXECUTION != EVIDENCE != CLAIM`
