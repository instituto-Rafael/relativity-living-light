# RLL — Auditoria Coerente dos resultados enviados (2026-07-09)

Status: `VERIFIED_AS_UPLOADED_ARTIFACTS` / `CLAIM_BOUNDED`

Este diretório preserva a varredura dos pacotes enviados nesta sessão:

- `rll-validation-results.zip`
- `resultados-bayesianos.zip`

A leitura é **operacional e documental**: compara os artefatos recebidos, registra hashes e mantém fronteira explícita de claim. Não declara superioridade cosmológica.

## Inventário pronto

| Bloco | Estado | Arquivos vistos | Leitura |
|---|---:|---|---|
| Comparação LCDM/RLL | `VERIFIED` | `comparison.json`, `lcdm.json`, `rll.json`, `plot_results_report.md` | 33 pontos; RLL muito próximo de LCDM; χ² LCDM menor neste artefato. |
| Bayes | `VERIFIED` | `data/bayes_result.json` | log BF = -6.633943221580; BF RLL/LCDM = 0.001314967640579. |
| Figuras | `HASHED_NOT_EMBEDDED` | `figs/model_comparison.png`, `figs/posterior_epsilon.png` | Presentes no pacote local; hashes registrados no manifesto. |
| Delta ponto a ponto | `DERIVED_VERIFIED` | `rll_uploaded_results_delta_audit.csv` | RLL − LCDM positivo nos 33 pontos. |
| Auditoria humana | `DERIVED_VERIFIED` | `rll_uploaded_results_audit.md` | Resumo F_ok/F_gap/F_next com fronteira de claim. |

## Métricas centrais

| Métrica | Valor |
|---|---:|
| N pontos | 33 |
| χ² LCDM | 25.654091158296 |
| χ² RLL | 25.842261429087 |
| Δχ² = χ²_RLL − χ²_LCDM | 0.188170270791 |
| ε mediano RLL | -0.000402026120419 |
| intervalo credível ε | [-0.001093264783950, 0.000297549855130] |
| logZ RLL | -1241.932079944736 |
| logZ LCDM | -1235.298136723156 |
| log Bayes Factor RLL/LCDM | -6.633943221580 |
| Bayes Factor RLL/LCDM | 0.001314967640579 |
| Odds aproximado LCDM/RLL | 760.475:1 |

## Fronteira de claim

O próprio `comparison.json` declara:

```text
comparison metric only; no superiority claim without predefined real-data thresholds
```

Interpretação permitida:

> RLL está numericamente próximo de LCDM neste ensaio, mas este pacote favorece LCDM no χ² e no Bayes factor. O resultado é auditável como artefato recebido, não como validação cosmológica forte.

Interpretação proibida:

> RLL venceu LCDM / provou matéria escura / provou energia escura / validou cosmologia.

## F_ok / F_gap / F_next

### F_ok

- Pacotes contêm comparação, séries de 33 pontos, relatório leve e resultado bayesiano.
- A posteriori de ε fica perto de zero e o intervalo informado inclui zero.
- O conjunto agora possui manifesto SHA256 para cadeia de custódia.

### F_gap

- Não há dados observacionais brutos, incertezas, matriz de covariância, priors completos, likelihood explícita, número de amostras ou diagnóstico de convergência.
- `model_lcdm.note` informa ΛCDM fixo com `logZ = log-likelihood`, o que torna a comparação assimétrica.
- Figuras PNG foram hasheadas localmente, mas a preservação canônica deve ocorrer preferencialmente via artifact/release/Zenodo ou commit binário separado.

### F_next

1. Adicionar script gerador e `requirements.txt`.
2. Incluir dataset/covariância/priors/likelihood.
3. Rodar MCMC/nested sampling com diagnóstico completo.
4. Separar explicitamente teste sintético de teste observacional real.
5. Atualizar `results/manifest.json` e `results/OUTPUTS_TEXTUAIS_INDEX.md` quando este diretório for consolidado.

Ω = caminho coerente + hash + fronteira de claim + próximo experimento.
