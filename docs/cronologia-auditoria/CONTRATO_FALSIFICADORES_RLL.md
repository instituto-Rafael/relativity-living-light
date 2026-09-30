# CONTRATO DE FALSIFICADORES — RLL v0.1.0

**Data**: 20260806 | **Pipeline**: rll-validacao-cientifica-completa | **Run**: 31066012098 | **Commit**: 3191a1d2

> *"Um modelo científico que não pode ser falsificado não é ciência — é dogma."* — RAFAELIA

## Status Geral

| PASS | FAIL | TOKEN_VAZIO |
|------|------|-------------|
| 1/5 | 0 | 4 |

## Falsificadores Ativos

| ID | Descrição | Threshold | Resultado CI | Status |
|----|-----------|-----------|-------------|--------|
| F-COS-01 | ΔAIC(RLL−ΛCDM) < +10 — Pantheon+SH0ES | `ΔAIC < 10` | TOKEN_VAZIO | ⚠️ TOKEN_VAZIO |
| F-COS-02 | χ²_Pantheon/dof < 1.05 — RLL original | `χ²_red < 1.05` | TOKEN_VAZIO | ⚠️ TOKEN_VAZIO |
| F-COS-03 | z_t ∈ [0.5, 1.5] — scan C01 slingshot | `0.5 ≤ z_t ≤ 1.5` | TOKEN_VAZIO | ⚠️ TOKEN_VAZIO |
| F-COS-04 | ln(B₁₀) RLL/ΛCDM > −5 — escala Jeffreys | `ln(B₁₀) > −5` | TOKEN_VAZIO P0 | ⚠️ TOKEN_VAZIO |
| F-COS-05 | χ²_DESI DR2 BAO < 150 (parâmetros nominais) | `χ²_nominal < 150` | 93.81 | ✅ PASS |

## P0 Desbloqueadores

| Gap | Status | Método |
|-----|--------|--------|
| Joint MCMC Pantheon+ + DESI BAO | ✅ FECHADO | Structure-D inference (emcee 32×1000) |
| Fator de Bayes RLL/ΛCDM | ⚠️ TOKEN_VAZIO | BIC proxy (ln B ≈ −ΔBIC/2) |

## Rastreabilidade de Artefatos

| Artefato | Job | Arquivo CI |
|----------|-----|------------|
| Fit Pantheon+ | fit_pantheon_rll | artifacts/pantheon_fit/pantheon_fit_result.json |
| DESI BAO χ² | fit_desi_bao | artifacts/desi_bao/desi_bao_result.json |
| w_eff CPL | weff_cpl_mapping | artifacts/weff_mapping/weff_cpl_mapping.json |
| Scan z_t | zt_falsification | artifacts/zt_falsification/zt_result.json |
| MCMC conjunto | joint_mcmc_p0 | artifacts/joint_mcmc/joint_mcmc_summary.json |
| Bayes Factor | bayes_factor_p0 | artifacts/bayes_factor/bayes_factor_result.json |

## Claim Boundary

> Documento gerado automaticamente pelo pipeline CI. Resultados `TOKEN_VAZIO` indicam
> gaps epistêmicos ainda não fechados. Nenhuma afirmação de superioridade do modelo RLL
> pode ser feita sem revisão por pares dos artefatos completos.
> Referência canônica: `.github/workflows/real-data-complete-execution.yml`

---
*Gerado em 2026-08-06T02:40:27.206571+00:00 por rll-validacao-cientifica-completa*