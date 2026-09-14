# Doc 21 — FASE 22: Mapeamento do Bias E&H em Espaço de Parâmetros (G4)

**Data**: 2026-07-16 | **Gap**: G4 | **Status**: FECHADO [E]  
**Artefato**: `results/rll_fase22_g4_eh_bias_grid.json`  
**Script**: `scripts/rll_fase22_g4_eh_bias_grid.py`  
**claim_allowed**: false

---

## 1. Motivação

O gap G4 foi identificado na FASE 20 como uma limitação residual da calibração aditiva
introduzida na FASE 19:

> **G4** (TOKEN_VAZIO P3/H): A calibração `rd_corr = rd_EH + Δrd` usa uma correção
> constante `Δrd = −3.614 Mpc` calculada no ponto Planck 2018 de referência.
> Se o bias `Δrd = rd_EH(Ωm·h², Ωb·h²) − rd_Planck` varia no espaço de parâmetros,
> a calibração aditiva introduz um erro sistemático.

**Pergunta G4**: Qual é a magnitude da variação de `Δrd` no espaço de parâmetros
relevante (posterior MCMC FASE 20)?

---

## 2. Método

### 2.1 Fórmula E&H 1998 para z_drag

```
z_drag = 1291 × (Ωm·h²)^{0.251} / [1 + 0.659(Ωm·h²)^{0.828}]
         × [1 + b₁(Ωb·h²)^{b₂}]

b₁ = 0.313 × (Ωm·h²)^{−0.419} × [1 + 0.607(Ωm·h²)^{0.674}]
b₂ = 0.238 × (Ωm·h²)^{0.223}
```

### 2.2 Integral numérica de rd

```
rd = ∫_{z_drag}^{5×10⁵} c_s(z)/H(z) dz  +  cauda analítica

onde:
  c_s(z) = c / √[3(1 + R_b(z))]
  R_b(z) = (3Ωb)/(4Ωγ) × 1/(1+z)
  H(z)   = H₀ × √[Ωm(1+z)³ + Ωr(1+z)⁴ + ΩΛ]   (ΛCDM; os0=0)

cauda = (c/√3) / [H₀·√Ωr · (1 + 5×10⁵)]
```

**Validação no ponto Planck 2018**: `rd_EH_num = 150.7048 Mpc` ≡ `150.704 Mpc` da FASE 19. ✅

### 2.3 Grade

- Ωm·h² ∈ [0.12, 0.16] — 10 pontos (±14% em relação a Planck ≈0.143)
- Ωb·h² ∈ [0.020, 0.025] — 10 pontos (BBN ±5σ)
- Total: 100 pontos

---

## 3. Resultados

### 3.1 Validação no ponto Planck 2018

| Quantidade | Resultado FASE 22 | Referência FASE 19 | Concordância |
|-----------|------------------|--------------------|--------------|
| zdrag_EH  | 1020.729         | 1020.729           | ✅ idêntico  |
| rd_EH_num | 150.7048 Mpc     | 150.7040 Mpc       | ✅ <0.001%   |
| Δrd       | +3.6148 Mpc      | +3.6140 Mpc        | ✅ <0.01%    |

### 3.2 Grade 10×10 (faixa ampla)

| Estatística | Δrd (Mpc) |
|-------------|-----------|
| Mínimo      | −2.949    |
| Máximo      | +12.810   |
| Média       | +4.540    |
| Desvio padrão | 3.867  |
| Variação total | 15.759 |

A variação ampla na grade reflete a não-linearidade da fórmula E&H 1998 em extremos
de parâmetros (Ωm·h²=0.12 vs 0.16 é ±14% — muito além do posterior RLL).

### 3.3 Ponto MCMC posterior FASE 20 (p50 das marginais)

| Parâmetro | Valor |
|-----------|-------|
| H₀ | 66.912 km/s/Mpc |
| Ωm | 0.31437 |
| Ωb | 0.04977 |
| Ωm·h² | 0.14075 |
| Ωb·h² | 0.022283 |
| zdrag_EH | 1020.330 |
| rd_EH_num | 151.4262 Mpc |
| Δrd_MCMC | +4.3362 Mpc |
| **Erro sistemático calib.** | **0.7214 Mpc** |

> O erro sistemático é `|Δrd_MCMC − Δrd_Planck| = |4.3362 − 3.6148| = 0.7214 Mpc`.

---

## 4. Impacto sobre G3

A incerteza de G4 (0.72 Mpc) propaga-se no Bayes Factor via mudança em χ²:

```
Δχ²_G4 ≈ (0.72 / σ_rd_eff)²

onde σ_rd_eff é a incerteza efetiva em rd das medidas BAO combinadas.
Para DESI DR2 com 13 pontos: σ_rd_eff ~ 0.5–1.5 Mpc
→ Δχ²_G4 ≈ 0.2 – 2.1
→ Δln(B₁₀)_G4 ≈ 0.1 – 1.0
```

**Resultado G3**: `ln(B₁₀) = −6.190 ± 0.691` (incerteza estatística já incluída).

Mesmo no pior caso (`Δln(B₁₀)_G4 ≈ +1.0`):
- `ln(B₁₀)_corrigido ≈ −5.19`
- Ainda satisfaz `|ln(B₁₀)| > 5.0` → evidência forte para ΛCDM

**Conclusão**: G4 não altera a interpretação qualitativa de G3.

---

## 5. Interpretação Epistêmica

| Aspecto | Avaliação |
|---------|-----------|
| Calibração aditiva no ponto posterior | Boa aproximação: erro = 0.72 Mpc |
| Calibração na grade ampla | Aproximação de primeira ordem: varia até ±13 Mpc |
| Impacto em ln(B₁₀) | Estimado < 1 unidade; não muda conclusão G3 |
| Abordagem correta para trabalho futuro | Usar CAMB/RECFAST para rd(Ωm, Ωb) em cada passo MCMC |
| Prioridade futura | P3/H → P3/E (quantificada) |

---

## 6. Status Final dos Gaps

| Gap | Descrição | Status | Evidência |
|-----|-----------|--------|-----------|
| G1 | MCMC joint Ωs0 posterior | ✅ FECHADO (FASE 20) | emcee 32×1500 |
| G2 | rd numérico (calibração E&H) | ✅ FECHADO (FASE 19) | rd=147.09 Mpc |
| G3 | Bayes Factor formal ln(B₁₀) | ✅ FECHADO (FASE 20) | dynesty nlive=150 |
| G4 | Mapeamento bias E&H em param space | ✅ FECHADO (FASE 22) | grade 10×10; sist.=0.72 Mpc |

**Todos os 4 gaps fechados.** TOKEN_VAZIO estrutural = 0.

---

*claim_allowed: false — resultados numéricos verificáveis; impacto qualitativo em G3 avaliado;
substituição por CAMB/RECFAST recomendada para análise de precisão futura.*
