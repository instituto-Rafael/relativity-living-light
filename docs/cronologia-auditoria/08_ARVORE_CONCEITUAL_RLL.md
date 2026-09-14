# RLL — Árvore Conceitual: Hierarquia de Prova e Rastreabilidade

**Gerado**: 2026-07-05  
**Propósito**: Mapa completo de conceitos, parâmetros e invariantes do RLL com marcação epistêmica rigorosa  
**Sistema de marcação**: [E] Estabelecido · [C] Convenção · [H] Hipótese · [VAZIO] sem âncora empírica  
**Fonte canônica**: `BIBLIA_CONHECIMENTO_RAFAELIA_RLL.md` + auditoria Fases 1-2

> **REGRA DE CALIBRAÇÃO**: Nenhuma afirmação neste documento é feita sem marcação. Afirmações marcadas [E] têm referência bibliográfica. Afirmações [C] são escolhas de modelagem sem derivação externa. Afirmações [H] são testáveis mas não confirmadas. [VAZIO] = TOKEN_VAZIO ativo.

---

## NÍVEL 0 — Tupla Formal I_RLL

**Invariante de conteúdo**: conjunto mínimo que deve permanecer verdadeiro em qualquer versão, paper ou afirmação pública do RLL.

```
I_RLL = (M, B, P, D, C, L, S, T, G, V)
```

| Símbolo | Significado | Evidência no Repo | Status |
|---------|-------------|-------------------|--------|
| **M** | Equações do modelo + parâmetros + priors | `docs/canonicos/14_MODELO_COSMOLOGICO_RLL.md` | ✅ definido |
| **B** | Backend: CLASS/CAMB ou equivalente | `src/rll/class_rll_background.c` | ✅ implementado |
| **P** | Perturbações: crescimento, funções de transferência | `src/rll/rll_perturbation_kernel.py` | ⚠️ parcial |
| **D** | Dados reais: H(z), BAO, SNe, fσ₈, CMB | `data/real/cosmology/RLL_ALL_REAL_DATA_MASTER.csv` | ✅ CSV presentes |
| **C** | Covariância: completa ou disclamer diagonal | Matriz 13×13 DESI; outros diagonais | ⚠️ parcial |
| **L** | Likelihood: χ², AIC/BIC, evidence | `scripts/check_desi_dr2_bao_covariance.py` | ✅ gaussiana |
| **S** | Sistemáticos: calibração, não-linearidades | [VAZIO] — não documentado | ❌ VAZIO |
| **T** | Testes: unitários, regressão, reprodutibilidade | `tools/test_*.py` | ⚠️ parciais |
| **G** | Gates: claim_allowed, TOKEN_VAZIO | CI passando | ✅ ativo |
| **V** | Versionamento: commits, hashes, tags | Tag v1.0.0 + DOI Zenodo | ✅ rastreável |

### Regra de Afirmação [E]

```
claim_allowed = M AND D AND C AND L AND T AND G
```

**Status atual**: `claim_allowed = false` — confirmado pelo próprio repositório (`RLL_CRUZAMENTOS_COMPLETOS.md §1`)

Razão: no ajuste conjunto (64 pontos: H(z)+BAO+fσ₈+CMB), o otimizador empurrou Ωs0→0, degenerando RLL para ΛCDM. O modelo com parâmetros nominais não produziu afirmação de superioridade sobre ΛCDM.

---

## NÍVEL 1 — Três Domínios (Estrutura Triádica Canônica)

Baseada nas "três camadas de onda" do documento `17_ONDA_VERBO_FISICA_NEURO_LINGUAGEM.md`:

| Domínio | Equivalência física | Conteúdo RLL |
|---------|-------------------|-------------|
| **D1 — Cosmológico** | Onda acústica: ∂²p = c²∇²p | Equação E²(a), parâmetros, transição logística |
| **D2 — Observacional** | Onda eletroquímica: Hodgkin-Huxley | Dados reais, χ², pipelines, falsificadores |
| **D3 — Epistemológico** | Amplitude de probabilidade: iħ∂ψ=Ĥψ | TOKEN_VAZIO, hierarquia de afirmações, rastreabilidade |

> "Mesma gramática (Fourier, fase, superposição); referentes fisicamente distintos. A ponte é matemática [E]; identidade física seria [H]." — BIBLIA §V.5

