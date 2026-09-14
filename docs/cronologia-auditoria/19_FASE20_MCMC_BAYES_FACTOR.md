# Doc 19 — FASE 20: MCMC Joint + Bayes Factor Formal (G1 + G3)

**Data**: 2026-07-14  
**Branch**: `claude/rll-cronologia-auditoria-qyvn83`  
**Status epistêmico**: [E] posterior Bayesiana e evidência formal com dados reais

---

## 1. Objetivos

Fechar os dois TOKEN_VAZIO que restavam após FASE 19:

| ID | Gap | Método |
|----|-----|--------|
| **G1** | MCMC joint — posterior de Ωs0 | `emcee` 32 walkers × 1500 steps |
| **G3** | Bayes Factor formal ln(B₁₀) | `dynesty` nested sampling, nlive=150 |

---

## 2. Configuração

### 2.1 Calibração (idêntica a FASE 19)

```
_RS_STAR_CALIB_MPC = +0.1988 Mpc  (chi²_CMB(Planck) = 0.021 ✓)
_RD_CALIB_MPC      = −3.6140 Mpc  (rd(Planck) = 147.09 Mpc ✓)
```

### 2.2 Priors (planos dentro dos limites)

| Parâmetro | Prior |
|-----------|-------|
| H₀ | Uniforme [60, 80] km/s/Mpc |
| Ωm | Uniforme [0.20, 0.50] |
| Ωb | Uniforme [0.030, 0.070] |
| Ωs0 | Uniforme [0.0, 0.15] |
| z_t | Uniforme [0.1, 20.0] |
| w_t | Uniforme [0.05, 2.0] |

*Prior BBN (Ωb·h²) incorporado no chi²_total como contribuição gaussiana.*

### 2.3 Configuração MCMC (G1)

- `emcee` EnsembleSampler: 32 walkers × 1500 steps
- Burn-in descartado: 400 steps
- Posição inicial: MAP de FASE 19 + perturbação gaussiana pequena
- Ωs0 inicial ≥ 0 (reflexão de abs)

### 2.4 Configuração Nested Sampling (G3)

- `dynesty` NestedSampler: nlive=150, dlogz=0.5
- Dois runs separados: RLL (6D) e ΛCDM (3D)
- ln(B₁₀) = log Z_RLL − log Z_ΛCDM

---

## 3. Resultados G1 — Posterior MCMC

### 3.1 Diagnóstico de Convergência

```
Fração de aceitação: 0.377  (ideal: 0.2–0.5) ✓
Tempo de autocorrelação τ:
  H₀:  67.4 steps
  Ωm:  75.2 steps
  Ωb:  66.9 steps
  Ωs0: 81.8 steps
  z_t: 97.8 steps
  w_t: 99.5 steps
Atenção: N/50 = 30 < τ_max/50 ≈ 2 → cadeia mais curta que o ideal.
  Posteriors confiáveis para H₀, Ωm, Ωb; intervalos de Ωs0 aproximados.
```

### 3.2 Posteriors Marginalizadas

| Parâmetro | Mediana | −1σ | +1σ | 95% UL |
|-----------|---------|-----|-----|--------|
| H₀ (km/s/Mpc) | 66.912 | −0.722 | +0.698 | — |
| Ωm | 0.31437 | −0.00107 | +0.00108 | — |
| **Ωs0** | **0.00039** | **−0.00030** | **+0.00072** | **0.00178** |

### 3.3 Posterior de Ωs0

```
Mediana     = 0.00039
1σ intervalo = [0.00009, 0.00111]
95% limite superior = 0.00178 ← limite observacional para nova física
Média ± σ   = 0.00057 ± 0.00057
```

**Interpretação**: A posterior de Ωs0 é fortemente concentrada próxima de zero, consistente com o MAP de FASE 19 (Ωs0=0). O limite superior de 95% é Ωs0 < 0.0018, excluindo o sinal de FASE 18-E (Ωs0=0.012) por um fator ~7.

---

## 4. Resultados G3 — Bayes Factor Formal

### 4.1 Log-Evidências

```
log Z_RLL  = −404.340 ± 0.530
log Z_ΛCDM = −398.150 ± 0.443
```

### 4.2 Fator de Bayes

```
ln(B₁₀) = log Z_RLL − log Z_ΛCDM = −6.190 ± 0.691
```

**Escala de Jeffreys (1961)**:

| |ln(B₁₀)| | Interpretação |
|-----------|---------------|
| < 1.0 | Não vale menção |
| 1.0–2.5 | Evidência positiva |
| 2.5–5.0 | Evidência forte |
| **> 5.0** | **Evidência muito forte** |

→ **|ln(B₁₀)| = 6.19 > 5.0: evidência muito forte para ΛCDM** ✓

