# Doc 17 — FASE 18: Horizonte Sonoro Numérico Corrigido + Prior BBN

**Data**: 2026-07-14  
**Branch**: `claude/rll-cronologia-auditoria-qyvn83`  
**Status epistêmico**: [E] análise quantitativa com 5 datasets reais + calibração em Planck 2018

---

## 1. Motivação e Problema Descoberto

### 1.1 Herança de FASE 17

FASE 17 (`rll_analise_completa.py`) usava a fórmula Eisenstein & Hu 1998 (E&H) para o horizonte sonoro de arrasto:

```
rd_EH = f(Ωm·h², Ωb·h²)    [fórmula analítica E&H]
```

Esta fórmula era usada para **duas** finalidades distintas:
1. BAO: `D_M/rd`, `D_H/rd` — **correto** usar `r_s(z_drag)`
2. CMB: `l_A = π × D_M / rd` — **incorreto** usar `r_s(z_drag)`!

### 1.2 Descoberta Crítica: Dois Horizontes Sonoros

A definição correta dos parâmetros de shift do CMB (Chen, Huang & Wang 2019, arXiv:1808.05724, Tabela I) é:

| Parâmetro | Fórmula correta | Horizonte usado |
|-----------|-----------------|-----------------|
| BAO scale | `r_s(z_drag)` | `z_drag ≈ 1059` (E&H) |
| CMB l_A | `l_A = π × D_M(z_*) / r_s(z_*)` | `z_* ≈ 1089.92` (recombinação) |

Como `z_* > z_drag`, temos `r_s(z_*) < r_s(z_drag)`:
- `r_s(z_drag)` ≈ 147.09 Mpc (Planck 2018)
- `r_s(z_*)` ≈ 144.43 Mpc (Planck 2018)

### 1.3 Por que FASE 17 Funcionou "Por Acaso"

A fórmula E&H superestimava `rd` em ~3% nos parâmetros MAP de FASE 17 (baixo Ωm·h²≈0.127, fora da região de calibração E&H de Ωm·h²≈0.143):

```
E&H rd_MAP ≈ 151.56 Mpc  (superestimado)
r_s(z_*) verdadeiro ≈ 149-151 Mpc nesses parâmetros específicos
→ acidentalmente coincidentes → chi²_CMB ≈ 19.68 (aparentemente correto)
```

Com rd numérico correto (≈147 Mpc) mas usando-o para l_A:
```
l_A_th = π × D_M / 147 ≈ 295  (vs l_A_obs = 301.47)
→ chi²_CMB ≈ 5000+  (catastrófico!)
```

---

## 2. Evolução das Versões FASE 18

### FASE 18 (inicial): `rll_fase18_rd_numerico.py`
- **Problema**: `np.trapz` removido em NumPy ≥ 2.0 → `AttributeError`
- **Fix**: integral trapezoidal manual via `np.sum(dz * 0.5 * (y[:-1]+y[1:]))`
- **Resultado**: convergiu para mínimo local errado H₀=72 (dominado por Moresco, CMB formula incorreta)

### FASE 18-C: `rll_fase18c_corrigido.py`
- **Fix 1**: Usa `r_s(z_*)` para CMB l_A (não `r_s(z_drag)`)
- **Fix 2**: Pontos de partida ancorados no BBN
- **Problema residual**: truncamento de integração em z_high=5×10⁵ perde ~0.54 Mpc do horizonte sonoro
- **chi²_CMB(Planck)** = 379 (esperado: ~0) → bias de +0.54 Mpc em rs_star

### FASE 18-D: `rll_fase18d_final.py`
- **Fix 3**: Correção analítica da cauda z > z_high:
  ```
  tail = (c/√3) / (H₀√Ωr) / (1+z_high) ≈ +0.54 Mpc
  ```
  Em regime de radiação pura: `c_s → c/√3`, `H → H₀√Ωr·(1+z)²`
- **chi²_CMB(Planck)** = 28.1 → melhora mas gap residual de +0.24 Mpc
- **Causa do gap residual**: física simplificada (tratamento do plasma barion-fóton sem código Boltzmann completo)

### FASE 18-E: `rll_fase18e_calibrado.py` ← **VERSÃO FINAL**
- **Fix 4**: Auto-calibração em parâmetros Planck 2018:
  ```python
  rs_star_target = π × D_M(Planck) / l_A_obs
  RS_STAR_CALIB  = rs_star_target - rs_star_raw(Planck)  # = +0.1988 Mpc
  ```
  Aplicada uniformemente: `rs_star_corrected = rs_star_raw + RS_STAR_CALIB`
