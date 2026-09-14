# Metodologia Coerente RLL — Documento Canônico

**Estado epistêmico:** `[E] Estabelecido` (metodologia) | `claim_allowed: false`
**Versão:** 1.0 — 2026-08-03
**Âncora de proveniência:** `data/manifests/dados_reais_fundamentais_v1.json`

> **Aviso:** Materialização de dados reais e aplicação da metodologia descrita aqui não constituem
> validação científica do modelo RLL nem autorizam qualquer claim de superioridade sobre ΛCDM, wCDM ou CPL.
> O protocolo de gating (`claim_allowed`) permanece `false` enquanto os critérios de falsificação
> definidos em `docs/canonicos/19_ROADMAP_FALSIFICADORES_RLL.md` não forem satisfeitos.

---

## Seção 1 — Catálogo de Dados Reais Fundamentais

Os dados reais fundamentais do projeto RLL compõem seis blocos observacionais verificados.
Todos possuem SHA256 registrado em `data/manifests/dados_reais_fundamentais_v1.json`
e snapshots frozen em `data/failsafe/`.

| ID canônico | Label | Arquivo local | n_obs | z_range | Estado |
|---|---|---|---|---|---|
| `hz_cosmic_chronometers` | H(z) CC Moresco 2022 | `data/real/Hz_data_real.csv` | 33 | 0.07–2.34 | VERIFIED |
| `bao_legacy` | BAO DV/rs BOSS+DESI2024 | `data/real/BAO_data_real.csv` | 10 | 0.106–2.33 | VERIFIED |
| `desi_dr2_bao` | DESI DR2 BAO + cov 13×13 | `data/real/cosmology/desi_dr2_bao_primary_points.csv` | 13 | 0.295–2.330 | VERIFIED |
| `fsigma8_rsd` | fσ8 compilação RSD | `data/real/cosmology/fsigma8_growth_real.csv` | 16 | 0.02–0.78 | VERIFIED |
| `cmb_shift_planck2018` | CMB shift Planck 2018 | `data/real/CMB_shift_real.json` | 2 scalars | z=1089.92 | VERIFIED |
| `pantheon_plus_shoes` | Pantheon+SH0ES SNe Ia | `data/real/cosmology/pantheon_plus/` | ~1700 | 0.001–2.26 | PARTIAL |

### 1.1 Proveniência das fontes primárias

- **H(z):** Moresco et al. 2022 (arXiv:2205.05701) — cronômetros cósmicos CC + BOSS Ly-α
- **BAO legacy:** 6dFGS, SDSS MGS, BOSS DR12, DESI 2024
- **DESI DR2 BAO:** arXiv:2503.14738, Tabela IV — 13 traçadores BGS/LRG/ELG/QSO/Lya
- **fσ8:** Hudson & Turnbull 2013 + Beutler 2012 + compilação multi-survey
- **CMB shift:** Chen, Huang & Wang 2019 (arXiv:1808.05724, Tabela I) — prior comprimido Planck 2018
- **Pantheon+SH0ES:** Brout et al. 2022 (arXiv:2202.04077) + Riess et al. 2022 (SH0ES)

### 1.2 Itens TOKEN_VAZIO fundamentais

Os seguintes dados ainda não estão integrados na pipeline de análise:

| Item | Razão | Próximo passo |
|---|---|---|
| Pantheon+ cov matrix (stat+sys) | Arquivo >100 MB excluído do git | Implementar modelo μ(z) em `models.py` |
| Cadeias MCMC/Cobaya | Apenas otimização pontual disponível | Configurar Cobaya com `desi_gaussian_bao_ALL_GCcomb_cov.tsv` |
| Cálculo de crescimento CLASS/CAMB | Proxy analítico em uso | Completar `src/rll/class_rll_background.c` |
| ACT DR6 lensing | Não materializado | Obter de arXiv:2304.05202 |
| Posteriors LIGO GW190814/GW230529 | Não materializado | GWOSC public data |