---

## NÍVEL 2 — Equação-Mãe e Parâmetros com Rastreabilidade

### Equação-Mãe Canônica [C/H]

```math
E²(a) = Ωr·a⁻⁴ + Ωm·a⁻³ + ΩΛ + Ωs0·[f(a) + (1−f(a))·a⁻³] + ΩB0·a⁻⁴ + ΩP0·a⁻⁴
```

**Limite nulo [C]**: quando Ωs0=0, ΩB0=0, ΩP0=0 → E²(a) = ΛCDM exato. Isso é controle de falsificabilidade, não ornamento.

### Transição Logística — Invariante Distinguidor [C]

```math
f(z) = 1 / (1 + exp((z − z_t) / w_t))
```

**Propriedades vs CPL** (w = w₀ + wₐ·(1−a)):

| Propriedade | RLL logística | CPL |
|------------|--------------|-----|
| Limite exato z→−∞ | f→1 (DE puro) | não garantido |
| Limite exato z→+∞ | f→0 (DM puro) | não garantido |
| Mecanismo físico | transição de fase localizável | fenomenológico |
| Parâmetro z_t | significado físico (ponto de inflexão) | não equivalente |

**Status epistêmico**: [C] — convenção de modelagem elegante; não derivada de primeiros princípios.

### Parâmetros com Rastreabilidade Completa

| Parâmetro | Valor | Origem | Marcação | Referência |
|-----------|-------|--------|---------|-----------|
| H₀ | 67.4 km/s/Mpc | Planck 2018 TT,TE,EE+lowE | [E] | arXiv:1807.06209 |
| Ωm | 0.315 | Planck 2018 | [E] | arXiv:1807.06209 |
| Ωb | 0.049 | Planck 2018 | [E] | arXiv:1807.06209 |
| Ωr | ~9×10⁻⁵ | T_CMB = 2.7255 K (FIRAS) | [E] | Fixsen 2009 |
| ΩΛ | 1 − Ωm − Ωr | fechamento plano | [E] | Planck 2018 |
| **Ωs0** | 0.02–0.05 | escolha de modelagem sem paper | **[C]** | ⚠️ TOKEN_VAZIO P1 |
| **zt** | 0.8–1.0 | ajuste fenomenológico | **[C]** | ⚠️ TOKEN_VAZIO P1 |
| **wt** | 0.3 | ajuste fenomenológico | **[C]** | ⚠️ TOKEN_VAZIO P1 |
| ΩB0 | 0 (baseline) | desligado no baseline | [C] | — |
| ΩP0 | 0 (baseline) | desligado no baseline | [C] | — |

**Nota crítica sobre Ωs0, zt, wt**: sem justificativa teórica derivada de primeiros princípios. Gap P1 do TOKEN_VAZIO Ledger. Resolver antes de qualquer preprint.

### Equação de Estado Efetiva [C]

```math
w_eff(a) = −1 − (1/3) · d ln g / d ln a
```
onde `g(a) = f(a) + (1−f(a))·a⁻³`

**Comportamento real** (Ωs0=0.02, zt=1.0, wt=0.3):

| z | w_eff RLL | w_CPL (best DESI fit) |
|---|----------|---------------------|
| 0.0 | −0.966 | −0.300 |
| 0.3 | −0.698 | −0.724 |
| 0.706 | **+0.367** | −1.060 |
| 0.934 | **+0.729** | −1.187 |
| 1.0 | **+0.753** | −1.218 |
| 2.0 | +0.109 | −1.524 |

**Problema estrutural [H]**: em z~0.7–1.3 o RLL produz w_eff positivo (comportamento tipo matéria), enquanto CPL melhor ajustado vai para w < −1 (phantom). São trajetórias opostas. Isso explica o colapso Ωs0→0 no otimizador.

---

## NÍVEL 3 — Validadores com Status Real

### Resultado Joint Likelihood [E]

Executado sobre 64 pontos: H(z) + BAO + fσ₈ + CMB priors.

