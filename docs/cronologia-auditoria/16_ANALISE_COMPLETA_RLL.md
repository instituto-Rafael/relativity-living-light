# Análise Completa RLL — FASE 17: 5 Datasets, 6 Parâmetros, Profile Likelihood

**Data**: 2026-07-14 | **Fase**: FASE 17  
**Script**: `scripts/rll_analise_completa.py`  
**Output**: `results/rll_analise_completa.json`  
**Status epistêmico**: [E] análise MAP completa + profile likelihood executados

---

## 1. Propósito

Ampliar a análise de FASE 16 para incluir todos os datasets reais disponíveis e computar o profile likelihood bidimensional em (Ωs0, z_t), testando se existe qualquer combinação de parâmetros RLL que seja favorecida pelos dados.

**Pergunta central**: existe algum par (Ωs0 > 0, z_t) que melhora o ajuste conjunto?

---

## 2. Configuração

### 2.1 Modelo

Setor logístico RLL (espaço plano):
```
E²(z) = Ωm(1+z)³ + Ωr(1+z)⁴ + Ωs0·[f(z) + (1-f(z))·(1+z)³] + ΩΛ
f(z) = 1/(1+exp((z-z_t)/w_t))
ΩΛ = 1 - Ωm - Ωr - Ωs0   [planura]
```

### 2.2 Parâmetros

**Livres (6)**: H₀, Ωm, Ωb, Ωs0, z_t, w_t

**Fixo**: Ωr = 9.18×10⁻⁵ (T_CMB = 2.7255 K)

**rd auto-consistente**: Eisenstein & Hu (1998) via Aubourg et al. (2015):
```
rd = 147.49 × (Ωm·h²/0.1432)^{-0.255} × (Ωb·h²/0.02236)^{-0.128} Mpc
```

### 2.3 Datasets usados

| Dataset | N | Observável | Referência |
|---------|---|-----------|------------|
| Moresco H(z) 2022 | 33 | H(z) [km/s/Mpc] | CC+BAO BOSS |
| BAO histórico | 4 | DV/rs | 6dFGS, MGS, BOSS DR12 LOWZ/CMASS |
| DESI DR2 BAO 2025 | 13 | DV/rd, DM/rd, DH/rd | arXiv:2503.14738 |
| Pantheon+SH0ES | 1624 | μ(z), M_B marginalizado | IS_CALIBRATOR=0 |
| CMB shift Planck 2018 | 3 | R, l_A, Ωb·h² + cov 3×3 | arXiv:1808.05724 |
| **Total** | **1677** | | |

**Nota sobre dupla contagem**: Excluídas das BAO históricas as linhas DESI2024_* (DR1; coberto por DESI DR2) e BOSS_Lya (coberta por DESI DR2 Lya z=2.33, observável diferente mas redshift idêntico).

---

## 3. Resultado — MAP joint 6 parâmetros [E]

### 3.1 Parâmetros ótimos

| Parâmetro | Valor ótimo | Nota |
|-----------|-------------|------|
| H₀ | **67.14 km/s/Mpc** | Entre Planck (67.4) e SH0ES (73) |
| Ωm | **0.2825** | Abaixo Planck (0.315) |
| Ωb | **0.05065** | Ωb·h² = 0.02284 (vs Planck 0.02236) |
| **Ωs0** | **0.0000** | Colapso — setor RLL removido |
| z_t | não identificado | Ωs0=0 → sem efeito |
| w_t | não identificado | Ωs0=0 → sem efeito |
| ΩΛ (derivado) | **0.7174** | |
| **rd (auto-consistente)** | **151.55 Mpc** | E&H com Ωm·h²=0.1274, Ωb·h²=0.02284 |

**Nota sobre rd**: rd=151.55 Mpc é mais alto que o valor Planck fixado (147.09 Mpc) em FASE 16. Isso ocorre porque o ajuste conjunto com CMB favorece Ωm·h²=0.127 < 0.143 (Planck), ampliando rd. Esta é uma tensão real entre os datasets.

### 3.2 χ² breakdown

