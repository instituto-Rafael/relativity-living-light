# Índice de Artefatos — RLL

> **Gerado**: 2026-07-20 | **FASE 25**
>
> Rastreabilidade: workflow fonte → script → diretório de saída → arquivos principais.

---

## Estrutura de Diretórios de Artefatos

```
results/
├── ci/                          — runs CI formais (por data: YYYYMMDD/)
│   ├── 20260707/                — FASE 18: rs_star calibrado
│   ├── 20260708/                — FASE 19: rd calibrado
│   ├── 20260709/                — FASE 20: MCMC + Bayes formal
│   └── 20260719/                — run mais recente
│       ├── pantheon_fit_result.json
│       ├── desi_bao_result.json
│       ├── joint_mcmc_summary.json
│       ├── bayes_factor_result.json
│       ├── full_summary.json
│       └── RELATORIO_FINAL.md
├── audit/                       — auditoria de dados reais
│   ├── real_data_materialization_audit.{csv,json,md}
│   ├── real_source_signature_verification.{json,md}
│   └── rll_audit_gap_report.{json,md}
├── dha/                         — DHA Fisher forecast
│   ├── desi_dha_pipeline_summary.json
│   ├── fisher_forecast_reference.json
│   └── ln1pz_fit*.{csv,json}
├── coerente/                    — resultados de coerência
├── session_grafo_fase17_20/     — grafo epistêmico FASE 17-20 (FASE 21)
│   ├── session_manifest.json
│   ├── claims.jsonl             — 9 afirmações C_i
│   ├── sources.bib              — 10 fontes BibTeX
│   ├── entities.jsonl           — 28+ nós tipados
│   ├── relations.jsonl          — 25+ arestas tipadas
│   ├── contradictions.jsonl     — 1 contradição resolvida
│   ├── gaps.jsonl               — G1-G4 (G1-G3 fechados, G4 aberto)
│   ├── actions.jsonl            — 5 ações documentadas
│   ├── formulas.yaml            — 6 fórmulas chave RLL
│   ├── experiments.yaml         — 3 experimentos formais
│   ├── graph.graphml            — grafo completo GraphML
│   └── report.md                — relatório de síntese
├── BAO_data_real.csv            — dados BAO reais
├── Hz_data_real.csv             — dados H(z) reais
├── RLL_chi2_results.csv         — χ² comparativos
├── bayes_factor_bic_proxy.json  — Bayes BIC proxy (FASE 19)
├── cal_maya_arithmetic_check.json — H-CAL-01 aritmética
├── desi_dr2_bao_covariance_chi2.json — χ² DESI DR2
├── evolution_watcher_manifest.json
├── fibonacci_ratio_verification.json — H-UNIV-01
├── growth_comparison_rll_vs_lcdm.{csv,json}
├── h0_grid_expansion_summary.json   — H₀ grid scan
├── h0_grid_expansion_scan.csv
├── h_elec_01_layer_model.json   — H-ELEC-01
├── manifest.json
├── moresco_hz_chi2.json         — χ² H(z) Moresco
└── OUTPUTS_TEXTUAIS_INDEX.md    — índice de outputs textuais

artifacts/
├── EVOLUTION_TRAIL.jsonl        — trilha de evolução epistemológica
├── formulas/                    — artefatos de fórmulas (gerado por formulas-artifacts.yml)
├── rafaelia_q16/                — artefatos Q16 RAFAELIA
├── rll-real-run-impact-vector/  — impacto de runs reais
└── rll_balance/                 — relatórios de balanço RLL

docs/cronologia-auditoria/
├── CONTRATO_FALSIFICADORES_RLL.md  — contrato formal F-COS-01..05
├── 11_AUDIT_FINAL_STATUS.md        — estado consolidado pós FASE 22
└── 20_GRAFO_SESSAO_FASE17_20.md    — doc 20: grafo epistêmico

data/real/cosmology/
├── pantheon_plus/
│   └── pantheon_data.dat           — 1701 SNe Ia (Pantheon+SH0ES)
└── desi_dr2_bao_primary_points.csv — 13 pontos BAO DESI DR2
```

---

## Tabela de Rastreabilidade Workflow → Artefato

| Workflow | Artefato Produzido | Localização |
|----------|-------------------|-------------|
| `rll-pipeline-linear-completo.yml` | `PIPELINE_LINEAR_LOG.md` + `CHECKSUMS.sha256` + `step_status.tsv` | `results/linear/` + artefato GitHub |
| `rll-validacao-cientifica-completa.yml` | `pantheon_fit_*.json`, `desi_bao_chi2_*.json`, `joint_mcmc_*/`, `bayes_factor_*.json`, `RELATORIO_FINAL.md`, `CONTRATO_FALSIFICADORES_RLL.md` | `results/ci/YYYYMMDD/`, `docs/cronologia-auditoria/` |
| `bayes_analysis.yml` | `ln(B₁₀)`, corner plots | `results/` + artefato GitHub |
| `desi-dr2-bao-validation.yml` | `desi_dr2_bao_covariance_chi2.json` | `results/` |
| `dha-fisher-ci.yml` | `desi_dha_pipeline_summary.json`, `fisher_forecast_reference.json` | `results/dha/` |
| `formulas-artifacts.yml` | fórmulas compiladas | `artifacts/formulas/` |
| `iml_artifact.yml` | `iml_artifact.json` | `artifacts/iml/` |
| `rll-balance-report.yml` | relatório de balanço BIC | `artifacts/rll_balance/` |
| `canonical-route-artifacts.yml` | artefatos de rota canônica | `artifacts/canonical-route/` |
| `real-data-complete-execution.yml` | `real_data_materialization_audit.*`, `real_source_signature_verification.*` | `results/audit/` |
| `repo-real-inventory.yml` | `docs/YML_WORKFLOWS_INDEX.md` | `docs/` |
| `rll-real-data-orchestrator.yml` | dados computados por domínio | `results/` |
| `raw-data-manifest-status.yml` | manifesto de dados brutos | `results/` |
| `real-seed-ingestion-plan.yml` | plano de ingestão | `results/` |
| `dense-feature-matrix.yml` | matriz de features | `results/` |
| `real-data-bootstrap-validation.yml` | resultados bootstrap | `results/` |
| `unified-geometry.yml` | geometria unificada | `results/` |
| `orbital-shape-angular-momentum-validation.yml` | validação orbital | `results/` |