---

## Seção 2 — Pipeline de Análise

A metodologia completa segue o fluxo linear abaixo. Cada etapa tem implementação
rastreável no código-fonte do projeto.

```
[Dados reais verificados]
        │
        ▼
[1. INGESTÃO + VERIFICAÇÃO SHA256]
   data/pipelines/structure_d/data_access.py
   → load_active_datasets(config_path, profile_name)
   → sha256 validado contra datasets_config.json
        │
        ▼
[2. PRÉ-PROCESSAMENTO]
   → normalização de colunas (z, value, error/covariance)
   → política de duplicatas (erro | sort | primeira_ocorrencia)
   → política de covariância (prefer_full | diagonal_only | full_required)
        │
        ▼
[3. CONSTRUÇÃO DA VEROSSIMILHANÇA]
   data/pipelines/structure_d/likelihood.py
   → chi2(d, m, sigma)                     # diagonal
   → chi2_with_covariance(d, m, C)         # com matriz C⁻¹
   → chi2_cmb_shift(params, hz_model)      # CMB scalar
        │
        ▼
[4. AVALIAÇÃO DOS MODELOS]
   data/pipelines/structure_d/models.py
   → model_LCDM_Hz(z, params)
   → model_RLL_like_Hz(z, params)          # 3 parâmetros autorais: Ωs0, z_t, w_t
   → model_LCDM_bao_dv_over_rs(z, params)
   → model_RLL_like_bao_dv_over_rs(...)
   → model_LCDM_fs8 / model_RLL_like_fs8
        │
        ▼
[5. SELEÇÃO DE MODELOS]
   data/pipelines/structure_d/likelihood.py
   → aic(chi2, k) = chi2 + 2k
   → bic(chi2, k, n) = chi2 + k·ln(n)
   → estimate_log_evidence(bic)            # proxy BIC
   → bayes_factor_interpretation_contract(delta_bic)
        │
        ▼
[6. GATING DE CLAIMS]
   data/contracts/rll_falsifier_bundle_v1.json
   → gate_1: chi2_rll <= chi2_lcdm + 2
   → gate_2: delta_aic_rll < 0
   → gate_3: delta_aic_rll <= -6 (forte)
   → claim_allowed = (gate_1 AND gate_2 AND gate_3)
        │
        ▼
[RESULTADO: model_comparison.csv + reproduction_contract.json]
   results/structure_d/
```

### 2.1 Perfis de execução disponíveis

O arquivo `data/pipelines/structure_d/datasets_config.json` define os perfis:

| Perfil | Datasets ativos | Uso |
|---|---|---|
| `structure_d_default` | hz (sintético), fsigma8 (sintético) | Testes de regressão |
| `structure_d_synthetic_advanced` | hz_cov_synth, fsigma8_cov_synth | Testes com covariância |
| `structure_d_partial_real` | real_hz, real_bao | Validação parcial |
| `structure_d_real_validation` | real_hz, real_bao, real_cmb_shift, real_fsigma8 | Validação real padrão |
| `structure_d_real_growth_validation` | + real_desi_dr2_bao | Validação com DESI DR2 |
| **`structure_d_fundamentals`** | real_hz, real_bao, real_desi_dr2_bao, real_cmb_shift, real_fsigma8 | **Perfil canônico fundamental** |

**Execução do perfil canônico:**
```bash
python -m data.pipelines.structure_d.run_all \
  --profile structure_d_fundamentals \
  --covariance-policy prefer_full
```

---

## Seção 3 — Cadeia Epistêmica

O projeto usa 9 estados epistêmicos definidos em `ARCHITECTURE.md`.
A cadeia para dados reais fundamentais segue:

