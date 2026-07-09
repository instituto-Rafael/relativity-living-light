# Auditoria dos pacotes enviados — RLL validation + resultados bayesianos

Data da leitura: 2026-07-09

## Pacotes inspecionados

- `rll-validation-results.zip`
  - `comparison.json`
  - `lcdm.json`
  - `rll.json`
  - `plot_results_report.md`

- `resultados-bayesianos.zip`
  - `data/bayes_result.json`
  - `figs/model_comparison.png`
  - `figs/posterior_epsilon.png`

## Resultado direto

### Comparação χ²

| Métrica | Valor |
|---|---:|
| χ² LCDM | 25.654091158296 |
| χ² RLL | 25.842261429087 |
| Δχ² = χ²_RLL − χ²_LCDM | 0.188170270791 |
| Interpretação local | LCDM fica levemente melhor neste artefato |

Observação do próprio arquivo `comparison.json`:
`comparison metric only; no superiority claim without predefined real-data thresholds`

### Diferença ponto a ponto

| Métrica | Valor |
|---|---:|
| N pontos | 33 |
| delta mínimo RLL-LCDM | 0.006765864847 |
| delta máximo RLL-LCDM | 0.120597080699 |
| delta médio | 0.050003311921 |
| delta mediano | 0.046561903093 |
| RMSE do delta | 0.058387281302 |
| delta relativo médio | 0.04191243% |

Os valores RLL estão sempre ligeiramente acima dos valores LCDM nos 33 pontos.

### Resultado bayesiano

| Métrica | Valor |
|---|---:|
| ε mediano | -0.000402026120419 |
| intervalo credível ε | [-0.001093264783950, 0.000297549855130] |
| logZ RLL | -1241.932079944736 |
| erro logZ RLL | 0.138611336762 |
| logZ LCDM | -1235.298136723156 |
| log BF = logZ_RLL − logZ_LCDM | -6.633943221580 |
| BF RLL/LCDM | 0.001314967640579 |
| Odds LCDM/RLL aproximado | 760.475:1 |

## Conclusão operacional

F_ok:
- O pacote tem trilha mínima coerente: comparação, séries de 33 pontos, relatório markdown e evidência bayesiana.
- A fronteira ética já está escrita no artefato: não há reivindicação de superioridade.
- A posteriori de ε está centrada perto de zero e inclui zero no intervalo informado.

F_gap:
- Não há dados observacionais brutos, incertezas, matriz de covariância, script de geração, priors completos, likelihood explícita, número de amostras, diagnóstico de convergência ou reprodutibilidade plena.
- O arquivo `model_lcdm.note` diz que ΛCDM é fixo e logZ = log-likelihood no valor observado; isso torna a comparação útil como teste local, mas ainda insuficiente como validação cosmológica forte.
- O Bayes factor favorece ΛCDM contra esta formulação RLL neste teste específico.

F_next:
1. Anexar scripts e ambiente (`requirements.txt`, seeds, comando exato).
2. Incluir dataset bruto/covariância/priors/likelihood.
3. Rodar MCMC/nested sampling com diagnóstico completo.
4. Separar teste sintético de teste observacional real.
5. Gerar `audit_manifest.json` com hash SHA256 de cada artefato.