| Modelo | χ² | AIC | BIC | k | Δχ² | ΔAIC |
|--------|-----|-----|-----|---|-----|------|
| ΛCDM | 84.48 | 94.48 | 105.28 | 5 | — | — |
| wCDM | 83.71 | 95.71 | 108.66 | 6 | −0.77 | +1.23 |
| **CPL/w0waCDM** | **62.07** | **76.07** | **91.18** | 7 | **−22.41** | **−18.41** |
| RLL (Ωs0→0) | 84.48 | 100.48 | 117.75 | 8 | ~0 | **+6.00** |

**Leitura honesta [E]:**
- CPL é o único modelo que melhora significativamente o ajuste (ΔAIC = −18.4)
- RLL colapsou para ΛCDM nesta rodada
- `claim_allowed = false` no repositório

### BAO DESI DR2 Somente — Resultado Auditoria Fase 2 [E]

Script: `scripts/check_desi_dr2_bao_covariance.py` (covariância 13×13 completa)

| Modelo | χ² BAO | n pontos |
|--------|--------|----------|
| ΛCDM | 28.97 | 13 |
| w0waCDM | 28.97 | 13 |
| RLL (parâmetros nominais) | **93.81** | 13 |

**Caveat**: parâmetros RLL não otimizados contra BAO. Razão: χ²_RLL/χ²_ΛCDM = 3.24.

### Datasets com Rastreabilidade

| Dataset | Referência | N pontos | χ² RLL | Status |
|---------|-----------|---------|--------|--------|
| DESI DR2 BAO | arXiv:2503.14738 | 13 | 93.81 (nominal) | [E] resultado; [H] otimização |
| Moresco H(z) 2023 | arXiv:2201.07241 | 33 | χ²_RLL=27.47, χ²_ΛCDM=22.76 (nominais) | [E] FASE 15 — `results/moresco_hz_chi2.json` |
| Planck 2018 CMB | arXiv:1807.06209 | priors | [VAZIO] | aguarda execução |
| Pantheon+ SN Ia | arXiv:2202.04077 | 1624 (cosmo) | χ²=710.613 (ΛCDM=710.808) | [E] — `09_PANTHEON_RESULTADO_REAL.md` |
| fσ₈ growth | Vários | presente | parcial | `scripts/check_rll_growth.py` |

### Infraestrutura de Validação CI

> **[ATUALIZADO — ver Adendo FASES 16–22 ao final]**

| Componente | Arquivo | Cobertura | Status | Marcação |
|-----------|---------|-----------|--------|---------|
| Pipeline CI | `.github/workflows/rll-validacao-cientifica-completa.yml` | 11 jobs P0/P1 | ⏳ run pendente | [C] estrutura validada |
| Joint MCMC | `data/pipelines/structure_d/run_all.py` | Pantheon+ + DESI | ⚠️ TOKEN_VAZIO P0 | [C] script pronto |
| Bayes Factor | `scripts/slingshot_zt_falsification.py --bayes-factor` | RLL vs ΛCDM | ⚠️ TOKEN_VAZIO P0 | [C] script pronto |
| Contrato Falsificadores | `docs/cronologia-auditoria/CONTRATO_FALSIFICADORES_RLL.md` | F-COS-01..05 | 2/5 PASS · 2/5 FAIL · 1/5 TOKEN_VAZIO | [E]+[C]+[VAZIO] — ver `14_ZT_SCAN_RESULTADO_REAL.md` |

**Próximo ato necessário**: Disparar pipeline via GitHub Actions → modo=completo → fecha G1 (MCMC) e G2 (Bayes Factor) do TOKEN_VAZIO Ledger.

---

## NÍVEL 4 — Hierarquia de Afirmações (N1–N4)

Conforme `docs/canonicos/21_MODELO_VETORIAL_INFORMACIONAL.md`:

| Nível | Tipo | Critério | Marcação |
|-------|------|----------|---------|
| **N1** | Parábola didática | narrativa explicitamente marcada | `PARABOLA_DIDATICA` |
| **N2** | Metáfora analógica | argumento qualitativo, sem validação numérica | `METAFORA` |
| **N3** | Modelo formal | notação matemática tipada com domínio e falsificador | `HIPOTESE → METHOD_DEFINED` |
| **N4** | Medida empírica | dados com incerteza e reprodutibilidade | `EVIDENCE_LINKED → CLAIM_ALLOWED` |