```
TOKEN_VAZIO
    │ (fonte identificada)
    ▼
METADATA_READY
    │ (arquivo local + SHA256)
    ▼
AUDIT_PENDING
    │ (SHA256 verificado + snapshot frozen)
    ▼
VERIFIED
    │ (dados integrados no pipeline)
    ▼
REAL_VALIDATED_BLOCKED   ← estado atual de todos os runs reais
    │ (resultados mostram ΛCDM preferido; Ωs0 → 0)
    │ (aguardando: MCMC, Pantheon+, CLASS/CAMB growth)
    ▼
CLAIM_ALLOWED            ← requer gates 1+2+3 positivos
```

### 3.1 Estado atual dos runs reais (2026-08-03)

Resultado do run mais completo (`results/structure_d/joint_real_likelihood.json`):

| Modelo | χ² | AIC | ΔAIC vs ΛCDM | k |
|---|---|---|---|---|
| ΛCDM | 93.95 | 103.95 | — | 5 |
| wCDM | 92.79 | 104.79 | +0.84 | 6 |
| CPL | 63.10 | 77.10 | **-26.85** | 7 |
| RLL | 93.96 | 109.96 | **+6.01** | 8 |

**Diagnóstico central:** Ωs0 → 0.0 no best-fit de todos os runs. O setor RLL colapsa para ΛCDM.
Artefato de fronteira H0 = 60.0 km/s/Mpc documentado em `data/real/cosmology/h0_grid_expansion.yml`.

---

## Seção 4 — Protocolo de Falsificação

O protocolo completo está em `docs/canonicos/19_ROADMAP_FALSIFICADORES_RLL.md`.
Os caminhos de validação prioritários são:

| ID | Observable | Status | Dado necessário |
|---|---|---|---|
| C00 | H(z) CC | VERIFIED | `Hz_data_real.csv` — integrado |
| C01 | BAO BOSS+DESI | VERIFIED | `BAO_data_real.csv` — integrado |
| C02 | CMB shift | VERIFIED | `CMB_shift_real.json` — integrado |
| C03 | fσ8 RSD | VERIFIED | `fsigma8_growth_real.csv` — integrado |
| C04 | DESI DR2 BAO anisotropo | VERIFIED (parcial) | `desi_dr2_bao_primary_points.csv` — integrado |
| C05 | Pantheon+SH0ES SNe Ia | TOKEN_VAZIO | Modelo μ(z) pendente |
| C06 | Lensing ACT DR6 | TOKEN_VAZIO | Dados não materializados |
| C07 | MCMC marginalização | TOKEN_VAZIO | Cobaya/MontePython |
| C08 | Growth structure CLASS | TOKEN_VAZIO | `class_rll_background.c` incompleto |

O conjunto de modelos adversariais definido é:
**A_RLL** = {ΛCDM, w0waCDM, GEDE, Anton-Schmidt, viscous, interacting DE, EFT/MG, standard plasma, axion/photon}

---

## Seção 5 — Conexão com a Topologia de Conhecimento

### 5.1 Floresta de Conhecimento (Route Forest)

O arquivo `data/knowledge_forest/rll_route_forest_blueprint.json` define a topologia estrutural
do conhecimento como um grafo de árvores com vetores 7D:

```
D1: origin_provenance       — Origens, linhagem, referências imutáveis
D2: semantic_coherence      — Significados estáveis, estados epistêmicos
D3: geometric_dimensional   — Unidades, domínios, transformações
D4: runtime_execution       — Workflows executáveis, gates, recibos
D5: temporal_state_memory   — Histórico append-only, precedência
D6: rights_security         — Licença, privacidade, autoria
D7: evidence_falsification  — Observáveis, baselines, falsificadores
```

Escala: `[absent=0, gap=1, partial=2, ready_for_test=3, verified=4]`
Normalização: `score_component = raw / 4`

As novas árvores adicionadas por este documento:
- **T-REAL-DATA**: âncora os 6 datasets reais como nós VERIFIED na topologia
- **T-METHODOLOGY**: representa as etapas do pipeline como nós verificáveis

