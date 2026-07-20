# FASE 27 — Ω7 Operacional: Invariante Estrutural Multidimensional

> Estado: contrato operacional executável · `claim_allowed=false`
>
> Escopo: avaliar se uma estrutura do RLL pode avançar, permanecer em teste, ser auditada ou retornar ao vazio.

## 1. Relação com a matriz semântica 7D

A matriz existente em `docs/architecture/30_SEVEN_DIRECTION_SEMANTIC_MATRIX.md` interpreta conteúdo em sete leituras semânticas.

A Ω7 operacional é ortogonal:

```text
matriz semântica 7D
→ interpreta linguagem, relações, causalidade, lacunas e governança

Ω7 operacional
→ avalia proveniência, coerência, dimensão, runtime, memória, direitos e falsificação
```

Uma camada não substitui a outra.

## 2. Invariante

A definição adotada é uma convenção arquitetural:

\[
\Omega =
Identidade \otimes Relação \otimes Proveniência \otimes Medida
\otimes Direitos \otimes Estado \otimes Evidência
\]

O símbolo \(\otimes\) representa articulação estrutural. Não representa multiplicação física, produto tensorial demonstrado da natureza ou nova lei cosmológica.

Uma transformação é coerente quando preserva identidade e custódia:

\[
X_t \xrightarrow{\Delta} X_{t+1}
\]

\[
I_\Omega(X_{t+1}) =
I_\Omega(X_t) + \Delta_{\text{declarado}}
\]

Toda mudança relevante deve registrar origem, ação, método, efeito, artefato, hash e possibilidade de reversão.

## 3. Sete direções operacionais

| Direção | Dimensão | Pergunta |
|---|---|---|
| D1 | Origem e proveniência | Cada resultado chega a um run, commit, dado e artefato? |
| D2 | Coerência semântica | Nomes, estados, unidades e versões mantêm significado? |
| D3 | Integridade geométrica e dimensional | Domínios, unidades, transformações e limites são compatíveis? |
| D4 | Runtime e execução | O sistema executa o que declara e emite recibos? |
| D5 | Tempo, estado e memória | Histórico, linhagem, supersessão e invalidação são preservados? |
| D6 | Direitos e segurança | Autorização, licença, privacidade, autoria e risco estão ligados à ação? |
| D7 | Evidência e falsificação | Toda hipótese possui observável, baseline, incerteza e falsificador? |

## 4. Gates rígidos

Os sete gates I1–I7 têm precedência sobre qualquer pontuação.

```text
I1 nenhum resultado promovido sem origem
I2 nenhum claim sem evidência e revisão de fronteira
I3 nenhum TOKEN_VAZIO convertido silenciosamente em certeza
I4 nenhuma transformação material sem registro
I5 nenhuma evidência histórica apagada
I6 nenhuma execução crítica sem recibo auditável
I7 nenhum objetivo técnico acima de direitos e segurança
```

Se qualquer gate não estiver em `PASS`:

```text
decision = BLOCKED
```

A avaliação pode passar no schema e na CI enquanto declara `BLOCKED`. Isso significa que o instrumento está consistente, mas a estrutura avaliada ainda possui gates abertos.

## 5. Métricas de roteamento

Cada direção recebe uma nota convencional de 0 a 4:

| Nota | Estado |
|---:|---|
| 0 | bloqueado ou vazio |
| 1 | lacuna identificada |
| 2 | parcial |
| 3 | pronto para teste |
| 4 | verificado estruturalmente |

Normalização:

\[
d_i = score_i/4
\]

Equilíbrio global:

\[
\Omega_G =
\left(\prod_{i=1}^{7}d_i\right)^{1/7}
\]

Ponto mais fraco:

\[
\Omega_{\min} = \min(d_i)
\]

Essas métricas são convenções de roteamento. Não são geometria física, probabilidade, confiança científica ou evidência.

## 6. Regra de decisão

```text
gate rígido aberto ou Ωmin < 0.50 → BLOCKED
sem gate aberto e ΩG < 0.75       → READY_FOR_TEST
ΩG >= 0.75 e Ωmin < 0.75          → AUDITABLE
ΩG >= 0.75 e Ωmin >= 0.75         → COHERENT
```

`COHERENT` não significa teoria verdadeira. Significa apenas que as sete condições estruturais atingiram o limiar operacional definido.

## 7. Avaliação inicial do RLL

O arquivo canônico é:

```text
data/omega_operational/rll_omega7_operational.json
```

Estado inicial:

```text
Omega_G   = 0.479867804894
Omega_min = 0.25
mais fracas = D3, D7
gates abertos = I1, I4, I5, I6, I7
decision = BLOCKED
claim_allowed = false
```

O bloqueio não invalida o trabalho já executado. Ele impede promoção estrutural forte enquanto proveniência histórica, contrato dimensional, memória temporal, direitos de datasets e falsificadores ainda estiverem incompletos.

## 8. Condições urgentes

| ID | Direção | Prioridade | Entrega |
|---|---|---|---|
| U1 | D1 | P0 | ledger canônico de runs |
| U2 | D2 | P1 | registro de famílias e versões RLL |
| U3 | D3 | P0 | contrato dimensional completo |
| U4 | D4 | P1 | retomada e reutilização por hash |
| U5 | D5 | P0 | ledger temporal append-only |
| U6 | D6 | P0 | manifesto de direitos por dataset |
| U7 | D7 | P0 | pacote de falsificadores científicos |

A prioridade operacional é atacar o menor eixo, não o tema mais atraente:

\[
D_{\text{urgente}} =
\operatorname*{arg\,min}_{i}(d_i)
\]

No estado inicial, D3 e D7 são os menores eixos.

## 9. Execução

```bash
python tools/validate_omega7_operational.py --strict --write-report
pytest -q tests/test_omega7_operational.py
```

Artefatos:

```text
artifacts/omega7-operational/
├── omega7_operational_report.json
├── OMEGA7_OPERATIONAL_REPORT.md
└── CHECKSUMS.sha256
```

## 10. Fronteiras

```text
schema_valid != scientific_validation
Omega_G != physical invariant
Omega_min != probability
semantic 7D != operational Omega7
coherent != scientifically confirmed
BLOCKED != false
TOKEN_VAZIO != inexistente
```

## R3

\[
\left\langle
F_{ok}=\text{sete direções e gates executáveis},
F_{gap}=\text{cinco invariantes rígidas ainda abertas},
F_{next}=\text{fechar D3 e D7 sem apagar D1, D5 e D6}
\right\rangle
\]