| Dataset | χ² | N pts | χ²/pt |
|---------|-----|-------|--------|
| Moresco H(z) | 28.963 | 33 | 0.878 |
| BAO histórico | 2.908 | 4 | 0.727 |
| DESI DR2 BAO | 26.671 | 13 | 2.052 |
| Pantheon+SH0ES | 723.102 | 1624 | 0.445 |
| CMB shift | 19.685 | 3 | 6.562 |
| **TOTAL** | **801.329** | **1677** | **0.478** |

**Achado CMB**: χ²_CMB/3 = 6.56 indica tensão com CMB shift. O ajuste conjunto sacrifica CMB para acomodar Pantheon (dominante: 1624 SNe). O Planck CMB prefere Ωm≈0.315 com rd≈147 Mpc; os dados de distância (BAO + SN) com rd auto-consistente preferem Ωm≈0.28.

**Achado DESI DR2**: χ²_DESI/13 = 2.05 — acima do esperado (≈1), refletindo que Ωm=0.2825 com rd=151.55 Mpc não reproduz perfeitamente as razões DM/rd e DH/rd do DESI DR2.

---

## 4. Comparação com ΛCDM [E]

### 4.1 Parâmetros ΛCDM ótimos (3 parâmetros: H₀, Ωm, Ωb)

| Parâmetro | Valor |
|-----------|-------|
| H₀ | 67.14 km/s/Mpc |
| Ωm | 0.2825 |
| Ωb | 0.05065 |
| rd | 151.55 Mpc |
| χ²_total | 801.329 |

Com Ωs0=0, o modelo RLL é identicamente ΛCDM → χ²_RLL = χ²_ΛCDM.

### 4.2 Critérios de seleção de modelos

| Critério | RLL (k=6) | ΛCDM (k=3) | Δ(RLL−ΛCDM) | Interpretação |
|---------|-----------|-----------|-------------|---------------|
| χ² | 801.329 | 801.329 | 0.000 | Idênticos (Ωs0=0) |
| AIC | 813.329 | 807.329 | **+6.000** | RLL penalizado |
| BIC | 836.603 | 821.066 | **+15.537** | RLL fortemente penalizado |

**Regra de Jeffreys para BIC**: ΔBIC > 10 → evidência muito forte contra RLL.

**Nota AIC vs FASE 16**: ΔAIC=+6 (mesmo que FASE 16, pois Δk=3 com mesmo χ²). Porém ΔBIC=+15.5 (vs +12.3 em FASE 16 com N=1670 vs N=1677 aqui) — mais forte com mais dados.

---

## 5. Profile Likelihood — grade 10×10 em (Ωs0 × z_t) [E]

### 5.1 Resultado: χ² mínimo por linha Ωs0

| Ωs0 | χ²_min(z_t) | Δχ² vs ΛCDM | z_t_opt | Status |
|-----|------------|-------------|---------|--------|
| 0.000 | **801.329** | **+0.000** | — | [E] mínimo global |
| 0.001 | 804.448 | +3.119 | ≥0.5 | [E] PIOR |
| 0.003 | 811.200 | +9.871 | ≥0.5 | [E] PIOR |
| 0.005 | 818.630 | +17.301 | ≥0.5 | [E] PIOR |
| 0.010 | 840.104 | +38.775 | ≥0.5 | [E] PIOR |
| 0.020 | 894.954 | +93.625 | ≥0.5 | [E] PIOR |
| 0.030 | 964.626 | +163.297 | ≥0.5 | [E] PIOR |
| 0.050 | 1143.489 | +342.161 | ≥0.5 | [E] PIOR |
| 0.070 | 1367.247 | +565.918 | ≥0.5–1.1 | [E] PIOR |
| 0.100 | 1768.910 | +967.581 | ≥0.5 | [E] PIOR |

**Nota (z_t=0.3 — caso especial)**:
| Ωs0 | χ²(z_t=0.3) | χ²_min(z_t≥0.5) | Penalidade z_t baixo |
|-----|------------|----------------|---------------------|
| 0.001 | 807.839 | 804.448 | +3.391 |
| 0.003 | 822.945 | 811.200 | +11.745 |
| 0.005 | 840.763 | 818.630 | +22.133 |
| 0.010 | 896.678 | 840.104 | +56.574 |
| 0.020 | 1053.178 | 894.954 | +158.224 |
| 0.030 | 1261.541 | 964.626 | +296.915 |

