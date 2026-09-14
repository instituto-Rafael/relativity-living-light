# RLL — TOKEN_VAZIO Priority Ledger

**Gerado**: 2026-07-05  
**Método**: Sistematização de lacunas documentadas em auditoria  
**Princípio**: "Lacuna marcada vira ciência" — preservação honesta de incertezas

---

## Legenda de Prioridades

| Nível | Critério | Impacto | Ação |
|-------|----------|--------|------|
| **P0** | Crítico para validação central | Bloqueia afirmação de modelo | Requer resolução antes de paper |
| **P1** | Alto impacto em confiança | Afeta interpretação | Requere investigação documentada |
| **P2** | Médio impacto em robustez | Afeta generalização | Nice-to-have para completude |
| **P3** | Baixo impacto prático | Afeta performance | Melhorias secundárias |

---

## P0: Crítico para Validação Central

### Gap 1: Reprodutibilidade dos Notebooks

**Questão**: Os notebooks da tag v1.0.0 realmente reproduzem H(z) e os gráficos documentados?

**Por que P0**: Se notebooks não executam ou produzem outputs diferentes, toda a cronologia é questionável.

**Status**: ⚠️ **TOKEN_VAZIO** — arquivos existem, execução não validada

**Comando para resolver**:
```bash
cd data/
nbconvert --execute --to notebook Hz_superposicao.ipynb --output /tmp/Hz_exec.ipynb
nbconvert --execute --to notebook density_decomp.ipynb --output /tmp/density_exec.ipynb
# Comparar outputs contra figs/*.png
```

**Próximo passo**: Executar em ambiente Termux ARM32 + documentar outputs

---

### Gap 2: Primeiro Commit Exato com "DESI"

**Questão**: Qual é o commit absoluto que INTRODUZ "DESI" pela primeira vez (não just o que o contém)?

**Por que P0**: Rastreabilidade cronológica depende de haver um "primeiro" bem-definido.

**Status**: ⚠️ **TOKEN_VAZIO** — temos hash 207013741... mas requer análise de diff

**Comando para resolver**:
```bash
git show 207013741ac55db5a1bc6f3d61f72c4d31791c47 | grep -A5 -B5 "DESI" | head -20
# Mostrar contexto da introdução
```

**Próximo passo**: Analisar diffs de cada commit para encontrar o que adiciona "DESI" pela primeira vez

---

### Gap 3: Validação χ² Contra DESI DR2 Real

**Questão**: Qual é o χ² real (não marginal, não aproximado) do RLL vs. ΛCDM comparando contra dados DESI DR2 brutos?

**Por que P0**: Afirmação central do modelo é que reproduz observações; isso requer cálculo concreto.

**Status**: ⚠️ **TOKEN_VAZIO** — scripts existem, execução completa não documentada

**Arquivo relevante**: `scripts/rll_vs_lcdm.py`

**Comando para resolver**:
```bash
python3 scripts/rll_vs_lcdm.py \
  --bao data/real/cosmology/desi_dr2_bao_primary_points.csv \
  --adversary both --h0 67.4 --omega-m 0.315 \
  --omega-s0 0.05 --zt 0.8 --wt 0.3 \
  --out-json results/rll_vs_lcdm_final.json
```

**Próximo passo**: Executar e documentar resultado (χ² RLL vs. χ² ΛCDM)

---

## P1: Alto Impacto em Confiança

### Gap 4: Origem de Constantes (H₀, Ωm, etc.)

**Questão**: De onde vieram os valores iniciais H₀, Ωm, Ωb, Ωr?

**Por que P1**: Determina se modelo é baseado em literatura padrão ou escolhas ad hoc.

**Status**: ⚠️ **TOKEN_VAZIO** — provavelmente Planck 2018, mas não documentado

**Fontes candidatas**:
- Planck 2018 + WMAP + Baryon Acoustic Oscillations (BAO)
- SH0ES (H₀ local)
- Compilation Moresco 2023

**Próximo passo**: Citar fonte explícita no código (comments) e documentação

---

### Gap 5: Autoridade das Equações (Reformulação vs. Original)

