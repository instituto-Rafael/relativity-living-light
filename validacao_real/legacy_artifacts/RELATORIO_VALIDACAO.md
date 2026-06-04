# Validacao Real RLL vs LCDM — relatorio automatico

_Gerado em 2026-06-04T03:19:44+00:00 UTC. Todos os numeros sao lidos dos artefatos; nenhum e inventado._

**Regiao de validade:** z in [0.0, 2.4] (onde DESI DR2 + cronometros cosmicos existem).

## Comparacao de modelos

| modelo | chi2 | chi2/dof | AIC | BIC | falsificado (BAO/Hz) |
| --- | --- | --- | --- | --- | --- |
| LCDM | 39.3823 | 0.9377 | 45.3823 | 50.8023 | False/False |
| RLL | 44.8893 | 1.1222 | 54.8893 | 63.9226 | False/False |

## Veredito

- Delta chi2 (LCDM - RLL): **-5.507**
- Preferido por AIC: **LCDM**
- Preferido por BIC: **LCDM**
- Limiar de falsificabilidade: 3.0 sigma (media de |pull|)

## Leitura honesta

- Modelo preferido pelos dados atuais: **LCDM**.
- Algum modelo falsificado na regiao de validade: **nao**.
- RLL permanece testavel: a amplitude do setor de superposicao (Os) e o ponto/largura
  de transicao (zt, wt) podem ser ajustados e re-testados sem mudar o pipeline.

## Figuras

### H(z): modelos vs cronometros cosmicos reais
![H(z): modelos vs cronometros cosmicos reais](figures/hubble_diagram.png)

### Distancias BAO: DESI DR2 vs modelos
![Distancias BAO: DESI DR2 vs modelos](figures/bao_distances.png)

### Pulls residuais por ponto
![Pulls residuais por ponto](figures/residual_pulls.png)

### Comparacao chi2 / AIC / BIC
![Comparacao chi2 / AIC / BIC](figures/model_comparison_bars.png)

## Artefatos

- `results/validation_summary.json` — resumo completo + parametros
- `results/model_comparison.csv` — uma linha por modelo
- `results/per_point_predictions.csv` — predicao e pull por ponto
- `results/figures/*.png` — figuras