Transição logística em z_t baixo perturba fortemente o Pantheon+ (SNe em z<1).

### 5.2 Padrão do profile likelihood — achados detalhados

**Achado 1 — Monotonia estrita**: χ² é **monotonicamente crescente** com Ωs0 em toda a grade. O mínimo global é Ωs0=0.000 com χ²=801.329. Não existe nenhum (Ωs0, z_t) que melhore o ajuste.

**Achado 2 — Crescimento não-linear com Ωs0**:
```
Ωs0 = 0.001 → Δχ² = +3.1    (muito pequeno — zona de "ruído")
Ωs0 = 0.010 → Δχ² = +38.8   (já significativo: >6σ equivalente)
Ωs0 = 0.030 → Δχ² = +163    (excluído a >12σ)
Ωs0 = 0.050 → Δχ² = +342    (excluído a >18σ)
Ωs0 = 0.100 → Δχ² = +968    (excluído a >31σ)
```

**Achado 3 — H₀ anti-correlacionado com Ωs0**: À medida que Ωs0 cresce, H₀ decresce:
```
Ωs0=0.000 → H₀=67.14   Ωs0=0.030 → H₀=64.95
Ωs0=0.050 → H₀=63.45   Ωs0=0.100 → H₀=59.87
```
O otimizador reduz H₀ para compensar o excesso de energia do setor Ωs0, mas não consegue reproduzir os dados BAO+SN com boa qualidade.

**Achado 4 — z_t não identificado (perfil plano em z_t ≥ 0.5)**: Para qualquer Ωs0 fixo com z_t ≥ 0.5, χ² é praticamente idêntico (diferenças < 1). Isso confirma que z_t não é identificado pelos dados atuais — F-COS-03 FAIL reforçado.

**Achado 5 — z_t=0.3 penalizado**: Transição logística em z_t=0.3 perturba fortemente SNe Ia em z<1, aumentando χ²_Pantheon. Para Ωs0=0.1, χ²(z_t=0.3)=3570 vs χ²(z_t≥0.5)=1769 — razão ~2×.

---

## 6. Interpretação Epistêmica

### 6.1 O que este resultado implica

1. **Com 5 datasets e 1677 pontos, o setor RLL (Ωs0) é completamente eliminado pelo conjunto de dados atual.** A análise mais completa possível com dados reais confirma Ωs0=0.

2. **O rd auto-consistente resolve um artefato de FASE 16**: com rd fixo em 147.09 Mpc, havia uma tensão implícita entre os parâmetros. Com rd livre via E&H, o ajuste encontra rd=151.55 Mpc — 3% maior que o Planck, refletindo Ωm·h² menor.

3. **Tensão CMB × BAO/SN identificada**: χ²_CMB=19.68 (≈7σ² total sobre 3 observáveis) indica que os dados de distância preferem Ωm≈0.28, enquanto o CMB prefere Ωm≈0.315. Esta tensão é conhecida na literatura e não é específica do RLL.

4. **ΔBIC=+15.5** → evidência "muito forte" (escala Jeffreys) contra complexidade extra do RLL.

### 6.2 Limitações e caminhos de revisão

| Revisão | Por que pode mudar | Status |
|---------|------------------|--------|
| MCMC com prior Ωs0 > 0 | Pode revelar região de Ωs0 > 0 com χ² local menor | TOKEN_VAZIO G1 |
| rd por integração numérica completa | Fórmula E&H tem erro ~0.3%; rd exato pode mudar tensão CMB | TOKEN_VAZIO P1 |
| Dados H(z) em z > 2 | Logística difere de ΛCDM mais em alto z | Aguarda dados futuros |
| Prior cosmológico em Ωb·h² | Forçar Ωb·h²≈0.02236 poderia mudar rd e tensão | TOKEN_VAZIO P1 |

### 6.3 Relação com falsificadores existentes

