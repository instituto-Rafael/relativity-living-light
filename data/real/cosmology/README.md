# Data README — Cosmology (Real)

Status: metadata_only / fetch-ready via orchestrator

## Fontes
- DESI DR2 BAO — https://www.desi.lbl.gov/
- Pantheon+ SNe Ia — https://github.com/PantheonPlusSH0ES/DataRelease
- Planck 2018 chains (PLA) — https://pla.esac.esa.int/
- H(z) cosmic chronometers — doi:10.48550/arXiv.1604.01410
- fσ8 constraints — doi:10.48550/arXiv.1801.01590

## Limitações
- Sem download de chains/dados pesados por padrão.
- Modo compute permanece stub até processamento reproduzível real.

## Orquestração GitHub Actions
- Workflow: `.github/workflows/rll-real-data-orchestrator.yml`
- Script de ingestão: `scripts/fetch_real_sources.py`
- Artefatos principais:
  - `artifacts/rll-real-run/raw/SOURCES.json`
  - `artifacts/rll-real-run/raw/cosmology_curated/CURATED_SOURCES.json`
  - `artifacts/rll-real-run/raw/cosmology_curated/Hz_data_real.csv`
  - `artifacts/rll-real-run/raw/cosmology_curated/CMB_shift_real.json`
- The curated import also preserves the remaining inputs from the joint contract:
  `desi_dr2_bao_primary_points.csv`, `desi_dr2_bao_covariance_summary.csv`, and
  `fsigma8_growth_real.csv`. Each file retains its source path and SHA256
  in `CURATED_SOURCES.json`.
- The canonical workflow `.github/workflows/real-data-complete-execution.yml`
  packages these inputs under `artifacts/real-data-complete/inputs/` and publishes
  `REAL_INPUTS.json`. The operational sequence is: stage 30 audits/materializes,
  stage 40 runs the auxiliary route, and stages 50/60 generate formulas/IML.
  IML uses only `Hz_data_real.csv`; DESI, fσ8, and CMB remain on the joint
  Structure-D route to avoid mixing observables or semantics.

## Materialização real adicional — crescimento `fσ8`

- `fsigma8_growth_real.csv` contém uma compilação real de medições de crescimento/RSD com colunas de proveniência por linha (`survey`, `method`, `reference`, `source_url`).
- O arquivo substitui a fixture suave `data/inputs/structure_d/fsigma8.csv` apenas nas rotas de validação real/joint; a fixture continua no repositório para testes e rollback.
- A auditoria `python tools/real_data_materialization_audit.py` registra essa rota como `fsigma8 → real_fsigma8` e `fsigma8_cov_synth → real_fsigma8`.

## Assinaturas/proveniência viva de fontes

- `real_source_signatures.json` é gerado por `python tools/verify_real_source_signatures.py`.
- O arquivo registra SHA256 local, amostra HTTP limitada, termos obrigatórios encontrados e status de revisão/failover por fonte.
- Uma fonte bloqueada permanece marcada como revisão necessária; isso não autoriza preencher dados ausentes.

## Materialização oficial Pantheon+SH0ES (não-binária)

- `pantheon_plus/` contém arquivos oficiais selecionados do repositório público `PantheonPlusSH0ES/DataRelease`.
- A política desta cópia é **sem binários e sem matrizes pesadas no git**: FITS, TAR e covariâncias de dezenas de MB ficam como materialização manual/failover a partir da origem oficial.
- `pantheon_plus/MANIFEST.json` registra `source_url`, `size_bytes` e `sha256` por arquivo para rollback e auditoria.

## Structure-D real data

- O profile `structure_d_real_validation` agora inclui `real_fsigma8`, além de Hz, BAO e CMB shift.
- O profile `structure_d_real_growth_validation` executa Hz + BAO + CMB shift + fσ8 real + pontos primários DESI DR2 BAO para validação expandida.

## Contrato YAML canônico para cosmologia real

- `real_cosmology_inputs.yml` é a fonte de verdade YAML para os blocos reais locais usados em validação conjunta: H(z), DESI DR2 BAO, fσ8/RSD e CMB shift.
- O contrato aponta apenas para arquivos reais já materializados no repositório e preserva a fronteira de claim: registro/materialização de fonte não é validação científica nem confirmação de RLL.
- Validação estrutural: `python tools/validate_real_cosmology_inputs_yml.py`.
- Gate de CI: `.github/workflows/real-data-contract-ci.yml` valida o YAML antes de executar a computação com dados reais commitados.

## Importação real com failover, watchdog, rollback e tags

- A rota executável principal é `scripts/compute_rll_real_pipeline.py`; ela lê dados reais materializados em `artifacts/.../raw/cosmology_curated` no modo `auto` e usa os arquivos reais versionados em `data/real` como failover explícito, sem promover fixtures sintéticas.
- Cada execução publica `MANIFEST.json`, `COMPUTE_REPORT.md`, `TAGS.json`, `WATCHDOG.json`, `CHECKSUMS.sha256` e tabelas processadas para upload pelo workflow `.github/workflows/real-data-contract-ci.yml`.
- `WATCHDOG.json` falha a execução quando entradas reais obrigatórias faltam, quando contagens ficam vazias ou quando incertezas deixam de ser positivas.
- Escritas de artefatos são atômicas e preservam `*.bak` quando substituem saída anterior, permitindo rollback local auditável.
- Tags GitHub (`refs/tags/...`) e `RLL_IMPORT_TAGS` são autodetectadas apenas como proveniência de publicação; não autorizam claim científico nem release promocional.

## Covariância completa do CMB shift (Planck 2018)

- `data/real/CMB_shift_real.json` agora inclui `ob_h2_obs`/`ob_h2_sig` e a matriz de covariância 3x3 completa `[R, l_A, Omega_b h^2]`, extraída da Tabela I (ΛCDM base) de Chen, Huang & Wang (2019, arXiv:1808.05724) — a submatriz principal 3x3 do bloco de correlação publicado 4x4 `{R, l_A, Omega_b h^2, n_s}`, descartando `n_s` por não ser parâmetro ajustado nos modelos deste repositório.
- `data.pipelines.structure_d.joint_real_likelihood._cmb_chi2` usa essa covariância completa (via `chi2_with_covariance`) quando presente, com fallback diagonal `[R, l_A]` para fixtures antigas/mínimas.
- Fontes assinadas: `real_cmb_shift` (Planck 2018 VI, valores compressos) e `real_cmb_shift_covariance` (Chen, Huang & Wang 2019, matriz de correlação) em `real_source_signatures.json`.
- Isso fecha a sub-lacuna de covariância comprimida em `GAP-COSMO-CMB`; a lacuna permanece `TOKEN_VAZIO*` porque ainda falta um backend nativo CLASS/CAMB (C_l completo) — ver `data/real_sources/rll_required_data_gap_registry.yml`.
