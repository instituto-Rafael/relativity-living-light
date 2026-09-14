# RLL — Auditoria do Pipeline de Validação Científica Completa

**Gerado**: 2026-07-07  
**Fase**: 8 — Consolidação Pós-Pipeline  
**Analogia**: `09_PANTHEON_RESULTADO_REAL.md` (auditoria de execução) → este documento audita o *pipeline* como ato documentado

---

## Propósito

Este documento audita o pipeline CI como artefato científico, independentemente de seus resultados.
O pipeline existe e está merged — isso é auditável. Os resultados do primeiro run são TOKEN_VAZIO P0 até execução.

**Princípio**: Documentar a infraestrutura de validação é parte do processo científico, não apenas os números.

---

## Arquivo Canônico

```
.github/workflows/rll-validacao-cientifica-completa.yml
```

- **PR**: #506 (merged 2026-07-07)
- **Commit**: `700f1ba`
- **Trigger**: `workflow_dispatch` (manual)
- **Estado epistêmico**: [C] pipeline existe e compila; [VAZIO P0] primeiro run pendente

---

## Arquitetura: 11 Jobs em Sequência Lógica

```
setup_ambiente
    ├── fit_pantheon_rll ─────────────────┐
    ├── fit_desi_bao ─────────────────────┤
    │                                    ▼
    ├── h0_grid_scan          weff_cpl_mapping
    │                         zt_falsification
    │                                    │
    │                          joint_mcmc_p0 ★ (P0)
    │                                    │
    │                          bayes_factor_p0 ★ (P0)
    │                                    │
    │                    gerar_contrato_falsificadores
    │                                    │
    └──────────────────── relatorio_final
                                         │
                           commit_resultados (opcional)
```

### Detalhamento por Job

| Job | Função | Script | Output | Timeout |
|-----|--------|--------|--------|---------|
| `setup_ambiente` | Checkout + deps + checksum inputs | `pip install -e ".[dev]"` | `data-checksums` | 10 min |
| `fit_pantheon_rll` | χ² RLL vs ΛCDM em Pantheon+ SH0ES | `scripts/pantheon/run_rll_vs_pantheon.py` | `pantheon_fit_result.json` | 10 min |
| `fit_desi_bao` | χ² RLL em DESI DR2 BAO (13 pontos) | `scripts/compute_rll_real_pipeline.py --desi-only` | `desi_bao_result.json` | 10 min |
| `weff_cpl_mapping` | Mapeamento w₀_eff, wₐ_eff vs CPL | `scripts/compute_weff_cpl_mapping.py` | `weff_cpl_mapping.json` | 10 min |
| `zt_falsification` | Scan de z_t: verificar se z_t ≠ 0 com C.L. | `scripts/slingshot_zt_falsification.py` | `zt_result.json` | 10 min |
| `h0_grid_scan` | Grid H₀ × Ωm sobre residuals | `scripts/run_h0_grid_expansion.py` | `h0_grid_result.json` | 10 min |
| `joint_mcmc_p0` ★ | **P0 CRÍTICO**: MCMC conjunto Pantheon+ + DESI | `python -m data.pipelines.structure_d.run_all` | `joint_mcmc_summary.json` + corner.png | **25 min** |
| `bayes_factor_p0` ★ | **P0 CRÍTICO**: Evidence ratio ln(B₁₀) RLL/ΛCDM | `scripts/slingshot_zt_falsification.py --bayes-factor` | `bayes_factor_result.json` | 15 min |
| `gerar_contrato_falsificadores` | Tabela F-COS-01..05 com resultados CI | script Python inline | `CONTRATO_FALSIFICADORES_RLL.md` | 5 min |
| `relatorio_final` | Consolida todos os JSONs + CLAIM_BOUNDARY | `scripts/build_real_validation_report.py` | `RELATORIO_COMPLETO_*.md` | 5 min |
| `commit_resultados` | Git add + commit + push (se `commit_resultados=true`) | bash inline | commit ao branch | 5 min |

★ = P0 desbloqueador do PODE

---

## Como Disparar

### Via GitHub Actions UI

1. Navegar para `Actions → RLL Validação Científica Completa (P0/P1 Desbloqueadores PODE)`
2. Clicar `Run workflow`
3. Selecionar inputs:
   - **modo**: `completo` (todos os 11 jobs)
   - **commit_resultados**: `true` (para persistir resultados no repo)
4. Aguardar ~75 minutos

### Modos Disponíveis

| Modo | Jobs Executados | Uso |
|------|----------------|-----|
| `completo` | todos os 11 jobs | validação completa P0/P1 |
| `apenas_fit` | setup + fit_pantheon + fit_desi + relatorio | verificar fits rapidamente |
| `apenas_bayes` | setup + joint_mcmc + bayes_factor + relatorio | focar em P0 |
| `apenas_falsificadores` | setup + gerar_contrato + relatorio | atualizar tabela |
| `dry_run` | setup apenas | verificar ambiente |

---

## Outputs Esperados (Primeiro Run)

### Artefatos CI (GitHub Actions Artifacts)

```
pantheon-fit-results/
  pantheon_fit_result.json       # χ²_RLL, χ²_ΛCDM, ΔAIC, N=1624
  CLAIM_BOUNDARY.md              # obrigatório
  CHECKSUMS.sha256               # verificação de integridade

desi-bao-results/
  desi_bao_result.json           # χ²_RLL otimizado (13 pontos DESI DR2)
  CLAIM_BOUNDARY.md

joint-mcmc-results/
  joint_mcmc_summary.json        # posteriors: {H₀, Ωm, Ωs0, z_t, w_t}
  corner.png                     # plot de posteriores 2D
  chains.npy                     # cadeia MCMC completa
  CLAIM_BOUNDARY.md

bayes-factor-results/
  bayes_factor_result.json       # ln(B₁₀), escala Jeffreys
  CLAIM_BOUNDARY.md

contrato-falsificadores/
  CONTRATO_FALSIFICADORES_RLL.md # tabela F-COS-01..05 com resultados CI

relatorio-final/
  RELATORIO_COMPLETO_YYYYMMDD.md # relatório consolidado
  CHECKSUMS.sha256
```