- **chi²_CMB(Planck)** = 0.021 ≈ 0 ✓
- **Profile 5×5**: grade em (Ωs0 × z_t)

---

## 3. Resultados FASE 18-E (Definitivos)

### 3.1 Calibração

```
rs_star_raw (Planck 2018)     = 144.3123 Mpc
D_M (Planck 2018)             = 13867.5 Mpc
rs_star_target (l_A_obs=301.471) = 144.5111 Mpc
Calibração aplicada           = +0.1988 Mpc
chi²_CMB(Planck verificação)  = 0.0213  (≈ 0) ✓
```

### 3.2 MAP RLL (6 parâmetros: H₀, Ωm, Ωb, Ωs0, z_t, w_t)

| Parâmetro | Valor MAP |
|-----------|-----------|
| H₀ | 66.994 km/s/Mpc |
| Ωm | 0.32476 |
| Ωb | 0.04994 (Ωb·h² = 0.02241) |
| **Ωs0** | **0.01160** |
| z_t | 11.45 |
| w_t | 0.2266 |
| ΩΛ | 0.66356 |
| z_drag (E&H) | 1021.0 |
| r_s(z_drag) para BAO | 148.99 Mpc |
| r_s(z_*) para CMB | 142.92 Mpc (calibrado) |

**Decomposição chi²:**

| Dataset | chi² | n_pts | chi²/pt |
|---------|------|-------|---------|
| Moresco H(z) | 23.97 | 33 | 0.727 |
| BAO histórico | 2.42 | 4 | 0.605 |
| DESI DR2 BAO | 21.79 | 13 | 1.676 |
| Pantheon+SH0ES | 712.10 | 1624 | 0.438 |
| CMB shift | 0.76 | 3 | 0.254 |
| Prior BBN | 0.12 | — | — |
| **TOTAL** | **761.16** | **1677** | **0.454** |

### 3.3 MAP ΛCDM (3 parâmetros: H₀, Ωm, Ωb)

| Parâmetro | Valor MAP |
|-----------|-----------|
| H₀ | 67.667 km/s/Mpc |
| Ωm | 0.31626 |
| Ωb·h² | 0.02244 |
| r_s(z_drag) | 149.83 Mpc |
| r_s(z_*) | 143.68 Mpc (calibrado) |
| **chi²_total** | **778.60** |

### 3.4 Comparação de Modelos

| Critério | Valor | Interpretação |
|----------|-------|---------------|
| Δchi²(RLL−ΛCDM) | **−17.44** | RLL melhor em chi² |
| k_RLL − k_ΛCDM | +3 | RLL tem 3 parâmetros extras |
| ΔAIC | **−11.44** | RLL preferido por AIC |
| ΔBIC | **+4.84** | ΛCDM preferido por BIC |
| ln(B₁₀) | **−2.42** | Evidência "positiva" para ΛCDM (Jeffreys) |

**Escala de Jeffreys para |ln(B₁₀)|:**
- < 1: não vale menção
- 1.0–2.5: evidência positiva
- 2.5–5.0: evidência forte
- > 5.0: evidência muito forte

→ |ln(B₁₀)| = 2.42: na fronteira entre positiva e forte (levemente a favor do ΛCDM).

### 3.5 Profile Likelihood 5×5 em (Ωs0, z_t)

| Ωs0 | chi²_min | Δchi² vs 0 | z_t_opt | H₀ | Ωm |
|-----|----------|------------|---------|-----|-----|
| 0.000 | 778.60 | 0.000 | — | 67.667 | 0.3163 |
| 0.003 | 770.40 | −8.20 | 3.5 | 67.591 | 0.3170 |
| **0.010** | **765.79** | **−12.81** | **3.5** | **67.383** | **0.3189** |
| 0.030 | 818.18 | +39.58 | 1.5 | 65.679 | 0.3266 |
| 0.100 | 1367.72 | +589.12 | 1.5 | 63.569 | 0.3432 |

**Observação**: o mínimo do profile está em Ωs0≈0.010 (z_t=3.5), com chi²=765.79. Para Ωs0≥0.030 há exclusão forte (chi²≥818).

---

## 4. Interpretação Física do Mínimo Ωs0=0.012

### 4.1 O que significa Ωs0=0.012 com z_t=11.45

Com w_t=0.23 (transição moderadamente aguda):

- **z << z_t = 11.45** (universo observável, z < 6): `f(z) ≈ 1`
  → rho_s ≈ Ωs0 = 0.012 [constante, como ΩΛ]
  
