# CI Scientific Skills — Tier 1

## Objetivo

Este módulo transforma três itens do roadmap em verificações executáveis pela CI, sem converter diagnóstico numérico em alegação física:

1. **C1 — detecção de anomalias** em uma coluna numérica explícita de dados do repositório;
2. **B4 — Fourier em toro** por teste determinístico em `T¹`, como base auditável anterior à extensão `T^d`;
3. **D1 — diagnóstico Bayes aproximado** a partir de BIC, identificado explicitamente como aproximação de Laplace e não como nested sampling.

## Correção metodológica importante

CRC e hashes verificam integridade e identidade de bytes. Eles não são observáveis físicos e não devem ser usados como variável de anomalia cosmológica. Por isso, C1 usa escore robusto mediana/MAD sobre uma coluna numérica declarada e registra:

- caminho do arquivo;
- SHA-256 do arquivo;
- coluna analisada;
- limiar;
- índices sinalizados;
- fronteira explícita da claim.

## Estados permitidos

| Estado | Significado |
|---|---|
| `VERIFIED_METHOD` | Um teste numérico determinístico passou dentro da tolerância definida. |
| `EVIDENCED_ON_REPOSITORY_DATA` | Um arquivo real do repositório foi lido e diagnosticado. |
| `TOKEN_VAZIO` | O dado ou resultado necessário não existe no checkout; nenhuma conclusão é inventada. |
| `CONTRADICTION` | Um teste numérico esperado falhou. |

## Entradas procuradas

### C1

- `data/real/cosmology_observational_seed_2026.csv`
- `data/real/cosmology/cosmology_observational_seed_2026.csv`

### D1

- `results/structure_d/model_comparison_real.csv`
- `data/results/model_comparison.csv`

A ausência dessas entradas produz `TOKEN_VAZIO` no modo normal. O disparo manual pode ativar modo estrito e falhar a execução.

## Saídas

O workflow `.github/workflows/ci-scientific-skills.yml` produz um artefato contendo:

- `report.json` — resultado estruturado dos três skills;
- `run.log` — log da execução;
- `RECEIPT.json` — commit, workflow canônico e fronteira de claim;
- `CHECKSUMS.sha256` — hashes de todos os arquivos do artefato.

## Fronteiras científicas

- O teste Fourier valida a implementação em `T¹`; **não prova** convergência nova em `T⁷`.
- O diagnóstico BIC fornece `log(B)` aproximado; **não substitui** evidência calculada por nested sampling.
- O detector de anomalias sinaliza outliers sob um estimador; **não declara descoberta**.
- Nenhum resultado desta CI resolve Hodge, Riemann, Yang–Mills ou Navier–Stokes.

## Execução local

```bash
python -m pip install numpy pandas pytest
python -m pytest -q tests/test_ci_scientific_skills.py
python tools/ci_scientific_skills.py --root . \
  --output artifacts/ci-scientific-skills/report.json
```

Para exigir todas as evidências locais:

```bash
python tools/ci_scientific_skills.py --root . \
  --output artifacts/ci-scientific-skills/report.json \
  --strict
```

## Próxima camada verificável

1. Substituir o proxy BIC por nested sampling real, registrando priors, seed, tolerância e evidência.
2. Generalizar Fourier de `T¹` para `T^d` com testes de Parseval e recuperação de modos multidimensionais.
3. Definir schema observacional para C1, evitando escolha automática de coluna em execuções científicas finais.
4. Integrar os receipts ao workflow canônico de dados reais sem permitir push automático.