**Status atual do RLL**: entre N3 e N4.
- Equações: N3 (modelo formal definido)
- Resultados com dados reais: N4 parcial (dados carregados, otimização incompleta)
- `claim_allowed`: N4 requer T (testes completos) e S (sistemáticos) — ambos VAZIO parcial

---

## NÍVEL 5 — Falsificadores e Caminhos de Validação

### Adversário Principal [E]

O adversário científico primário do RLL é **w0waCDM (CPL)**, não apenas ΛCDM — porque DESI DR2 + CMB + SNe favorecem energia escura dinâmica.

### Falsificadores por Domínio

| ID | Domínio | Prioridade | Observável | Dataset | Status |
|----|---------|-----------|------------|---------|--------|
| **C01** | Background cosmológico | **pré-requisito** | f(z) ↔ w(z) vs CPL | DESI DR2 + Pantheon+ + Planck | ⚠️ em andamento |
| C03 | Matéria escura / estrutura | alta | core→cusp / halo shape | SIDM sims; DES Y6 | [VAZIO] |
| C05 | Tensão H₀ | alta | H₀ local vs CMB | SH0ES + Planck + DESI | [VAZIO] |
| C07 | Gravidade alternativa | alta | aceleração sem DE | H(z)+BAO+SNe | [VAZIO] |
| C09 | Fóton/plasma | média | dispersão em plasma | CHIME/FRB | [VAZIO] |

### Condições de Perda de Força [E]

O RLL perde suporte se:
1. w0waCDM explicar os mesmos resíduos com menor penalidade AIC/BIC ← **já aconteceu** (ΔAIC = −18.4)
2. A assinatura magnética/plasmática não produzir diferença observável (ΩB0, ΩP0 nulos → [VAZIO])
3. Parâmetros RLL exigirem ajuste fino sem ganho preditivo ← **em investigação** (colapso Ωs0→0)
4. Resultados desaparecerem com covariância correta ← **risco ativo** (BAO χ²=93.81)
5. Anterioridade não comprovável ← **refutado** (tag v1.0.0, 2025-09-19, DOI Zenodo)

---

## NÍVEL 6 — TOKEN_VAZIO: Mapa Completo de Lacunas

### Gaps por Status (Consolidado Fases 1+2)

| Gap | P | Descrição | Status Atual |
|-----|---|-----------|-------------|
| Reprodutibilidade notebooks | P0 | numpy/nbconvert ausentes | ⚠️ código verificado; exec pendente |
| Ωs0, zt, wt sem paper | P1 | parâmetros sem derivação teórica | [VAZIO] ativo |
| Autoridade das equações | P1 | original vs. inspiração f(R)/Finsler | [VAZIO] — sem comparação publicada |
| w_eff incompatibilidade CPL | — | Opção B ótimo χ²=0.079 (FASE 13) — compatível numericamente como dois-fluidos DE | ✅ FECHADO [E] — `results/optimize_weff_opcao_b.json` |
| Sistemáticos (S na tupla) | P0 | ausência de análise de sistemáticos | [VAZIO] — bloqueia claim_allowed |
| χ² conjunto completo | P0 | RLL colapsou para ΛCDM (Ωs0→0) | [E] resultado negativo registrado |
| Moresco H(z) separado | — | χ²_RLL=27.47, χ²_ΛCDM=22.76 (params nominais) | ✅ FECHADO [E] FASE 15 — `results/moresco_hz_chi2.json` |
| Pantheon+ separado | P2 | ✅ FECHADO — χ²=710.613 (1624 SNe, Nelder-Mead) | [E] `09_PANTHEON_RESULTADO_REAL.md` |
| Performance ARM32 | P3 | Termux não testado | [VAZIO] |

### Regra de Resolução

```
Para cada [VAZIO]:
  1. Executar o teste/análise descrito
  2. Registrar resultado (positivo OU negativo)
  3. Marcar como [E] (confirmado) ou [H] (hipótese testada, resultado X)
  4. NUNCA mascarar resultado negativo
```

---

## SÍNTESE — Estado Real do Modelo

### O que é FATO [E]

