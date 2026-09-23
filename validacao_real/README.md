# Validação real RLL

Este diretório contém o bundle executável de validação real que antes estava
misturado em `.github/workflows`. A separação é intencional:

- `.github/workflows` fica reservado a workflows executáveis do GitHub Actions.
- `validacao_real/` contém scripts, contratos YAML de dados, fallbacks embutidos
  e artefatos gerados pela validação RLL vs LCDM.
- `docs/pipelines/validation_paths/` contém metodologia e arquivos de apoio que
  não devem ser interpretados pelo GitHub como workflows.

## Fluxo padrão

```bash
cd validacao_real
python3 fetch_real_data.py
python3 compute_validation.py
python3 make_figures.py
python3 render_report.py
```

## Artefatos

- `fetched/`: dados materializados e manifesto de proveniência.
- `results/`: métricas, predições, relatório renderizado e figuras.
- `legacy_artifacts/`: artefatos históricos preservados ao remover a fricção do
  diretório `.github/workflows`.

## Princípio operacional

A validação não declara descoberta. Ela materializa dados públicos/fallbacks,
calcula métricas explícitas e registra critérios de falsificação. Se a execução
falhar, o erro deve permanecer visível para fail-safe/failover/rollback.


## Fluxo Python puro / stdlib-only

Para ambientes mínimos (por exemplo Termux sem NumPy/Pandas/SciPy/PyYAML), use a rota aditiva abaixo:

```bash
cd ~/relativity-living-light-main
RLL_STDLIB_OUTPUT_STEM="rll_lcdm_hz_bao_stdlib_v1" \
RLL_STDLIB_SEED=1 \
RLL_STDLIB_MAXITER=12 \
python3 validacao_real/compute_validation_stdlib.py
```

Características desta rota:

- zero dependências Python de terceiros;
- zero funções definidas pelo usuário no arquivo (`def`);
- lê diretamente CSVs reais já versionados no repositório;
- usa a matriz de covariância DESI DR2 materializada;
- integra distâncias por Simpson implementado no próprio fluxo;
- ajusta LCDM e RLL por busca limitada determinística;
- inicializa RLL no limite aninhado `Os0=0` a partir do melhor ponto LCDM, impedindo regressão artificial do χ² nesse gate;
- escreve saídas versionadas em `validacao_real/results/`;
- mantém `claim_allowed=false`.

Escopo: H(z) + DESI DR2 BAO. Esta rota não substitui a pilha multiprobe/Scipy; ela existe para reprodução em Python mínimo sem dependências externas.
