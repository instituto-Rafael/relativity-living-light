# Contrato da Balança RLL — Hipótese que Aceita Perder

> Repositório: `relativity-living-light`  
> Ponte: Livro Vivo RAFAELIA  
> Status: `HIPOTESE_AUTORAL` + `FORMALIZACAO_READY`  
> Regra: uma hipótese que não aceita perder ainda não entrou na ciência

## 1. Parábola do mestre da balança

Um pesquisador levou ao mestre uma hipótese luminosa.

Ela tinha forma bonita.
Tinha nomes fortes.
Tinha símbolos que pareciam constelações.
Tinha uma narrativa capaz de aquecer o coração.

O pesquisador disse:

— Mestre, esta hipótese é especial.

O mestre respondeu:

— Então ela deve aceitar uma balança especial.

Sobre a mesa, colocou dois pratos.

No primeiro, escreveu:

```text
RLL
```

No segundo, escreveu:

```text
baseline
```

O pesquisador perguntou:

— Baseline?

O mestre respondeu:

— Sim. A hipótese não luta contra o vazio. Ela conversa com modelos que já carregam peso.

Então colocou no segundo prato:

```text
ΛCDM
wCDM
CPL
outros modelos de comparação
```

O pesquisador ficou inquieto.

— E se minha hipótese perder?

O mestre sorriu.

— Então ela começa a aprender.

— Mas se perder, ela deixa de ter valor?

— Não. Ela deixa de fingir. E aquilo que deixa de fingir pode amadurecer.

O mestre escreveu no alto do observatório:

```text
uma hipótese que não aceita perder ainda não entrou na ciência
```

E, abaixo, escreveu:

```text
beleza chama; medida decide; derrota honesta ensina
```

---

## 2. Invariante científica

```text
hipótese → baseline → dados → métrica → decisão → relatório → próximo teste
```

Forma compacta:

```math
Inv(Balança)=H_{RLL}\rightarrow H_{base}\rightarrow D\rightarrow M\rightarrow Decisão\rightarrow Auditoria
```

Onde:

| Símbolo | Significado |
|---|---|
| `H_RLL` | hipótese/modelo RLL |
| `H_base` | modelo de comparação, como ΛCDM, wCDM ou CPL |
| `D` | dados usados |
| `M` | métrica: χ², AIC, BIC, AICc, evidência, Bayes factor |
| `Decisão` | vence, perde, empata, colapsa ou precisa mais dados |
| `Auditoria` | registro dos parâmetros, seed, tolerância e artefatos |

---

## 3. Contrato mínimo

Toda execução RLL deve declarar:

```yaml
run_id: "YYYYMMDD-HHMM-rll"
modelos:
  rll: "descrição/versão"
  baselines:
    - LCDM
    - wCDM
    - CPL
dados:
  origem: "real|sintetico|misto|TOKEN_VAZIO"
  dataset: "nome/caminho"
  n_amostras: null
config:
  seed: null
  priors: []
  tolerancia: null
  maxiter: null
metricas:
  chi2: null
  aic: null
  aicc: null
  bic: null
  evidencia: null
  bayes_factor: null
decisao:
  vencedor: "RLL|LCDM|wCDM|CPL|empate|inconclusivo"
  motivo: ""
status_epistemologico: "RESULTADO_COMPUTACIONAL|HIPOTESE_AUTORAL|TOKEN_VAZIO"
artefatos:
  - "path/to/result.json"
  - "path/to/report.md"
limites:
  - ""
proximo_teste: ""
```

---

## 4. Estados da balança

| Estado | Significado | Ação |
|---|---|---|
| `RLL_VENCE` | RLL supera baselines nas métricas declaradas | revisar robustez e repetir |
| `RLL_PERDE` | baseline explica melhor | registrar honestamente e buscar F_gap |
| `RLL_EMPATA` | diferenças pequenas/inconclusivas | aumentar dados ou melhorar métrica |
| `RLL_COLAPSA_BASELINE` | RLL vira equivalente ao baseline | declarar degenerescência |
| `DADOS_INSUFICIENTES` | não há base para decisão | marcar `TOKEN_VAZIO` |
| `EXECUCAO_INVALIDA` | erro de script/configuração | corrigir antes de interpretar |

---

## 5. Métricas mínimas

| Métrica | Função | Observação |
|---|---|---|
| `χ²` | mede ajuste aos dados | menor pode ser melhor, conforme contexto |
| `AIC` | penaliza complexidade | comparar modelos no mesmo dataset |
| `AICc` | AIC corrigido para amostra menor | útil com N limitado |
| `BIC` | penaliza parâmetros mais fortemente | comparar com cuidado |
| `Bayes factor` | compara evidência bayesiana | exige priors e cálculo robusto |
| `evidência` | integração da likelihood | sensível a priors |

---

## 6. Regra de honestidade

```text
Se ΛCDM, wCDM ou CPL vencerem, registrar a vitória deles.
```

Isso não destrói RLL.

Apenas diz onde RLL ainda precisa trabalhar.

```text
derrota honesta → F_gap → novo teste
```

Não usar:

```text
resultado desfavorável → silêncio
```

Usar:

```text
resultado desfavorável → relatório → revisão
```

---

## 7. Separação de dados

| Tipo | Pode decidir ciência? | Como marcar |
|---|---|---|
| dado real validado | sim, com limites | `DADO_REAL` |
| dado sintético | não sozinho | `SIMULACAO` |
| dado misto | depende | `MISTO` |
| dado simbólico | não como evidência física | `METAFORA_DIDATICA` ou `HIPOTESE_AUTORAL` |
| dado ausente | não | `TOKEN_VAZIO` |

---

## 8. Como a hipótese pode falhar

RLL deve declarar falsificadores possíveis:

```text
1. Ajuste pior que ΛCDM/CPL em dados reais.
2. AIC/BIC penalizando RLL por complexidade sem ganho.
3. Bayes factor desfavorável.
4. Parâmetros colapsando para ΛCDM.
5. Falha de reprodutibilidade em seeds/configurações.
6. Sensibilidade extrema a priors.
7. Incapacidade de prever novos dados.
```

Uma hipótese defensável não foge desses itens.

Ela os transforma em teste.

---

## 9. Checklist antes de declarar resultado

```text
[ ] O dataset está identificado?
[ ] O dado é real, sintético, misto ou simbólico?
[ ] Os baselines foram rodados?
[ ] A mesma métrica foi aplicada a todos?
[ ] Priors, seed, tolerância e maxiter foram declarados?
[ ] Os artefatos foram salvos?
[ ] O vencedor foi registrado honestamente?
[ ] As limitações foram escritas?
[ ] O próximo teste foi definido?
```

---

## 10. Pequena parábola do prato vazio

Um discípulo colocou sua hipótese em um prato da balança.

No outro prato, não colocou nada.

A hipótese subiu imponente.

— Venceu! — gritou.

O mestre riu com ternura.

— Contra prato vazio, qualquer coisa parece peso.

Então colocou no outro prato modelos, dados, métricas e reprodutibilidade.

A balança se moveu novamente.

O discípulo perguntou:

— E agora?

O mestre respondeu:

— Agora começou.

---

## 11. Retroalimentar[3]

- **F_ok:** RLL recebe um contrato operacional para aceitar vitória, derrota, empate, colapso ou inconclusão.
- **F_gap:** falta conectar este contrato aos workflows reais, outputs JSON e relatórios existentes.
- **F_next:** criar um script ou relatório que leia resultados e gere `rll_balance_report.md` com decisão automática e auditável.