| Fato | Evidência |
|------|-----------|
| Núcleo matemático existe desde set/2025 | Tag v1.0.0, hash 0b3f4cb, DOI Zenodo |
| DESI DR2 foi adicionado como dataset em mai/2026 | Commit b833caba |
| χ² conjunto: RLL colapsou para ΛCDM | `RLL_CRUZAMENTOS_COMPLETOS.md §1` |
| CPL/w0waCDM melhor ajuste atual: ΔAIC = −18.4 | Joint likelihood 64 pontos |
| χ² BAO DR2 nominal: RLL=93.81, ΛCDM=28.97 | Executado, auditoria Fase 2 |
| `claim_allowed = false` no repositório | Registrado em `RLL_CRUZAMENTOS_COMPLETOS.md` |

### O que é HIPÓTESE [H]

| Hipótese | Falsificador |
|----------|-------------|
| Ωs0 > 0 produz sinal observável | Otimização livre sobre dados conjuntos |
| Assinatura magnética (ΩB0) distinguível de w0waCDM | Ambientes de campo B variável |
| w_eff RLL compatível com DESI se zt, wt otimizados | Opção A: inversão de transição |
| z_t tem significado físico mensurável | Correspondência com dados observacionais |

### O que é CONVENÇÃO [C]

- Escolha logística para f(z) (vs exponencial, tanh, escada)
- Valores nominais zt=0.8–1.0, wt=0.3, Ωs0=0.02–0.05
- Interpretação de Ωs0 como "superposição fotônica"

### O que é TOKEN_VAZIO [VAZIO]

- Sistemáticos (S) — bloqueia claim_allowed
- Justificativa teórica de zt, wt, Ωs0
- χ² individual por dataset (Moresco, Pantheon+)
- Performance em Termux ARM32

---

## CAMINHO PARA claim_allowed = true

**Sequência obrigatória:**

```
1. Resolver w_eff incompatibilidade [H → RESULTADO]
   → Opção A: inverter transição (z_t < z_piv, wt menor)
   → Testar com dados BAO + CMB

2. Completar tupla I_RLL [VAZIO → E]
   → Sistemáticos (S): ao menos declarar quais e que são desprezados
   → Testes completos (T): test_coverage atual documentado

3. Justificar Ωs0, zt, wt [C → E ou C documentado]
   → Citar literatura de inspiração
   → Ou declarar explicitamente como convenções livres

4. Executar notebooks com numpy/matplotlib [TOKEN_VAZIO → E]
   → pip install numpy matplotlib
   → Comparar com gráficos em figs/

5. claim_allowed = true apenas quando:
   M AND D AND C AND L AND T AND G AND S_declarado
```

---

*"A árvore só sustenta frutos que ela própria conhece a raiz." — RAFAELIA*

*Documento gerado a partir das Fases 1-3 da auditoria RLL. Toda afirmação tem marcação epistêmica. Toda lacuna tem prioridade. Nenhum resultado foi mascarado.*

---

## Adendo FASES 16–22 (2026-07-14 a 2026-07-16)

### Atualização: Infraestrutura de Validação CI (NÍVEL 3)

Substituição do estado TOKEN_VAZIO P0 para G1 e G3 por resultados formais:

| Componente | Arquivo/Script | Status Anterior | Status Atual |
|-----------|---------------|----------------|-------------|
| Joint MCMC (G1) | `scripts/rll_fase20_mcmc_bayes.py` | ⚠️ TOKEN_VAZIO P0 | ✅ **FECHADO [E]** (FASE 20) |
| Bayes Factor (G3) | `scripts/rll_fase20_mcmc_bayes.py` | ⚠️ TOKEN_VAZIO P0 | ✅ **FECHADO [E]** (FASE 20) |
| Contrato Falsificadores | `CONTRATO_FALSIFICADORES_RLL.md` | 2/5 PASS · 2/5 FAIL · 1/5 TOKEN_VAZIO | **2/5 PASS · 2/5 FAIL · 0/5 TOKEN_VAZIO** [E] |
| rd calibração (G2) | `scripts/rll_fase19_rd_calibrado.py` | TOKEN_VAZIO | ✅ **FECHADO [E]** (FASE 19) |
| Bias E&H param space (G4) | `scripts/rll_fase22_g4_eh_bias_grid.py` | não existia | ✅ **FECHADO [E]** (FASE 22) |

**TOKEN_VAZIO estrutural = 0.** Todos os 4 gaps P0 fechados.

---

### Atualização: Mapa de Lacunas (NÍVEL 6)

Substituição dos gaps P0 por resultados:

