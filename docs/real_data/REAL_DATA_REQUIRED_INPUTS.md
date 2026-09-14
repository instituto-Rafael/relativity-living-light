# RLL — Required Real Cosmology Inputs

## Regra científica

O repositório só deve chamar algo de **dado real** quando houver origem primária, arquivo materializado, checksum e papel claro no teste. Lacuna não deve ser preenchida com mock, chute, interpolação ou dado sintético.

> Claim boundary: `No superiority claim unless real-data metrics pass predefined thresholds.`

## 1. Pantheon+SH0ES — supernovas Tipo Ia

**Status:** pronto para download automatizado.

**Fonte primária:** `PantheonPlusSH0ES/DataRelease`, repositório público oficial da colaboração Pantheon+SH0ES.

**Arquivos necessários no RLL:**

| caminho local | função | origem |
|---|---|---|
| `data/pantheon/Pantheon+SH0ES.dat` | tabela real SN/Cepheid-host distances | `Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat` |
| `data/pantheon/Pantheon+SH0ES_STAT+SYS.cov` | matriz de covariância estatística+sistemática | `Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES_STAT+SYS.cov` |
| `data/pantheon/lcparam_full_long_zhel.txt` | compatibilidade com runner atual | cópia byte-for-byte de `Pantheon+SH0ES.dat` |

**Comando:**

```bash
bash scripts/download_real_cosmology_inputs.sh
python scripts/run_real_pantheon_validation.py
```

**Critério de validação:** gerar `data/results/model_comparison.json` com `n_obs`, `chi2`, `AIC`, `BIC`, deltas e hashes dos arquivos reais.

## 2. DESI DR2 BAO — BAO 2025

**Status:** fonte real registrada, mas ainda não chi2-ready no repositório.

**Fonte primária:** DESI DR2 BAO, paper `arXiv:2503.14738`, publicado como `Phys. Rev. D 112, 083515 (2025)`.

**Necessário antes de usar em fit:**

| arquivo local requerido | conteúdo obrigatório |
|---|---|
| `data/real/desi_dr2_bao_measurements.csv` | tabela oficial de medidas BAO: tracer, z_eff, observável (`DM/rd`, `DH/rd`, `DV/rd` ou equivalente), valor, erro |
| `data/real/desi_dr2_bao_covariance.csv` | matriz/correlação oficial compatível com a tabela |
| `data/real/desi_dr2_bao_provenance.json` | URL/fonte, data, checksum, versão e notas de licença |

**Critério de bloqueio:** sem tabela oficial e sem covariância, DESI fica como fonte real registrada, não como dado usado em chi2.

## 3. Cosmic Chronometers — H(z)

**Status:** seed real inicial já materializado.

**Arquivo atual recomendado para importação auditável:** `data/real/Hz_data_real.csv`

**Colunas esperadas:** `z,H_obs,sigma_H,source`.

**Exemplo de linhas materializadas:**

| z | H_obs | sigma_H | source |
|---:|---:|---:|---|
| 0.07 | 69.0 | 19.6 | `CC_Moresco2022` |
| 0.09 | 69.0 | 12.0 | `CC_Moresco2022` |
| 0.12 | 68.6 | 26.2 | `CC_Moresco2022` |
| 0.17 | 83.0 | 8.0 | `CC_Moresco2022` |

**Necessário para virar compilação forte:** coletar tabela completa de cronômetros cósmicos com referência por linha, método, erro estatístico/sistemático e política de covariância.

## 4. Planck 2018 / CMB

**Status:** referência/prior, não dado bruto ingerido.

**Fonte primária aceitável:** Planck Legacy Archive / ESA ou produtos oficiais Planck 2018.

**Necessário antes de usar:** declarar exatamente se o RLL usa:

- prior comprimido (`Omega_b h^2`, `Omega_c h^2`, `theta_*`, etc.);
- likelihood oficial;
- cadeia MCMC;
- ou apenas comparação bibliográfica.

