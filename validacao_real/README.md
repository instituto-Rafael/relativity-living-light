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

## Fluxo Rx — zero dependências externas Python

O caminho dependency-free canônico deste bundle é o runtime autoral `rx/`, construído apenas sobre a biblioteca padrão do Python.

```bash
cd ~/relativity-living-light-main
python3 -m validacao_real.run_rx_pipeline
```

Compatibilidade com o comando anterior:

```bash
python3 validacao_real/compute_validation_stdlib.py
```

Esse segundo comando apenas delega para o mesmo motor Rx; não existe uma segunda implementação numérica concorrente.

### Contrato Rx

- nenhum `pip install`;
- nenhum NumPy/Pandas/SciPy/PyYAML/Matplotlib/Astropy/emcee/dynesty;
- entrada operacional em JSON/CSV;
- inversão matricial, forma quadrática, Simpson, busca limitada, CSV/JSON e SVG implementados em `rx/kernel.py`;
- DESI DR2 usa a matriz de covariância commitada;
- RLL inicia no limite aninhado `Os0=0` do melhor ponto LCDM para o gate de não-regressão;
- figuras são SVG geradas sem biblioteca gráfica externa;
- `claim_allowed=false` permanece obrigatório.

Os algoritmos matemáticos utilizados são métodos conhecidos. "Autoral" aqui significa a implementação e arquitetura de software do projeto, não reivindicação de autoria sobre Simpson, Gauss-Jordan, AIC/BIC ou outros métodos acadêmicos existentes.

### Auditoria global de dependências

```bash
python3 tools/rx_dependency_audit.py
```

O auditor percorre os arquivos Python e materializa a dívida externa restante em:

- `results/rx_dependency_audit.json`
- `results/rx_dependency_audit.md`

Arquivos históricos, notebooks e rotas científicas antigas não são declarados migrados até que o auditor e testes específicos comprovem a substituição.


## Entrada canônica do programa Rx

O desenvolvimento dependency-free pode ser executado por um único programa determinístico:

```bash
cd ~/relativity-living-light-main
python3 -m rx status
python3 -m rx develop
```

Subcomandos:

- `status`: contratos e estado do runtime;
- `selftest`: gates de runtime, horizonte sonoro e paridade freestanding;
- `validate`: validação Rx + sucessor Structure-D;
- `parity`: gates de paridade semântica e Q16;
- `audit`: dívida de imports externos do repositório;
- `develop`: cadeia completa de desenvolvimento.

Contrato operacional: `training=false`, `ai_runtime=false`, zero dependências Python de terceiros no caminho Rx ativo. Otimização matemática determinística permanece permitida.