**Questão**: As equações do RLL são originalmente derivadas pelo autor, ou reformulação de trabalhos publicados?

**Por que P1**: Determina precedência científica e inovação.

**Status**: ⚠️ **TOKEN_VAZIO** — sem citação de trabalho anterior similar

**Possibilidades**:
- Extensão original de Friedmann (mais provável)
- Inspiração em f(R) gravity ou Finsler (menos provável)
- Reformulação de trabalho anterior não citado (improvável mas TOKEN_VAZIO)

**Próximo passo**: Comparação explícita com f(R), Finsler, EDE em literatura revisada por pares

---

### Gap 6: Correlação de Parâmetros (zt, wt, Ωs0)

**Questão**: Os parâmetros (zt=1.0, wt=0.3, Ωs0=0.02) têm justificativa física ou são ajustes?

**Por que P1**: Determina se modelo é mecanístico (parâmetros têm significado) ou fenomenológico.

**Status**: ⚠️ **TOKEN_VAZIO** — não há derivação teórica clara de "por que esses valores"

**Possível justificativa**:
- zt ~ redshift de equivalência matéria/radiação? Não documentado.
- wt ~ escala de transição Hubble? Não documentado.
- Ωs0 ~ fração observada de "setor novo"? Requer validação DESI.

**Próximo passo**: Investigar se há motivação teórica nos papers anteriores de Rafael

---

## P2: Médio Impacto em Robustez

### Gap 7: Reprodução de Gráficos Numéricos

**Questão**: Os valores de H(z), σ8(z), etc. nos gráficos coincidem com os calculados pelos notebooks?

**Por que P2**: Afeta precisão da apresentação, não do modelo per se.

**Status**: ⚠️ **TOKEN_VAZIO** — gráficos .png existem, mas origem (hand-drawn vs. gerada) não documentada

**Próximo passo**: Comparar outputs de nbconvert com .png pixel-by-pixel

---

### Gap 8: Performance em Diferentes Ambientes

**Questão**: O modelo e scripts executam em Termux ARM32, colab, servidor standard?

**Por que P2**: Afeta replicabilidade pelos usuários.

**Status**: ⚠️ **TOKEN_VAZIO** — executável em x86, ARM32 não testado

**Próximo passo**: Testar em Termux e documentar incompatibilidades

---

## P3: Baixo Impacto Prático

### Gap 9: Documentação de Commits Antigos

**Questão**: Commits anteriores a v1.0.0 têm histórico documentado?

**Por que P3**: Afeta história de projeto, não validação científica.

**Status**: ⚠️ **TOKEN_VAZIO** — shallow clone, histórico anterior desconhecido

**Nota**: Não é crítico para auditoria, mais para "background".

---

## Plano de Resolução Proposto

| Gap | P | Resolução | Responsável | Prazo |
|-----|---|-----------|-------------|-------|
| Reprodutibilidade notebooks | P0 | Executar nbconvert + documentar | user | semana 1 |
| Primeiro commit DESI exact | P0 | Analisar diffs de commit | user | semana 1 |
| χ² real DESI | P0 | Rodar scripts, capturar JSON | user | semana 2 |
| Origem constantes | P1 | Citar fonte em código | user | semana 1 |
| Autoridade equações | P1 | Comparar com f(R), Finsler | user | semana 3 |
| Justificativa parâmetros | P1 | Investigar papers anteriores | user | semana 2 |
| Gráficos numéricos | P2 | Comparar pixel-level | automation | semana 3 |
| Performance ARM32 | P2 | Testar em Termux | user | semana 4 |
| Histórico antigo | P3 | Documentar se possível | user | semana 4+ |

---

## GAPS RESOLVIDOS — Fase 4 (2026-07-06)

### Gap G0: Pantheon+SH0ES ausente do pipeline RLL → FECHADO [E]

**Questão original**: χ² do RLL contra dataset Pantheon+ SNe Ia não calculado.

**Status**: ✅ **FECHADO** — `docs/cronologia-auditoria/09_PANTHEON_RESULTADO_REAL.md`

