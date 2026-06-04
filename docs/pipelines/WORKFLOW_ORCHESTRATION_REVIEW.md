# Revisão de orquestração dos workflows

## Fato operacional

O diretório `.github/workflows` deve conter apenas YAMLs executáveis do GitHub
Actions. YAMLs de dados, metodologia, scripts Python, imagens, PDFs e ZIPs são
insumos ou artefatos; quando ficam no diretório de workflows, criam fricção de
interpretação e risco de validação incorreta.

## Antes

- Havia YAML de metodologia (`CAMINHOS_VALIDACAO_NOVOS.yml`) junto dos workflows.
- Havia YAMLs de dados (`sources.yml`, `desi_dr2_bao.yml`,
  `hz_cosmic_chronometers.yml`) no mesmo diretório de pipelines executáveis.
- Scripts e artefatos de validação também estavam em `.github/workflows`.
- A seleção manual existia, mas não distinguia claramente workflow executável,
  validação real e metodologia de caminhos novos.

## Depois

- `.github/workflows` ficou restrito a workflows executáveis com `name`, `on` e
  `jobs`.
- `validacao_real/` passou a ser o bundle executável de validação real.
- `docs/pipelines/validation_paths/` passou a guardar metodologia e arquivos de
  apoio que não devem ser executados como workflow.
- `START_MANUAL_HERE.yml` ganhou opções de seleção para auditoria de workflow,
  validação real e metodologia de caminhos.
- `tools/audit_github_workflows.py` formaliza a verificação de higiene do
  diretório e o contrato mínimo dos workflows.

## Interpretação do pedido em linguagem técnica

As metáforas de toro, vetores, janelas, tokenização, entropia e coerência foram
tratadas como parábolas didáticas: elas indicam a necessidade de reduzir
ambiguidade, mapear camadas, preservar verdade verificável e separar execução de
metodologia. Em engenharia de CI/CD, isso vira um princípio simples: cada arquivo
precisa ter papel inequívoco, rota de execução, contrato de validação e saída
rastreável.

## Critérios de qualidade adotados

1. Isolamento: workflows executáveis separados de dados e artefatos.
2. Orquestração: entrada manual com escolhas explícitas e caminhos de execução.
3. Falsificabilidade: validação real com métricas e relatório gerado a partir de
   artefatos, sem números inventados.
4. Fail-safe: auditoria falha em modo estrito se o diretório voltar a misturar
   scripts/dados com workflows.
5. Preservação: artefatos antigos foram movidos para `legacy_artifacts/` em vez
   de serem descartados.
