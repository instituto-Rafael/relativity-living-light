# Relatório da Balança RLL

> Gerado por `scripts/rll_balance_report.py`  
> Status epistemológico: `RESULTADO_COMPUTACIONAL`  
> Regra: uma hipótese que não aceita perder ainda não entrou na ciência.

## Parábola do escrivão

A balança falou.

O escrivão não escolheu o prato vencedor.

Ele apenas escreveu:

```text
resultado bruto → métrica comparada → decisão → limite → próximo teste
```

Assim, amanhã ninguém precisa lembrar de cabeça o que a balança já disse.

## Entrada

```text
artifacts/rll_balance/20260709-132833-utc/input.json
```

## Artefatos irmãos

```text
artifacts/rll_balance/20260709-132833-utc/rll_balance_report.json
artifacts/rll_balance/20260709-132833-utc/rll_balance_report.md
artifacts/rll_balance/20260709-132833-utc/manifest.json
```

## Métrica decisória

```text
bic (lower_is_better)
```

Tolerância:

```text
1e-09
```

## Tabela de modelos

| Modelo | χ² | AIC | AICc | BIC | Evidência | Bayes factor | Papel |
|---|---:|---:|---:|---:|---:|---:|---|
| RLL | 84.4824 | TOKEN_VAZIO | 103.1006 | 117.7535 | TOKEN_VAZIO | TOKEN_VAZIO | RLL |
| LCDM | 84.4824 | TOKEN_VAZIO | 95.5169 | 105.2768 | TOKEN_VAZIO | TOKEN_VAZIO | BASELINE |
| wCDM | 83.7104 | TOKEN_VAZIO | 97.1841 | 108.6637 | TOKEN_VAZIO | TOKEN_VAZIO | BASELINE |
| **CPL** | 62.0717 | TOKEN_VAZIO | 78.0717 | 91.1839 | TOKEN_VAZIO | TOKEN_VAZIO | BASELINE |

## Decisão

```yaml
state: RLL_PERDE
winner: CPL
metric: bic
reason: Baseline 'CPL' superou RLL em 'bic'.
```

## Coerência operacional

```text
upload zip → extração → pasta datada → input alinhado → relatório JSON/MD → manifest → próximo teste
```

Este relatório foi adaptado para apontar para a pasta datada real do artefato:

```text
artifacts/rll_balance/20260709-132833-utc/
```

## Limites

- Este relatório compara somente métricas presentes no JSON de entrada.
- Vitória local em métrica não equivale a prova científica universal.
- Bayes factor/evidência dependem dos priors e do método de integração usados.
- Se o JSON de entrada mistura dados reais e sintéticos, a decisão deve declarar essa limitação.

## Próximo teste

```text
Repetir com dados, priors, seeds e tolerâncias declarados; gerar artefatos versionados.
```

## Parábola da derrota que virou degrau

A balança desceu para CPL.

O discípulo quis esconder o peso.

O mestre segurou sua mão e disse:

> A derrota registrada vira degrau.  
> A derrota escondida vira labirinto.

Então o relatório foi guardado com caminho, data e manifesto.

## Retroalimentar[3]

- **F_ok:** a execução transformou JSON de métricas em decisão auditável e agora os caminhos apontam para a pasta real.
- **F_gap:** a decisão depende da qualidade do JSON, dos dados e das métricas disponíveis.
- **F_next:** usar este artefato como amostra real do workflow `rll-balance-report.yml` e publicar relatórios como artifacts oficiais do CI.