---

## Artefatos de Resultados Científicos Canônicos

> Estes são os artefatos que suportam diretamente o CONTRATO_FALSIFICADORES_RLL.md.

| Resultado | Arquivo | Falsificador | Valor |
|-----------|---------|-------------|-------|
| Fit Pantheon+ (χ², ΔAIC) | `results/ci/*/pantheon_fit_result.json` | F-COS-01, F-COS-02 | ΔAIC=3.805; χ²_red=0.4387 |
| DESI BAO χ² nominal | `results/ci/*/desi_bao_result.json` | F-COS-05 | χ²_nom=93.81 |
| z_t BAO (scan) | `results/ci/*/joint_mcmc_summary.json` | F-COS-03 | z_t_BAO=0.30 → FAIL [E] |
| Bayes Factor dynesty | `results/ci/*/bayes_factor_result.json` | F-COS-04 | ln(B₁₀)=−6.190±0.691 → FAIL [E] |

**Contrato final**: `2/5 PASS · 2/5 FAIL · 0/5 TOKEN_VAZIO` → `claim_allowed = false` [por resultado empírico, não por lacuna]

---

## Artefatos do Grafo Epistêmico (FASE 21)

Localização: `results/session_grafo_fase17_20/`

| Arquivo | Conteúdo | Schema |
|---------|----------|--------|
| `session_manifest.json` | Metadados da sessão FASE 17-20 | — |
| `claims.jsonl` | 9 afirmações C_i com status epistêmico | `schemas/semantic_token_unit.schema.json` |
| `sources.bib` | 10 fontes BibTeX (Planck 2018, E&H 1998, …) | BibTeX |
| `entities.jsonl` | 28+ nós (PAPER, CODE, RESULT, CONCEPT, GAP, …) | `schemas/omega_node.schema.json` |
| `relations.jsonl` | 25+ arestas tipadas (SUPPORTS, CONTRADICTS, …) | `schemas/omega_relation.schema.json` |
| `contradictions.jsonl` | 1 contradição resolvida (Ωs0 0.012→0) | — |
| `gaps.jsonl` | G1-G4 (G1-G3 fechados, G4 aberto P3) | `data/real_sources/rll_required_data_gap_registry.yml` |
| `actions.jsonl` | 5 ações (FASE18E, FASE19, FASE20, PR553, PR554) | — |
| `formulas.yaml` | 6 fórmulas (E²(z), f(z), rd_correction, …) | — |
| `experiments.yaml` | 3 experimentos (MCMC_G1, NESTED_G3, PROFILE_FASE19) | `docs/yml/PROOF_OBLIGATION_REGISTRY.yml` |
| `graph.graphml` | Grafo completo GraphML (nós + arestas tipadas) | GraphML XML |
| `report.md` | Síntese metodológica ψ→χ→Δ→Σ | — |

---

## Artefatos de Governança

| Arquivo | Gerado por | Conteúdo |
|---------|-----------|---------|
| `artifacts/EVOLUTION_TRAIL.jsonl` | manual/scripts | Trilha de evolução de todos os artefatos |
| `docs/cronologia-auditoria/CONTRATO_FALSIFICADORES_RLL.md` | `rll-validacao-cientifica-completa.yml` Job 9 | Contrato formal F-COS-01..05 |
| `docs/cronologia-auditoria/11_AUDIT_FINAL_STATUS.md` | FASE 23 | Estado consolidado pós-FASES 20-22 |
| `docs/yml/PROOF_OBLIGATION_REGISTRY.yml` | manual | Registro de obrigações de prova |
| `docs/yml/ACADEMIC_PARAMETER_REGISTRY.yml` | manual | Registro de parâmetros acadêmicos |
| `data/real_sources/rll_required_data_gap_registry.yml` | manual | Registro de gaps de dados |

---

## Links de Navegação

- [Índice Canônico de Workflows](INDICE_CANONICO.md)
- [Mapa de Articulações](MAPA_ARTICULACOES.md)
- [Índice de Workflows (bruto/SHA256)](../../docs/YML_WORKFLOWS_INDEX.md)
- [Contrato de Falsificadores](../../docs/cronologia-auditoria/CONTRATO_FALSIFICADORES_RLL.md)
- [Audit Final Status](../../docs/cronologia-auditoria/11_AUDIT_FINAL_STATUS.md)
- [Grafo Epistêmico FASE 21](../../docs/cronologia-auditoria/20_GRAFO_SESSAO_FASE17_20.md)
- [Token Vazio Ledger](../../docs/cronologia-auditoria/06_TOKEN_VAZIO_PRIORITY_LEDGER.md)

---

*Índice de artefatos FASE 25. Atualizar quando novos runs CI produzirem resultados relevantes.*
