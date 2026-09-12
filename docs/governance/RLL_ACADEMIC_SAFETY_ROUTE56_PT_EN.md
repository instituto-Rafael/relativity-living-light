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

## √3/2

`√3/2 = cos(30°)`.

A malha Route56 usa passos de 45°. Portanto `√3/2` **não é coordenada nativa nem peso científico** desta malha. Ele permanece um token geométrico separado:

`TOKEN_VAZIO_SEPARATE_GEOMETRIC_CONTRACT`

Na circunferência unitária, os oito triângulos isocêntricos adjacentes têm ângulo central 45°, corda `√(2-√2)` e área `√2/4`.

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