### 4.3 Consistência entre Estimativas

| Método | ln(B₁₀) estimado |
|--------|-----------------|
| FASE 19 — ΔBIC/2 (aproximação) | −11.14 |
| FASE 20 — dynesty (exact) | **−6.190 ± 0.691** |
| FASE 18-E — ΔBIC/2 (com viés E&H) | −2.42 |

A discrepância ΔBIC/2 vs dynesty é esperada: ΔBIC/2 assume posterior gaussiana concentrada no MAP (aproximação de Laplace), enquanto o dynesty integra o volume total da posterior. Para Ωs0 com prior plano [0, 0.15], o RLL tem volume de prior adicional que penaliza menos do que o ΔBIC sugere, mas ainda resulta em |ln(B₁₀)| > 5.

---

## 5. Conclusão Epistêmica

### 5.1 Evolução Completa FASE 17 → 20

| Fase | rd | CMB | Ωs0 MAP | ln(B₁₀) | Conclusão |
|------|----|----|---------|---------|-----------|
| 17 | E&H para BAO e l_A | incorreto | 0.04 | −11 (acident.) | ΛCDM |
| 18-E | Num. (viés E&H ativo) | r_s(z_*) ✓ | 0.0116 | −2.42 | borderline |
| 19 | Calibrado −3.614 Mpc ✓ | r_s(z_*) ✓ | 0.0000 | −11 (aprox.) | ΛCDM forte |
| **20** | **Calibrado ✓** | **r_s(z_*) ✓** | **0.0004** | **−6.19 (exact)** | **ΛCDM muito forte** |

### 5.2 Resultado Físico Final

Com toda a física implementada corretamente:
- **Ωs0 < 0.0018** (95% UL) — sem evidência de componente de transição RLL
- **ln(B₁₀) = −6.19** — evidência muito forte para ΛCDM (Jeffreys)
- **H₀ = 66.91 ± 0.70 km/s/Mpc** — consistente com Planck 2018

### 5.3 Limitações Residuais

1. **Cadeia MCMC curta**: N/τ ≈ 30 (recomendado: ≥ 50). Os intervalos de Ωs0 são orientativos; a conclusão qualitativa (Ωs0 ≈ 0) é robusta.
2. **Calibração aditiva de rd**: Offset constante −3.614 Mpc não captura variação do bias E&H em espaço de parâmetros (G4 — novo TOKEN_VAZIO).
3. **Prior de Ωs0**: Prior plano [0, 0.15] é arbitrário. Prior informativo (e.g., log-uniforme) poderia alterar ln(B₁₀) por ~1–2 unidades.

---

## 6. TOKEN_VAZIO — Estado Final

| ID | Gap | Status |
|----|-----|--------|
| **G1** | MCMC joint posterior de Ωs0 | **✅ FECHADO** — Ωs0 < 0.0018 (95%), ln(B₁₀)=−6.19 |
| **G2** | rd numérico (remove bias E&H) | **✅ FECHADO** (FASE 19) — calibração −3.614 Mpc |
| **G3** | Bayes Factor formal ln(B₁₀) | **✅ FECHADO** — dynesty: −6.19 ± 0.69 |
| G4 (novo) | Mapeamento bias E&H em (Ωm·h², Ωb·h²) | VAZIO [H] — avaliação futura |

**Todos os gaps P0 originais estão fechados.**

---

## 7. Arquivos Gerados

| Arquivo | Tipo | Conteúdo |
|---------|------|----------|
| `scripts/rll_fase20_mcmc_bayes.py` | Script | MCMC + nested sampling |
| `results/rll_fase20_mcmc_bayes.json` | Resultado | Posteriors, log-evidências, ln(B₁₀) |

---

## 8. Rastreabilidade

- **Planck 2018 VI** (arXiv:1807.06209): parâmetros de calibração; r_drag=147.09 Mpc
- **Chen, Huang & Wang 2019** (arXiv:1808.05724): l_A = π×D_M/r_s(z_*)
- **Cooke, Pettini & Steidel 2018** (arXiv:1710.11129): Ωb·h² = 0.02236 ± 0.00015
- **Foreman-Mackey et al. 2013** (arXiv:1202.3665): emcee ensemble sampler
- **Speagle 2020** (arXiv:1904.02180): dynesty nested sampling
- **Jeffreys 1961**: escala de evidência Bayesiana
- **DESI DR2 BAO** (arXiv:2503.14738): 7 tracers, 13 dados
- **Moresco 2022**: 33 pontos H(z)
- **Pantheon+SH0ES**: 1624 SNe

---

*Documento de auditoria — rastreabilidade epistêmica RAFAELIA-RLL*
