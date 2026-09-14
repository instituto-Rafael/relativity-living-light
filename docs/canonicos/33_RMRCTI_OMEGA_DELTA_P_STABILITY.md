# RMRCTI / Ω — contrato de estabilidade ΔP

## Associação medida, estabilidade candidata e atrator não demonstrado

> **Status:** ponte canônica entre `llamaRafaelia/rmrCti` e a governança
> epistemológica do RLL.
>
> **Gate:** `research_only` até existirem traces reais independentes,
> falsificadores, bacia de parâmetros e validação fora da amostra.

## 1. Origem corrigida

A referência oral `gbc color 3.6.h` corresponde, no repositório inspecionado, a:

```text
rafaelmeloreisnovo/llamaRafaelia
└── rmrCti/gbs3_color.c
```

O arquivo calcula e exibe uma diferença de proporções condicionais e usa o
resultado como entrada de uma arena demonstrativa. O nome oral não deve ser
convertido em novo arquivo fictício.

O termo reconhecido como `thanks ponto de Exu` não foi localizado como caminho,
executável ou repositório concreto. Permanece:

```text
source_alias = TOKEN_VAZIO
operational_gate = human_review
```

## 2. Métrica exata

\[
\Delta P =
P(stable\_any=1\mid peak)
-
P(stable\_any=1\mid nonpeak)
\]

`peak` é determinado preferencialmente por `gate_in_peaks`. Na ausência dessa
coluna, o código existente usa os gates 3, 4 e 8.

A interpretação mínima é:

> quanto a frequência de fixed points classificados como estáveis difere entre
> a população de gates de pico e a população restante.

Não é, por definição:

- pressão física;
- precisão semântica;
- probabilidade de verdade;
- constante universal;
- coordenada de atrator;
- causalidade.

## 3. Origem de `stable_any`

No acoplador `triad_cti_couple.py`, cada chunk é projetado em um toro:

\[
(u,v)\rightarrow c\in\mathbb{C}
\]

Em seguida são calculados os pontos fixos da transformação quadrática:

\[
z=\frac{1\pm\sqrt{1-4c}}{2}
\]

O critério implementado é:

\[
|2z|<1
\]

Se ao menos um dos dois pontos satisfizer esse critério, `stable_any=1`.
Portanto, o termo “estável” tem um significado de código preciso dentro dessa
transformação. Ele não deve ser transferido automaticamente para estabilidade
psicológica, física ou cosmológica.

## 4. Cadeia de proveniência

```text
bytes de origem
→ rafa_cti_scan.c
→ idx/off_pad/fid/entropia/flips
→ triad_cti_couple.py
→ u/v/c/D/fixed points/gate
→ stable_any
→ grupos peak/nonpeak
→ ΔP por trace
→ distribuição de ΔP entre traces
→ claim gate
```

A invariante prioritária é a continuidade dessa rota, não o decimal isolado.

## 5. O valor aproximadamente 0,18

A recorrência `ΔP ≈ 0,18` é registrada como:

```text
AUTHOR_OBSERVATION
→ TESTABLE_TARGET
→ NOT_YET_GLOBAL_RESULT
```

Um valor único próximo de 0,18 produz somente uma associação medida naquele
trace. Repetições independentes com mediana próxima e baixa dispersão permitem
falar em **candidato de estabilidade operacional**.

A proximidade entre `0,18` e outros números do repositório — por exemplo um
`IC_mean` próximo — não estabelece relação. Identidade decimal não é identidade
semântica, causal ou matemática.

## 6. Escada de alegação

| Nível | Evidência necessária | Estado permitido |
|---|---|---|
| L0 | fórmula e código inspecionados | `DOCUMENTED_METRIC` |
| L1 | um trace real com hash e contagens | `MEASURED_ASSOCIATION` |
| L2 | três ou mais runs independentes, alvo e baixa dispersão | `REPLICATED_STABILITY_CANDIDATE` |
| L3 | região ampla de seeds e parâmetros | `PARAMETER_BASIN_SUPPORTED` |
| L4 | corpus, aparelho ou domínio não usado no ajuste | `CROSS_DOMAIN_REPLICATED` |
| L5 | convergência, bacia, perturbação e nulos compatíveis | `ATTRACTOR_SUPPORTED` |

Estado atual canônico:

```text
code_metric = DOCUMENTED
real_repeated_runs = TOKEN_VAZIO
attractor_claim = TOKEN_VAZIO
universal_invariant = TOKEN_VAZIO
```

## 7. Ferramenta criada no llamaRafaelia

```text
rmrCti/rmrcti_delta_p_report.py
```

A ferramenta separa a medição da arena e gera:

- hash SHA-256 e tamanho de cada trace;
- contagens por população;
- proporções condicionais;
- ΔP;
- intervalo conservador de 95%;
- teste de associação de duas proporções;
- média, mediana, desvio padrão e MAD entre runs;
- gate de estabilidade candidata;
- limites epistemológicos.

A regra padrão exploratória é:

```text
alvo = 0.18
tolerância = ±0.02
mínimo de runs = 3
MAD ≤ 0.01
```

Esses parâmetros são declarados pelo experimento e podem ser alterados. Eles
não são propriedades naturais demonstradas.

## 8. Invariante geométrica candidata

A unidade transdisciplinar é:

\[
U_{\Delta P}=(X,O,Z,\widehat Z,R,\Sigma,H,F,G)
\]

onde:

- `X`: corpus, chunking, seed e parâmetros;
- `O`: implementação e máquina observadora;
- `Z`: proporções observadas;
- `Ẑ`: nulo ou baseline esperado;
- `R`: ΔP;
- `Σ`: incerteza e dispersão;
- `H`: hipóteses rivais;
- `F`: falsificadores;
- `G`: gate epistemológico e operacional.

A possível invariante não é “0,18 em todo lugar”. A pergunta é:

> ΔP permanece aproximadamente estável sob transformações explicitamente
> enumeradas da rota?

Transformações mínimas:

- seeds;
- parâmetros do toro;
- gates;
- chunk size e padding;
- corpus;
- dispositivo;
- implementação.

## 9. Fractalidade e recursividade

É possível usar a mesma gramática em três escalas:

```text
chunk
→ trace
→ corpus/rede de corpora
```

Isso constitui uma estrutura recursiva multiescalar. O termo “fractal
matemático” fica bloqueado até existir lei de escala, dimensão ou
self-similarity quantitativa.

## 10. Falsificadores obrigatórios

1. embaralhar `stable_any`;
2. sortear grupos de gates com os mesmos tamanhos;
3. executar seeds pré-declaradas;
4. varrer `R`, `r`, `kappa`, `alpha`, `beta` e `lam`;
5. alterar chunk size e padding;
6. usar corpora independentes;
7. usar traces sintéticos nulos;
8. corrigir busca múltipla de parâmetros;
9. repetir em implementação independente;
10. publicar runs negativos.

Se o valor só reaparece após escolher o melhor gate ou parâmetro no mesmo dado,
o resultado é compatível com seleção pós-hoc, não com invariante.

## 11. Relação com a arena

`gbs3_color.c` usa ΔP para definir um viés discreto:

```text
ΔP > 0.20 → bias 2
ΔP > 0.05 → bias 1
caso contrário → bias 0
```

Esse uso prova somente que o programa consome o valor. O comportamento dos
agentes não retroprova a validade estatística da métrica.

## 12. Relação com CTI memory e Lama

`cti_memory` é um recuperador externo opt-in, por palavras-chave, com
proveniência. Não é treinamento nem busca semântica aprendida.

Um relatório ΔP só pode entrar no contexto com rótulo explícito:

```text
[RMRCTI ΔP: associação medida; atrator não estabelecido]
```

Sem relatório real:

```text
retrieved_claim = TOKEN_VAZIO
```

## 13. Relação com RLL

RLL recebe o artefato como contrato metodológico transversal, não como evidência
cosmológica. Nenhum valor de ΔP do RMRCTI deve ser usado para ajustar ou validar
parâmetros cosmológicos sem uma ponte matemática e dados específicos.

```text
RMRCTI stability metric
≠
RLL cosmological likelihood
```

A convergência está na disciplina:

```text
origem
→ transformação
→ resíduo
→ incerteza
→ falsificador
→ claim gate
```

## 14. Artefatos

No `llamaRafaelia`:

- `rmrCti/gbs3_color.c`;
- `rmrCti/triad_cti_couple.py`;
- `rmrCti/rmrcti_delta_p_report.py`;
- `rmrCti/RMRCTI_DELTA_P_STABILITY_CONTRACT.md`;
- `rmrCti/tests/test_rmrcti_delta_p_report.py`.

No RLL:

- `docs/canonicos/33_RMRCTI_OMEGA_DELTA_P_STABILITY.md`;
- `schemas/rmrcti_delta_p_observation.schema.json`;
- `fixtures/rmrcti_delta_p_observation.example.json`;
- `scripts/validate_rmrcti_delta_p_observation.py`.

## 15. F_ok / F_gap / F_next

**F_ok:** fórmula, rota de origem e ferramenta de relatório estão formalizadas.

**F_gap:** não há ainda pacote versionado de traces reais independentes que
sustente a recorrência de 0,18.

**F_next:** gerar traces com manifesto, executar nulos e varreduras, comparar
holdout e promover somente o nível realmente alcançado.
