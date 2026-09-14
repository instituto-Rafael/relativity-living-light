# RLL_BALANCE_SCRIPT_USAGE — Como Usar o Escrivão da Balança

> Repositório: `relativity-living-light`  
> Script: `scripts/rll_balance_report.py`  
> Status: `FORMALIZACAO_READY` + `RESULTADO_COMPUTACIONAL` quando executado  
> Regra: o relatório não escolhe a hipótese; registra o peso declarado

## 1. Parábola do escrivão automático

O mestre colocou dois pratos na balança.

Em um prato, colocou RLL.

No outro, colocou os baselines.

A balança se moveu.

O discípulo gritou:

— Já sei quem venceu!

O mestre respondeu:

— Hoje sabes. Amanhã lembrarás diferente.

Chamou então um escrivão automático.

O escrivão não amava RLL.
Também não amava ΛCDM.
Não tinha preferência por wCDM.
Não se encantava com CPL.

Ele apenas lia números e escrevia:

```text
métrica → vencedor → estado → limite → próximo teste
```

Assim nasceu `scripts/rll_balance_report.py`.

---

## 2. Invariante

```text
JSON de métricas → normalização → comparação → decisão → relatório Markdown/JSON
```

Forma compacta:

```math
Inv(Script)=MetricsJSON \rightarrow Normalize \rightarrow Compare \rightarrow Decision \rightarrow Report
```

---

## 3. Comando básico

```bash
python scripts/rll_balance_report.py \
  --input artifacts/joint_real_likelihood.json \
  --output-md artifacts/rll_balance_report.md \
  --output-json artifacts/rll_balance_report.json \
  --metric bic
```

---

## 4. Métricas aceitas

| Métrica | Direção | Uso |
|---|---|---|
| `chi2` | menor melhor | ajuste aos dados |
| `aic` | menor melhor | ajuste penalizado |
| `aicc` | menor melhor | AIC corrigido |
| `bic` | menor melhor | penalização mais forte |
| `evidence` | maior melhor | evidência/log evidência |
| `bayes_factor` | maior melhor | comparação bayesiana |

---

## 5. Estados possíveis

```text
RLL_VENCE
RLL_PERDE
RLL_EMPATA
RLL_COLAPSA_BASELINE
DADOS_INSUFICIENTES
EXECUCAO_INVALIDA
```

---

## 6. Formatos de JSON tolerados

O script tenta ler formatos comuns:

### 6.1 Dicionário por modelo

```json
{
  "RLL": {"chi2": 84.48, "aicc": 103.10, "bic": 117.75},
  "LCDM": {"chi2": 84.48, "aicc": 95.51, "bic": 105.27},
  "CPL": {"chi2": 62.07, "aicc": 78.07, "bic": 91.18}
}
```

### 6.2 Lista de modelos

```json
{
  "models": [
    {"model": "RLL", "chi2": 84.48, "bic": 117.75},
    {"model": "LCDM", "chi2": 84.48, "bic": 105.27},
    {"model": "CPL", "chi2": 62.07, "bic": 91.18}
  ]
}
```

---

## 7. Saídas geradas

```text
artifacts/rll_balance_report.md
artifacts/rll_balance_report.json
```

O Markdown é para leitura humana.

O JSON é para automação e workflow.

---

## 8. Linguagem correta para decisão

Se RLL perder:

```text
Nesta execução, RLL não superou os baselines declarados sob a métrica escolhida.
Isso não prova falsidade universal do programa RLL, mas indica F_gap operacional.
```

Se RLL vencer:

```text
Nesta execução, RLL superou os baselines declarados sob a métrica escolhida.
O resultado exige repetição com novos dados, priors declarados, seeds diferentes e revisão independente.
```

---

## 9. Próximo passo natural

```text
.github/workflows/rll-balance-report.yml
```

Esse workflow deve:

1. localizar JSON de resultados;
2. executar `scripts/rll_balance_report.py`;
3. gerar `rll_balance_report.md`;
4. fazer upload do relatório como artefato.

---

## 10. Parábola final — O peso não precisa gritar

O discípulo perguntou:

— Mestre, e se o relatório disser que perdi?

O mestre respondeu:

— Então agradece. A balança te poupou de construir no ar.

— E se disser que venci?

— Agradece também. Mas pesa de novo amanhã.

E escreveu:

```text
vitória sem repetição é convite;
derrota sem registro é desperdício;
relatório honesto é chão.
```

---

## 11. Retroalimentar[3]

- **F_ok:** o script agora tem manual de uso, estados, formatos e linguagem correta.
- **F_gap:** falta workflow que rode automaticamente e publique o artefato.
- **F_next:** criar `.github/workflows/rll-balance-report.yml`.