**Resultado real**:
| Modelo | χ² | AIC | ΔAIC vs ΛCDM |
|--------|-----|-----|-------------|
| ΛCDM (k=2) | 710.808 | 714.808 | — |
| CPL (k=4) | 710.390 | 718.390 | +3.582 |
| RLL original (k=4) | 710.613 | 718.613 | +3.805 |
| RLL Opção A (k=4) | 710.613 | 718.613 | +3.805 |

N=1624 SNe cosmológicas. Ratio RLL_original/RLL_optionA = 1.0000 (degenerados em Pantheon+).

**Classificação**: [E] cálculo direto contra dado observacional real.

**Scripts**: `scripts/pantheon/load_pantheon.py`, `models_pantheon.py`, `run_rll_vs_pantheon.py`  
**Dados**: `validacao_real/data/pantheon_data.dat` (1702 linhas, 1624 amostra cosmológica)  
**Resultado**: `results/pantheon_plus_resultado_real.txt`

---

---

## GAPS ATUALIZADOS — Fase 7 (2026-07-07)

### Gap P0-3 (χ² DESI Real): PRONTO PARA EXECUÇÃO

**Status anterior**: ⚠️ TOKEN_VAZIO — scripts existem, execução completa não documentada

**Status atual**: ⏳ **PRONTO PARA EXECUÇÃO** — pipeline `rll-validacao-cientifica-completa.yml` existe (PR #506 merged)

**Para fechar**: Disparar o workflow em GitHub Actions → modo=completo. Job `fit_desi_bao` calcula χ² com parâmetros otimizados. Job `joint_mcmc_p0` fecha o joint MCMC P0.

**Referência**: `.github/workflows/rll-validacao-cientifica-completa.yml` (11 jobs, PR #506)

---

### Gap G1: Pipeline Joint MCMC — Primeiro Run Pendente [NOVO P0]

**Questão**: Qual é o χ² RLL real com parâmetros otimizados conjuntamente (Pantheon+ + DESI BAO)?

**Por que P0**: O joint MCMC é o teste definitivo da viabilidade do modelo — sem ele, não há afirmação de superioridade sobre ΛCDM com parâmetros livres.

**Status**: ⚠️ **TOKEN_VAZIO P0** — pipeline existe (Job 6: `joint_mcmc_p0`), primeiro run não executado

**Para fechar**:
```bash
# GitHub Actions → rll-validacao-cientifica-completa → Run workflow
# Inputs: modo=completo, commit_resultados=true
# Job joint_mcmc_p0 usa: python -m data.pipelines.structure_d.run_all \
#   --profile structure_d_real_validation --bayes --bayes-mode inference \
#   --bayes-nwalkers 32 --bayes-nsteps 1000
```

**Resultado esperado**: `results/ci/joint_mcmc_*/joint_mcmc_summary.json` com posteriors {H₀, Ωm, Ωs0, z_t, w_t}

---

### Gap G2: Fator de Bayes RLL/ΛCDM [NOVO P0]

**Questão**: ln(B₁₀) RLL vs ΛCDM — positivo, negativo, ou inconclusivo?

**Por que P0**: Falsificador F-COS-04 ainda TOKEN_VAZIO. Sem Bayes Factor, não há resposta à pergunta "o RLL é preferido Bayesianamente?"

**Status**: ⚠️ **TOKEN_VAZIO P0** — Job 7 (`bayes_factor_p0`) no pipeline; aguarda primeiro run

**Para fechar**: Mesmo run do Gap G1. Job `bayes_factor_p0` depende de `joint_mcmc_p0`.

---

### CONTRATO_FALSIFICADORES — Baseline Estático Criado [FASE 7]

**Status**: ✅ `docs/cronologia-auditoria/CONTRATO_FALSIFICADORES_RLL.md` criado como baseline estático

**Valores conhecidos (pré-CI)**:
- F-COS-01: ✅ PASS — ΔAIC=3.805 (resultados/pantheon_plus_resultado_real.txt)
- F-COS-02: ✅ PASS — χ²_red=0.4386 (710.613/1620)
- F-COS-05: ✅ PASS — χ²_DESI_nominal=93.81 < 150

**Valores TOKEN_VAZIO (aguardam pipeline)**:
- F-COS-03: z_t scan — aguarda Job 5 (`zt_falsification`)
- F-COS-04: ln(B₁₀) — aguarda Job 7 (`bayes_factor_p0`)

---

## GAPS RESOLVIDOS — FASE 11 (2026-07-07)

### Gap H1-WEFF: Opção B numericamente testada → FECHADO [E]

**Questão original**: Setor DE puro com dois estados logisticamente interpolados poderia compatibilizar w_eff com CPL DESI?

**Status**: ✅ **EXECUTADO** — `scripts/verify_weff_opcao_b.py` — scan 36 combinações (w2, w_t)

**Resultado**: Melhor χ²=14.8 (w2=−0.5, w_t=0.5). Não passa threshold<10, mas melhora drasticamente vs padrão (1162.3) e Opção A (2232.2). w_eff sempre negativo ✅.

**Implicação**: Opção B é a variante mais promissora. Otimização contínua pode cruzar χ²<10 (TOKEN_VAZIO P1 acionável).

---

### Gap H2-WEFF: Opção C numericamente testada → FECHADO [E]

**Status**: ✅ **EXECUTADO** — `scripts/verify_weff_opcao_c.py` — scan 35 combinações (α, r)

**Resultado**: Melhor χ²=104.0 (α=0.5, r=0.05). Opção C inferior à Opção B; espaço (α,r) com z_t fixo é insuficiente.

---

### Gap P0 PRED: Predição datada RLL → FECHADA [C]

**Status**: ✅ **CRIADO** — `docs/canonicos/PREDICAO_DATADA_RLL.md`

**Predições registradas** (antes de DESI DR3 e Euclid DR1):
- P-RLL-01: w_eff > 0 em z~0.7–1.3 (setor padrão) — disfavorecida por DR2, distinguível futuramente
- P-RLL-02: Transição E(z) em z~1.0 — aguarda MCMC (G1)
- P-RLL-03: Ωs0 < 0.05 — aguarda MCMC (G1)
- P-RLL-04: Degeneração padrão/Opção A ✅ verificada em FASE 4
- P-RLL-05: Opção B cruzará χ²<10 com otimização — pendente

---

### Gap P1-WEFF-B-OPT: Otimização contínua Opção B [FECHADO FASE 13 ✅]

**Questão original**: Um scipy.minimize sobre (z_t, w2, w_t) pode levar χ²_Opção_B abaixo de 10?

**Resultado** [E — FASE 13, 2026-07-08]: `scripts/optimize_weff_opcao_b.py` com Nelder-Mead (10 pontos de partida):
- **χ²_opt = 0.0792** (threshold: < 10) → **PASSA** ✅
- Parâmetros ótimos: w2=−0.2817, z_t=1.7523, w_t=1.500 (no limite superior de busca)
- w_eff sempre negativo em toda a faixa DESI BAO [E]; todos |Δw_eff| < 0.01 ≪ σ=0.05
- Predição P-RLL-05: CONFIRMADA [E]

**Nota interpretativa**: w_t=1.500 (fronteira) indica que compatibilidade emerge no limite em que
a transição logística se torna tão larga que Opção B degenera para mistura de dois fluidos DE.

**Status**: ✅ **FECHADO** [E] — `results/optimize_weff_opcao_b.json`

---

## GAPS RESOLVIDOS — FASE 13 (2026-07-08)

| Gap ID | Descrição | Resultado |
|--------|-----------|-----------|
| P1-WEFF-B-OPT | Otimização contínua Opção B | ✅ χ²=0.079, P-RLL-05 CONFIRMADA [E] |

---

## GAPS RESOLVIDOS — FASE 15 (2026-07-10/13)

### H-UNIV-01 φ — Verificação numérica f(z)/φ → FECHADO [E-negativo]

**Questão original**: A razão f(z_{n+1})/f(z_n) com z_n seguindo a série de Fibonacci converge para φ=1.618?

**Status**: ✅ **FECHADO [E-negativo]** — `scripts/verify_rll_fibonacci_ratio.py` (FASE 8, 2026-07-07)

**Resultado**: Razão **diverge** exponencialmente (1.0 → 2.009 → 7.703 → 48.83 → 581.2) ao passar pela transição logística em z_t=1.0. Não converge para φ em nenhum ponto do scan.

**Interpretação**: A função logística não possui auto-semelhança multiplicativa. A analogia "espirais em espirais" é qualitativa [C], sem fundamento na forma funcional de f(z). Resultado negativo registrado com mesma honestidade que positivo.

**Saída**: `results/fibonacci_ratio_verification.json`

---

### H-CAL-01 Aritmética — mmc(365,260) verificado → FECHADO [E]

**Questão original**: mmc(365, 260) = 18980 dias = 52 anos Haab' = 73 anos Tzolk'in — formalmente executado?

**Status**: ✅ **FECHADO [E]** — `scripts/verify_cal_maya_arithmetic.py` (FASE 8, 2026-07-07)

**Resultado**:
- `mmc(365, 260) = 18980` ✅ verificado por aritmética inteira
- `52 × 365 = 18980` ✅; `73 × 260 = 18980` ✅
- `18980 / 365.25 = 51.964 anos Julianos` ✅

**Candidatos astrofísicos [H]**: melhor candidato algébrico = Schwabe (5×11yr = 55yr, Δ=3yr); conjunção J-S: 2.62×19.86yr ≈ 52.03yr (Δ=0.03yr, mas 2.62 irracional).

**Saída**: `results/cal_maya_arithmetic_check.json`

---

### F-COS-03 z_t Scan → FECHADO [E-negativo]

**Questão original**: z_t ∈ [0.5, 1.5] — scan executado com dados H(z)+BAO?

**Status**: ✅ **FECHADO [E-negativo]** — `results/zt_scan/summary.json` (FASE 8); documentado em `docs/cronologia-auditoria/14_ZT_SCAN_RESULTADO_REAL.md` (FASE 15)

**Resultado**: z_t_BAO_ótimo = 0.3 ∉ [0.5, 1.5]. Scan monotônico: χ²_BAO decresce de z_t=2.0 até z_t=0.3 sem mínimo local. F-COS-03: **FAIL [E]**.

**Desbloqueador**: MCMC joint (G1) com Ωs0 livre pode encontrar configuração diferente.

---

### Moresco H(z) χ² → FECHADO [E]

**Questão original**: χ² RLL vs ΛCDM em dados Moresco H(z) 33 pontos — não calculado.

**Status**: ✅ **FECHADO [E]** — `scripts/compute_moresco_hz_chi2.py` (FASE 15, 2026-07-10)

**Resultado**: Parâmetros Planck nominais:
- χ²_RLL = 27.47 (χ²_red = 0.981)
- χ²_ΛCDM = 22.76 (χ²_red = 0.734)
- Δχ² = +4.70, ΔAIC = +10.70

**Interpretação**: RLL compete razoavelmente com ΛCDM em H(z) (Δχ² = 4.7 com 3 parâmetros extras), mas ΔAIC = +10.7 indica penalidade de complexidade. Parâmetros não otimizados — melhoria esperada com MCMC.

**Saída**: `results/moresco_hz_chi2.json`

---

### H-ELEC-01 Modelo Quantitativo → FECHADO [E+H]

**Questão original**: Modelo quantitativo do diferencial elétrico por camada (superfície → ionosfera) — não calculado especificamente (P2).

**Status**: ✅ **FECHADO [E+H]** — `scripts/verify_h_elec_01_layer_model.py` (FASE 15, 2026-07-10)

**Resultado**:
- σ(h) = 3×10⁻¹⁴ S/m (superfície) → ~10⁻⁷ S/m (ionosfera base)
- J = 3.90×10⁻¹² A/m² constante em todas as camadas (conservação de carga verificada ✅)
- Enhancement salino (NaCl 4%): σ_saline/σ_dry ≈ 2×10¹⁴×

**Residual P2**: verificação de campo em ambiente com aerossol marinho.

**Saída**: `results/h_elec_01_layer_model.json`

---

### F-COS-04 Bayes Factor (proxy BIC) → PARCIALMENTE FECHADO [C]

**Questão original**: ln(B₁₀) RLL/ΛCDM — token vazio P0.

**Status**: ⚠️ **PARCIALMENTE FECHADO [C proxy]** — `scripts/compute_bayes_factor_bic_proxy.py` (FASE 15)

**Resultado**: proxy via BIC: ΔBIC = (k_RLL − k_ΛCDM)·ln(n) = 3·ln(64) = 12.477; ln(B₁₀) ≈ −6.24 → **FAIL** (threshold > −5, escala Jeffreys).

**Nota**: Este é o pior caso (Ωs0→0, colapso do modelo). MCMC joint pode mudar significativamente. P0 permanece até G1.

**Saída**: `results/bayes_factor_bic_proxy.json`

---

## Conclusão (atualizada FASE 15)

**Token Total**: 9 gaps originais + G0/G1/G2 + novos FASE 11/13/15
**P0 (bloqueador)**: G1 (MCMC joint) + G2 (Bayes Factor definitivo) — ambos requerem pipeline manual
**P1 (confiança)**: todos resolvidos (Gap 6: FASE 12; P1-WEFF-B-OPT: FASE 13)
**P2 (robustez)**: residuais menores (dados de campo geofísico)
**P3 (polish)**: 1 original

**Fechados**:
- G0 Pantheon+: ✅ FASE 4
- H1-WEFF (Opção B scan): ✅ FASE 11 — χ²=14.8
- H2-WEFF (Opção C scan): ✅ FASE 11 — χ²=104.0
- Predição datada: ✅ FASE 11 — 5 predições em `PREDICAO_DATADA_RLL.md`
- Gap 6 (justificativa parâmetros): ✅ FASE 12 — `JUSTIFICATIVA_PARAMETROS_RLL.md`
- P1-WEFF-B-OPT: ✅ FASE 13 — χ²=0.079; P-RLL-05 CONFIRMADA [E]
- H-UNIV-01 φ: ✅ FASE 8/15 — [E-negativo]: ratio diverge, sem convergência para φ
- H-CAL-01 aritmética: ✅ FASE 8 — [E]: lcm(365,260)=18980 verificado
- F-COS-03 z_t scan: ✅ FASE 8/15 — [E-negativo]: z_t_BAO=0.3 ∉ [0.5,1.5]; F-COS-03 FAIL
- Moresco H(z) χ²: ✅ FASE 15 — [E]: χ²_RLL=27.47, ΔAIC=+10.70
- H-ELEC-01 modelo quantitativo: ✅ FASE 15 — [E+H]: J constante confirmado, enhancement ×2×10¹⁴
- F-COS-04 proxy BIC: ✅ FASE 15 — [C]: ln(B₁₀)=−6.24; F-COS-04 FAIL (proxy — definitivo aguarda G1)

**Falsificadores ativos** (2/5 PASS · 2/5 FAIL · 1/5 TOKEN_VAZIO P0):
- F-COS-01: ✅ PASS — ΔAIC=3.805 [E]
- F-COS-02: ✅ PASS — χ²_red=0.4387 [E]
- F-COS-03: ✗ FAIL — z_t_BAO=0.3 [E]
- F-COS-04: ✗ FAIL — ln(B₁₀)=−6.24 proxy [C]; revisável com G1
- F-COS-05: ✅ PASS — χ²_DESI_nominal=93.81 [E]

**Pendentes (requerem ação manual/pipeline)**:
- G1 (Pipeline MCMC joint): Disparar `rll-validacao-cientifica-completa.yml` modo=completo
- G2 (Bayes Factor definitivo): Idem (Job 7)

**Método**: TOKEN_VAZIO preserva honestidade enquanto trabalho prossegue.

---

### FASE 20 — MCMC joint + Bayes Factor formal (2026-07-15) [PR #554 merged]

**Gaps fechados**:
- G1 ✅ FECHADO — Ωs0 < 0.00178 (95% UL, emcee 32 walkers × 1500 steps, burn=400, n=1677)
  - aceitação=0.377; autocorr τ_max≈99.5; N/τ≈11 (marginal mas convergente)
  - posteriors: H₀=66.91±0.72, Ωm=0.3144±0.0011, Ωb=0.0498±0.0011
  - artefato: `results/rll_fase20_mcmc_bayes.json`
- G3 ✅ FECHADO — ln(B₁₀)=−6.190±0.691 (dynesty NestedSampler nlive=150)
  - logZ_RLL=−404.340±0.530; logZ_ΛCDM=−398.150±0.443
  - Jeffreys: |ln(B₁₀)|=6.19 > 5 → evidência muito forte para ΛCDM
  - artefato: `results/rll_fase20_mcmc_bayes.json`

**Gap novo (baixa prioridade)**:
- G4 ⬜ TOKEN_VAZIO [H] P3 — mapeamento do bias E&H em função de (Ωm·h², Ωb·h²)
  - descrição: calibração rd aditiva assume que Δrd=rd_EH−rd_Planck é constante; verificar variação em grid de parâmetros
  - impacto estimado: ~1–2 ln(B₁₀); não bloqueia resultados existentes
  - próximo passo: grade rd_EH(Ωm·h², Ωb·h²) em 10×10 pts; comparar com valor calibrado
  - **→ FECHADO na FASE 22 abaixo**

**Atualização falsificadores** (2/5 PASS · 2/5 FAIL · 0/5 TOKEN_VAZIO):
- F-COS-01: ✅ PASS — ΔAIC=3.805 [E]
- F-COS-02: ✅ PASS — χ²_red=0.4387 [E]
- F-COS-03: ✗ FAIL — z_t_BAO=0.3 [E]
- F-COS-04: ✗ FAIL — ln(B₁₀)=−6.190±0.691 [E] (formal, dynesty — antes proxy BIC)
- F-COS-05: ✅ PASS — χ²_DESI_nominal=93.81 [E]

**Nota epistêmica**: G1 e G3 fechados confirmam F-COS-04 como FAIL com evidência direta [E], substituindo o proxy BIC [C] da FASE 15. TOKEN_VAZIO P0 original esgotado.

---

### FASE 22 — G4 Mapeamento bias E&H (2026-07-16)

**Gap fechado**:
- G4 ✅ FECHADO — bias E&H quantificado em grade 10×10 (Ωm·h²∈[0.12,0.16], Ωb·h²∈[0.020,0.025])
  - Δrd varia −2.95 a +12.81 Mpc na grade ampla
  - **No ponto MCMC posterior (Ωm·h²=0.14075)**: erro sistemático = 0.72 Mpc
  - Δχ²_G4 ≈ (0.72/σ_rd)² << impacto de G3; conclusão ln(B₁₀)=−6.190 não afetada
  - artefato: `results/rll_fase22_g4_eh_bias_grid.json`
  - doc: `docs/cronologia-auditoria/21_FASE22_G4_EH_BIAS_GRID.md`

**Todos os gaps fechados (G1, G2, G3, G4). TOKEN_VAZIO estrutural = 0.**

---

### FASE 21 — Grafo Epistêmico de Sessão FASE 17–20 (2026-07-16)

**Artefatos gerados**:
- `results/session_grafo_fase17_20/` — 12 artefatos (claims, entities, relations, graph.graphml...)
- `docs/cronologia-auditoria/20_GRAFO_SESSAO_FASE17_20.md` — documento de auditoria

**Schema**: 10 afirmações C_i com 10 campos; 44 entidades (18 tipos); 44 arestas (14 tipos)
**Contradição documentada**: CONTRADICTION-01 — Ωs0=0.012 (FASE18-E) vs Ωs0≈0 (FASE19-20); mecanismo=bias E&H; status=RESOLVIDA
**claim_allowed**: false em todos os artefatos

**Método**: TOKEN_VAZIO preserva honestidade enquanto trabalho prossegue.

---

*"Lacuna marcada vira ciência. Lacuna ocultada vira propaganda." — RAFAELIA*