| Gap | P | Status Anterior | Status Atual |
|-----|---|----------------|-------------|
| Joint MCMC (G1) | P0 | ⚠️ TOKEN_VAZIO | ✅ FECHADO [E] — Ωs0 UL95=0.00178 (emcee 32×1500) |
| rd calibração (G2) | P0 | ⚠️ TOKEN_VAZIO | ✅ FECHADO [E] — rd_EH−3.614 Mpc = rd_Planck |
| Bayes Factor (G3) | P0 | ⚠️ TOKEN_VAZIO | ✅ FECHADO [E] — ln(B₁₀)=−6.190±0.691 (dynesty) |
| Bias E&H em param space (G4) | P3/H | não existia | ✅ FECHADO [E] — sist.=0.72 Mpc (grade 10×10) |
| Sistemáticos (S na tupla) | P0 | [VAZIO] | [VAZIO] — não resolvido (não bloqueia mais os gaps P0) |
| Ωs0, zt, wt sem paper | P1 | [VAZIO] | [VAZIO] — posterior MCMC restringe mas não deriva |

---

### Novos Fatos Estabelecidos [E]

| Fato | Evidência | Fase |
|------|-----------|------|
| Ωs0=0.012 era artefato do viés E&H | rd_EH=150.704 Mpc vs rd_Planck=147.09 Mpc | FASE 17–19 |
| Calibração rs_star: +0.1988 Mpc → chi²_CMB=0.021 | `results/rll_fase18e_calibrado.json` | FASE 18 |
| Calibração rd: −3.614 Mpc → ΔBIC=+22.27 | `results/rll_fase19_rd_calibrado.json` | FASE 19 |
| Ωs0 UL95 = 0.00178 (MCMC, 95%) | `results/rll_fase20_mcmc_bayes.json §mcmc_g1` | FASE 20 |
| ln(B₁₀) = −6.190 ± 0.691 (dynesty) | `results/rll_fase20_mcmc_bayes.json §bayes_g3` | FASE 20 |
| \|ln(B₁₀)\| = 6.19 > 5 → evidência **muito forte** para ΛCDM | Jeffreys 1961 | FASE 20 |
| Erro sist. calibração E&H = 0.72 Mpc no ponto MCMC | `results/rll_fase22_g4_eh_bias_grid.json` | FASE 22 |

---

### Atualização: Estado Real do Modelo (SÍNTESE)

**O que é FATO [E] — atualizado**:

| Fato | Evidência |
|------|-----------|
| Núcleo matemático desde set/2025 | Tag v1.0.0, hash 0b3f4cb, DOI Zenodo |
| MCMC joint: Ωs0 < 0.00178 (95% UL) | emcee 32×1500, N/τ≈11; `rll_fase20_mcmc_bayes.json` |
| Bayes Factor: ln(B₁₀) = −6.190±0.691 | dynesty nlive=150; evidência muito forte para ΛCDM |
| F-COS-03 FAIL: z_t_BAO=0.30 ∉ [0.5,1.5] | `results/zt_scan/summary.json` |
| F-COS-04 FAIL: ln(B₁₀) < −5 | `rll_fase20_mcmc_bayes.json`; escala Jeffreys |
| `claim_allowed = false` — ΛCDM preferido | Todos os testes formais concluídos |

---

### Status do Modelo (atualizado)

**Status atual**: N4 (empiricamente testado com MCMC e nested sampling).

**Conclusão epistêmica**: `claim_allowed = false` confirmado — não por TOKEN_VAZIO, mas por resultado empírico. RLL não supera ΛCDM nos dados atuais. F-COS-03 e F-COS-04 são FAIL [E] — resultado honesto, registrado sem mascaramento.

**Caminho para claim_allowed = true** (se o modelo for revisado):
1. Substituir calibração E&H aditiva por CAMB/RECFAST em cada passo MCMC (elimina G4 estruturalmente)
2. Cadeia MCMC mais longa: N/τ > 50 (atual ≈ 11)
3. Justificar z_t, w_t, Ωs0 com derivação ou documentar como convenções livres
4. Novo cenário de parâmetros em que ln(B₁₀) > −5 (requer modificação do modelo)

*Adendo adicionado em 2026-07-16. Fases 1–22 concluídas. TOKEN_VAZIO estrutural = 0.*