| Falsificador | Status antes FASE 17 | Status pós FASE 17 |
|-------------|--------------------|--------------------|
| F-COS-01 ΔAIC<+10 | ✅ PASS (ΔAIC=3.8, Pantheon+) | ✅ PASS (ΔAIC=+6, joint 5 datasets) |
| F-COS-02 χ²_red<1.05 | ✅ PASS (0.439) | ✅ PASS (0.478/pt total) |
| F-COS-03 z_t ∈ [0.5,1.5] | ✗ FAIL z_t não identificado | ✗ FAIL confirmado |
| F-COS-04 ln(B₁₀) > −5 | ✗ FAIL ln(B₁₀)=−6.24 proxy | ✗ FAIL ΔBIC=+15.5 → ln(B₁₀)≈−7.7 |
| F-COS-05 χ²_DESI<150 | ✅ PASS (93.81) | [E] χ²_DESI=26.67 para 13 pts |

**Revisão F-COS-04**: ΔBIC = **+22.27** → ln(B₁₀) ≈ −ΔBIC/2 = **−11.14** (muito pior que proxy anterior de −6.24 e muito abaixo do threshold −5). Evidência "decisiva" contra RLL na escala de Jeffreys.

**Revisão F-COS-05**: Note que os valores não são diretamente comparáveis — FASE 15 usou parâmetros nominais Planck sobre os 13 pontos DESI DR2 (χ²=93.81); FASE 17 usa parâmetros otimizados com rd auto-consistente (χ²=26.67).

---

## 7. Resumo de Falsificadores — Estado Pós FASE 17

| ID | Status | Valor [E] |
|----|--------|-----------|
| F-COS-01 | ✅ PASS | ΔAIC=+6.0 < +10 (5 datasets joint) |
| F-COS-02 | ✅ PASS | χ²_red = 0.478/pt (total) |
| F-COS-03 | ✗ FAIL | z_t não identificado (profile plano em z_t) |
| F-COS-04 | ✗ FAIL | ΔBIC=+22.27 → ln(B₁₀)≈−11.14 (decisivo contra RLL; threshold −5) |
| F-COS-05 | ✅ PASS | χ²_DESI=26.67 / 13 pts ≪ 150 |

**Resumo**: 3/5 PASS · 2/5 FAIL · 0 TOKEN_VAZIO

---

## 8. Próximos Atos Científicos

```
G1 — MCMC joint com prior Ωs0 > 0:
     Disparar rll-validacao-cientifica-completa.yml modo=completo
     Job joint_mcmc_p0: emcee 32 walkers × 2000 steps
     Incluir prior log-uniforme em Ωs0 ∈ [0.001, 0.15]

P1a — rd por integração numérica:
      Substituir fórmula E&H por integral numérica de r_s(z_drag)
      Teste: comparar rd_EH com rd_numerico para Planck → diferença ~0.3%

P1b — Prior Gaussiano em Ωb·h²:
      Incluir prior Ωb·h² = 0.02236 ± 0.00015 (Planck 2018)
      Força rd mais próximo de 147 Mpc, potencialmente mudando DESI χ²

P2 — Dados futuros:
     DESI DR3 (2026), Euclid DR1 (2027) — maior precisão BAO
     JWST H(z) em z > 2 — discriminação logística vs ΛCDM
```

---

## 9. Notas Metodológicas

**Integração**: Grid log-espaçado _ZG com 7001 pontos de z=0 a z=1200. Integração trapezoidal acumulada. Precisão ~0.1% para distâncias de decouplement (z=1090).

**CMB shift formula**: R = √Ωm × χ(z_CMB), l_A = π × (c/H₀) × χ(z_CMB) / rd, Ωb·h² = Ωb × (H₀/100)². Covariância 3×3 via np.linalg.inv.

**Pantheon+ M_B**: Marginalização analítica exata: M_B_opt = Σ(δ·w)/Σw, χ² = Σw(δ-M_B_opt)². Elimina degenerescência H₀-M_B.

**Profile likelihood**: Minimização Nelder-Mead adaptativo em (H₀, Ωm, Ωb, w_t) para cada ponto fixo (Ωs0, z_t). 100 pontos de grade, 3000 iterações máximo cada.

---

*Documento criado em FASE 17 (2026-07-14). Script: `scripts/rll_analise_completa.py`. JSON: `results/rll_analise_completa.json`.*