### Resultados Comprometidos (se `commit_resultados=true`)

```
results/ci/
  pantheon_fit_YYYYMMDD.json
  desi_bao_chi2_YYYYMMDD.json
  weff_cpl_mapping_YYYYMMDD.json
  zt_falsification_YYYYMMDD.json
  h0_grid_YYYYMMDD.json
  joint_mcmc_YYYYMMDD/
  bayes_factor_YYYYMMDD.json
  RELATORIO_COMPLETO_YYYYMMDD.md

docs/cronologia-auditoria/
  CONTRATO_FALSIFICADORES_RLL.md  # sobrescreve baseline estático
```

---

## Estado Epistêmico

| Item | Estado | Evidência |
|------|--------|-----------|
| Pipeline existe e é válido | [C] ✅ | PR #506 merged; `audit_github_workflows.py --strict` passa |
| Dados de entrada presentes | [E] ✅ | `data/real/cosmology/pantheon_plus/Pantheon+SH0ES.dat`, `desi_dr2_bao_primary_points.csv` |
| Scripts de fitting existem | [C] ✅ | `scripts/pantheon/`, `scripts/compute_rll_real_pipeline.py` |
| Structure-D pipeline existe | [C] ✅ | `data/pipelines/structure_d/run_all.py` |
| Primeiro run concluído | ⚠️ [VAZIO P0] | Token: G1 + G2 no Ledger |
| χ² otimizado DESI | ⚠️ [VAZIO P0] | Token: G1 no Ledger |
| ln(B₁₀) RLL/ΛCDM | ⚠️ [VAZIO P0] | Token: G2 no Ledger |
| CONTRATO atualizado com CI | ⚠️ [VAZIO P0] | baseline estático em uso |

---

## Conexão com P0 Desbloqueadores do PODE

O pipeline fecha diretamente os seguintes P0 do PODE:

| Gap PODE | Job do Pipeline | Falsificador |
|----------|----------------|-------------|
| Joint MCMC Pantheon+ + DESI BAO | `joint_mcmc_p0` | F-COS-01, F-COS-02 |
| Fator de Bayes RLL/ΛCDM | `bayes_factor_p0` | F-COS-04 |
| z_t ∈ [0.5, 1.5] | `zt_falsification` | F-COS-03 |
| χ² DESI otimizado | `fit_desi_bao` | F-COS-05 |
| w_eff vs CPL mapeado | `weff_cpl_mapping` | — |

---

## Conformidade com Políticas CI

O pipeline passou em todos os 9 checks CI, incluindo `validate-yaml` (auditor de workflows):

- ✅ `permissions.contents: read` (top-level)
- ✅ `persist-credentials: false` (checkout)
- ✅ `actions/upload-artifact@v4` (todos os jobs de output)
- ✅ `rll_real_data_write_checksums` (via `tools/ci/real_data_workflow_policy.sh`)
- ✅ `CLAIM_BOUNDARY` em texto estático (env var)
- ✅ `SYNTHETIC_BOUNDARY` em texto estático (env var)
- ✅ `CANONICAL_REAL_DATA_WORKFLOW` apontando para canônico

---

## Adendo FASE 20 (2026-07-15)

A seção "Próximo Passo" acima e as 4 linhas `[VAZIO P0]` na tabela de Estado Epistêmico estão **superadas**. Os jobs P0 foram executados via scripts locais (equivalente funcional ao pipeline) e os resultados estão commitados:

### Estado Epistêmico — Atualizado

| Item | Estado anterior | Estado final | Evidência |
|------|----------------|-------------|-----------|
| Primeiro run concluído | ⚠️ [VAZIO P0] | ✅ [E] | FASE 20 (2026-07-15) |
| χ² otimizado DESI | ⚠️ [VAZIO P0] | ✅ [E] | χ²_joint=749.228 (FASE 16); calibração rd=−3.614 Mpc (FASE 19) |
| ln(B₁₀) RLL/ΛCDM | ⚠️ [VAZIO P0] | ✅ [E] − FAIL | ln(B₁₀)=−6.190±0.691 (dynesty nlive=150) |
| CONTRATO atualizado | ⚠️ [VAZIO P0] | ✅ [E] | `CONTRATO_FALSIFICADORES_RLL.md` — 2/5 PASS · 2/5 FAIL · 0/5 TOKEN_VAZIO |

### Resultado do job `joint_mcmc_p0`

```json
{
  "method": "emcee",
  "n_walkers": 32,
  "n_steps": 1500,
  "burn": 400,
  "n_datasets": 5,
  "N_total": 1677,
  "Omega_s0_UL95": 0.00178,
  "tau_max": 99.5,
  "N_over_tau": 11.1
}
```

Arquivo: `results/rll_fase20_mcmc_bayes.json`

### Resultado do job `bayes_factor_p0`

```json
{
  "method": "dynesty",
  "nlive": 150,
  "dlogz": 0.5,
  "ln_B10": -6.190,
  "ln_B10_err": 0.691,
  "jeffreys_scale": "very_strong_for_LCDM"
}
```

`claim_allowed = false` — por resultado empírico (FAIL), não por lacuna (TOKEN_VAZIO = 0).

---

*Auditoria de infraestrutura — o pipeline é um ato científico documentado, não apenas automação.*