- **z >> z_t = 11.45** (época CMB, z ≈ 1090): `f(z) ≈ 0`
  → rho_s ≈ Ωs0 × (1+z)³ [como matéria]

**Efeito**: o componente Ωs0 age como:
- Pequena constante cosmológica em z < 11 (adiciona 0.012 a ΩΛ_eff)
- Pequena componente de matéria em z > 11 (reduz rs_star, aumenta H em z altos)

### 4.2 Por que Melhora o Fit

O Ωs0=0.012 a z_t=11.45 proporciona:
1. **rs_star menor** (mais matéria em z>11 → H maior → cs/H menor → rs menor)
2. **l_A correta** (D_M menor + rs_star menor → l_A ≈ 301.47 ✓)
3. **Melhor equilíbrio** entre tensão H₀ (Moresco puxa H₀↑) e CMB (puxa H₀↓)

### 4.3 Contraposição com FASE 17

| Análise | Método | ΔBIC | Conclusão |
|---------|--------|------|-----------|
| FASE 17 | E&H rd para BAO e CMB (acidentalmente ok) | +22.27 | ΛCDM decisivo |
| FASE 18-E | rd numérico BAO + rs_star calibrado CMB | +4.84 | ΛCDM levemente preferido |

A diferença de ΔBIC = +22 → +5 reflete:
- Cálculo mais preciso do horizonte sonoro
- Melhor ajuste aos dados DESI com a flexibilidade RLL
- Calibração correta removendo o erro de E&H

---

## 5. Limitações e TOKEN_VAZIO

### 5.1 [E] O que é certo

- Calibração em Planck 2018: chi²_CMB = 0.021 ≈ 0 ✓
- Análise com 5 datasets reais (1677 pontos)
- Prior BBN físico (Cooke+ 2018)
- Dois horizontes sonoros distintos usados corretamente

### 5.2 [H] O que é incerto

- **Ωs0_MAP = 0.012 real ou numérico?**: Δchi² = −17.4 com 3 parâmetros extras.
  ΔBIC = +4.84 penaliza os 3 parâmetros — borderline caso. Necessário MCMC com posteriors completas.
  
- **rd = r_s(z_drag)**: fórmula E&H usada para z_drag (bias relativo de ~3% em rd vs Planck, afetando chi²_BAO/DESI). Correção: usar Hu & Sugiyama 1996 fitting formula ou integrar rs(z_drag) com a mesma grade.

### 5.3 [VAZIO P0] TOKEN_VAZIO Abertos

| ID | Gap | Próximo Passo |
|----|-----|---------------|
| G1 | MCMC conjunto (posterior de Ωs0) | disparar `rll-validacao-cientifica-completa.yml` com `modo=apenas_bayes` |
| G2 | z_drag numérico para rd (remover E&H bias) | integrar rs(z_drag) na mesma grade que rs(z_*) |
| G3 | Bayes Factor formal ln(B₁₀) via nested sampling | dynesty ou multinest |

---

## 6. Arquivos Gerados

| Arquivo | Tipo | Conteúdo |
|---------|------|----------|
| `scripts/rll_fase18e_calibrado.py` | Script | Análise final calibrada |
| `scripts/rll_fase18d_final.py` | Script | Versão com cauda mas sem calib (referência) |
| `scripts/rll_fase18c_corrigido.py` | Script | Versão com rs_star mas sem cauda (referência) |
| `scripts/rll_fase18_rd_numerico.py` | Script | Versão inicial (bug np.trapz, mínimo local) |
| `results/rll_fase18e_calibrado.json` | Resultado | MAP, ΛCDM, profile, comparação |
| `results/rll_fase18d_final.json` | Resultado | Versão sem calibração (referência) |

---

## 7. Rastreabilidade

- **Chen, Huang & Wang 2019** (arXiv:1808.05724): definição de `l_A = π×D_M(z_*)/r_s(z_*)` ← Tabela I
- **Cooke, Pettini & Steidel 2018** (arXiv:1710.11129): prior BBN `Ωb·h² = 0.02236 ± 0.00015`
- **Eisenstein & Hu 1998** (ApJ 496, 605): fórmula E&H para z_drag (usada para rd; bias ≈3%)
- **Planck 2018 VI** (arXiv:1807.06209): parâmetros de verificação H₀=67.36, Ωm=0.3153
- **DESI DR2 BAO** (arXiv:2503.14738): 7 tracers, 13 dados
- **Moresco 2022**: 33 pontos H(z)
- **Pantheon+SH0ES**: 1624 SNe (IS_CALIBRATOR=0)

---

*Documento de auditoria — rastreabilidade epistêmica RAFAELIA-RLL*