### 5.2 Registro de Equações

O arquivo `rll_equation_registry.yml` conecta cada equação matemática do modelo RLL aos:
- `real_data_validators`: datasets que testam a equação empiricamente
- `methodology_phase`: fase do pipeline onde a equação é aplicada

A equação central ausente `rll_friedmann_e2` foi adicionada:
```
E²(a) = Ωr a⁻⁴ + Ωm a⁻³ + ΩΛ
      + Ωs0 [f(a) + (1-f(a)) a⁻³]
      + ΩB0 a⁻⁴ + ΩP0 a⁻⁴

f(z) = 1 / (1 + exp((z - z_t) / w_t))
```

Limite nulo: quando Ωs0 = ΩB0 = ΩP0 = 0, E²(a) → ΛCDM exato (testável, verificável).

### 5.3 Vetor 7D dos dados reais na topologia

Cada dataset real recebe um vetor 7D de scores na floresta de conhecimento.
Exemplo para `N-RD-HZ` (H(z) CC Moresco 2022):

```
D1 origin_provenance:    4  (SHA256 verified, arXiv:2205.05701, FROZEN snapshot)
D2 semantic_coherence:   4  (observable H(z) bem definido, unidades km/s/Mpc)
D3 geometric_dim:        4  (z_range [0.07, 2.34], σ_H per point)
D4 runtime_execution:    4  (integrado em pipeline, reprodutível)
D5 temporal_memory:      3  (snapshot frozen, sem ledger append-only completo)
D6 rights_security:      3  (dados públicos, licença implícita CC-BY)
D7 evidence_falsif:      4  (33 pontos, falsifica H(z) do modelo diretamente)
```

---

## Seção 6 — Limitações Atuais e Próximos Passos

### 6.1 Limitações conhecidas

1. **Artefato H0 = 60 km/s/Mpc**: O otimizador (`differential_evolution`) converge para a fronteira
   inferior do prior H0. Causa raiz documentada em `data/real/cosmology/h0_grid_expansion.yml`.
   Solução: prior gaussiano H0 ~ N(67.4, 0.5) baseado em Planck 2018.

2. **Ωs0 → 0 em todos os runs reais**: O setor RLL colapsa ao limite nulo. Diagnóstico:
   os dados atuais são consistentes com ΛCDM; a hipótese de superposição fotônica Ωs0 não
   encontra evidência observacional nos dados integrados.

3. **Crescimento de estrutura via proxy analítico**: `model_RLL_like_fs8` usa aproximação
   `fσ8 ≈ 0.55 · Ωm(z)^0.55 · σ8`, não o cálculo completo de perturbações via Boltzmann code.

4. **Ausência de Pantheon+SH0ES no pipeline**: ~1700 SNe Ia não contribuem para χ² total.

5. **Sem marginalização MCMC**: Apenas otimização pontual via `scipy.optimize.differential_evolution`.
   AIC/BIC são estimativas; sem posteriors marginalizados.

### 6.2 Próximos passos ordenados por impacto

| Prioridade | Tarefa | Arquivo alvo |
|---|---|---|
| 1 | Corrigir prior H0 no otimizador | `data/pipelines/structure_d/run_all_real.py` |
| 2 | Implementar modelo μ(z) SNe Ia | `data/pipelines/structure_d/models.py` |
| 3 | Integrar Pantheon+ no pipeline | `datasets_config.json` + `run_all_real.py` |
| 4 | Configurar Cobaya com DESI DR2 cov | `data/real/cosmology/desi_bao_dr2_cobaya/` |
| 5 | Completar CLASS/CAMB growth stub | `src/rll/class_rll_background.c` |

---

*Documento gerado em 2026-08-03. Parte da topologia estrutural de conhecimento do projeto
Relativity Living Light (DOI: 10.5281/zenodo.17188137). Autor: Rafael Melo Reis / Instituto Rafael.*