**Critério de bloqueio:** não usar Planck como número solto sem versão, likelihood/prior e arquivo verificável.

## 5. Política anti-sintética

- `mock`, `synthetic`, `demo`, `example`, `placeholder`, `TO_BE_REGENERATED`, `REGENERATE_WITH_SCRIPT` não podem entrar como dado real.
- Se o arquivo oficial não foi baixado, registrar lacuna.
- Se a matriz de covariância falta, não calcular chi2 completo.
- Se a fonte é resumo de artigo, marcar como `source_summary` ou `observed_seed`, nunca `validated_dataset`.

## 6. Registro adicional de dados reais — julho de 2026

O arquivo abaixo registra novas fontes reais e contextos observacionais sem promovê-los automaticamente a validação:

```text
data/real/cosmology/real_data_addition_registry_2026_07.json
```

O registro inclui:

- Pantheon+SH0ES oficial como `DOWNLOAD_READY`;
- DESI DR2 BAO como `REAL_VALIDATED_BLOCKED` até confirmar tabela/covariância exatas;
- DESI DR2 Lyα/extensões como `SOURCE_REGISTERED_ONLY` até localizar produto primário e covariância;
- Union3.1 e DES/Dovekie como contexto de compilação/calibração de supernovas, não dados locais ainda;
- Planck 2018 como `REAL_VALIDATED_BLOCKED` até distinguir prior comprimido, likelihood oficial, cadeia ou comparação bibliográfica.

Validador associado:

```bash
python tools/validate_real_data_addition_registry.py
```

Esse registro aumenta a cobertura de fontes reais, mas mantém `CLAIM_BLOCKED` até haver arquivo local, checksum, schema, covariância/erro, baseline e métrica.

## 7. URLs públicas para importação guardada

O workflow auxiliar abaixo aceita uma URL HTTPS pública CSV/JSON e gera artifact temporário de auditoria, sem commit automático de dado bruto:

```text
.github/workflows/import-data.yml
```

O arquivo abaixo registra URLs `raw.githubusercontent.com` já prontas para esse workflow:

```text
data/real/cosmology/import_data_public_real_urls_2026_07_09.json
```

Correção importante: `RLL_ALL_REAL_DATA_MASTER.csv` é **governança/ledger**, não dado observacional. Ele pode ser auditado como mapa, mas não deve ser usado como default de importação observacional.

URL padrão configurada no workflow:

```text
https://raw.githubusercontent.com/instituto-Rafael/relativity-living-light/main/data/real/Hz_data_real.csv
```

Exemplos de artifacts recomendados:

| bloco | URL registrada | artifact sugerido | estado |
|---|---|---|---|
| H(z) cronômetros cósmicos | `data/real/Hz_data_real.csv` | `rll-hz-real-audit` | observacional materializado |
| DESI DR2 BAO primary points | `data/real/cosmology/desi_dr2_bao_primary_points.csv` | `rll-desi-dr2-bao-audit` | observacional limitado; covariance gate |
| Planck 2018 compressed CMB prior | `data/real/CMB_shift_real.json` | `rll-cmb-shift-real-audit` | prior comprimido; não full likelihood |
| fσ8 growth compilation | `data/real/cosmology/fsigma8_growth_real.csv` | `rll-fsigma8-real-audit` | observacional limitado; covariance/independence gate |
| Master registry RLL | `data/real/cosmology/RLL_ALL_REAL_DATA_MASTER.csv` | `rll-real-master-governance-audit` | governança, não observação |

Fronteira: importar essas URLs prova apenas que o artefato foi baixado, normalizado para JSON e hasheado. Validação científica continua bloqueada até passar por loader, schema, erro/covariância, baseline e métrica.

## 8. Ordem operacional correta

```bash
# 1. Baixar Pantheon+ oficial
bash scripts/download_real_cosmology_inputs.sh

# 2. Verificar inputs Pantheon+ e gerar comparação real
python scripts/run_real_pantheon_validation.py

# 3. Conferir artefato final
cat data/results/model_comparison.json
```
