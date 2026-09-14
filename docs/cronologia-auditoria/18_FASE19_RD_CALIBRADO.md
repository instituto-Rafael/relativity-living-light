# Doc 18 — FASE 19: rd Calibrado — Fechamento do TOKEN_VAZIO G2

**Data**: 2026-07-14  
**Branch**: `claude/rll-cronologia-auditoria-qyvn83`  
**Status epistêmico**: [E] análise calibrada com dupla ancoragem em Planck 2018

---

## 1. Motivação e TOKEN_VAZIO G2

### 1.1 Gap Identificado em FASE 18

O doc 17 (FASE 18) identificou o TOKEN_VAZIO G2:

> "rd = r_s(z_drag): fórmula E&H usada para z_drag (bias relativo de ~3% em rd vs Planck, afetando chi²_BAO/DESI). Correção: usar Hu & Sugiyama 1996 fitting formula ou integrar rs(z_drag) com a mesma grade."

### 1.2 O Problema

A fórmula Eisenstein & Hu 1998 (Eq. 4) para z_drag subestima o valor real:

| Fonte | z_drag | rd [Mpc] |
|-------|--------|----------|
| E&H 1998 (parâmetros Planck) | ≈ 1021 | 150.70 (numérico bruto) |
| Planck 2018 VI (CAMB/RECFAST) | ≈ 1059 | 147.09 |
| **Diferença** | **−38** | **+3.61 Mpc** |

O E&H dá z_drag ≈ 38 unidades menor que o valor real. Isso alarga a janela de integração `∫_{z_drag}^{∞} c_s/H dz`, superestimando rd em ~3.61 Mpc.

---

## 2. Abordagem de Correção

### 2.1 Calibração Aditiva (análoga à rs_star em FASE 18-E)

Estratégia idêntica à calibração de rs_star:

```python
_RD_CALIB_MPC = 0.0   # preenchido em main()
# Em compute_sound_horizons():
return float(rd) + _RD_CALIB_MPC, float(rs_star) + _RS_STAR_CALIB_MPC
```

Calibração em `main()`:
```python
rd_numerical_planck, _ = compute_sound_horizons(*THETA_PLANCK)  # sem calibs
_RD_CALIB_MPC = RD_PLANCK2018 - rd_numerical_planck  # = 147.09 - 150.704 = -3.614 Mpc
```

### 2.2 Verificação

Com dupla calibração ativa em parâmetros Planck 2018:

```
rd  = r_s(z_drag) = 147.0900 Mpc  ✓  (alvo: 147.09 Mpc)
r_s(z_*) = 144.5111 Mpc           ✓  (herdado de FASE 18-E)
chi²_CMB(Planck) = 0.0213          ✓  (≈ 0)
```

---

## 3. Resultados FASE 19 — Descoberta Crítica

### 3.1 Calibrações Aplicadas

| Parâmetro | Valor bruto (Planck) | Alvo | Correção |
|-----------|---------------------|------|---------|
| rs_star | 144.3123 Mpc | 144.5111 Mpc | +0.1988 Mpc |
| **rd** | **150.7040 Mpc** | **147.09 Mpc** | **−3.6140 Mpc** |

### 3.2 MAP RLL (6 parâmetros)

| Parâmetro | FASE 18-E | FASE 19 |
|-----------|-----------|---------|
| H₀ | 66.994 km/s/Mpc | 66.997 km/s/Mpc |
| Ωm | 0.32476 | 0.31392 |
| Ωb·h² | 0.02241 | 0.02228 |
| **Ωs0** | **0.01160** | **0.00000** |
| z_t | 11.45 | — (Ωs0=0) |
| ΩΛ | 0.66356 | 0.68599 |
| rd | 148.99 Mpc | 148.18 Mpc |

### 3.3 Decomposição chi²

| Dataset | FASE 18-E | FASE 19 |
|---------|-----------|---------|
| Moresco H(z) | 23.97 / 33 | 23.31 / 33 |
| BAO histórico | 2.42 / 4 | 5.51 / 4 |
| DESI DR2 BAO | 21.79 / 13 | 28.48 / 13 |
| Pantheon+SH0ES | 712.10 / 1624 | 713.81 / 1624 |
| CMB shift | 0.76 / 3 | 1.12 / 3 |
| Prior BBN | 0.12 | 0.31 |
| **TOTAL** | **761.16** | **772.54** |

**Observação**: BAO e DESI pioraram porque rd menor (147→148 no MAP) piora o ajuste a observações que foram calibradas assumindo rd≈147 Mpc.

### 3.4 Comparação de Modelos

| Critério | FASE 18-E | FASE 19 | Variação |
|----------|-----------|---------|---------|
| Δχ²(RLL−ΛCDM) | −17.44 | **0.000** | RLL = ΛCDM ← colapso! |
| ΔAIC | −11.44 | **+6.00** | ΛCDM preferido |
| **ΔBIC** | **+4.84** | **+22.27** | ΛCDM fortemente preferido |
| ln(B₁₀) | −2.42 | **−11.14** | Evidência muito forte para ΛCDM |

### 3.5 Profile Likelihood 5×5 em (Ωs0, z_t)

| Ωs0 | chi²_min | Δchi² vs 0 | z_t_opt | H₀ | Ωm |
|-----|----------|------------|---------|-----|-----|
| **0.000** | **772.543** | **0.000** | — | **66.997** | **0.3139** |
| 0.003 | 775.495 | +2.952 | 2.5 | 66.950 | 0.3133 |
| 0.010 | 789.025 | +16.483 | 2.5 | 66.843 | 0.3119 |
| 0.030 | 877.595 | +105.052 | 1.5 | 66.560 | 0.3080 |
| 0.100 | 1626.776 | +854.234 | 1.5 | 61.498 | 0.3244 |

**Profile mínimo em Ωs0 = 0** (ΛCDM puro). Exclusão monotônica para Ωs0 > 0.

---

## 4. Interpretação Epistêmica — A Descoberta Central

### 4.1 O Sinal Ωs0=0.012 em FASE 18-E Era Artefato do Viés E&H

| Análise | rd para BAO | Ωs0 MAP | ΔBIC | Conclusão |
|---------|-------------|---------|------|-----------|
| FASE 17 | E&H ≈ 151.56 Mpc (acidentalmente ok) | 0.04 (instável) | +22 | ΛCDM decisivo |
| FASE 18-E | Numérico ~148.99 Mpc (E&H bias ativo) | **0.0116** | +4.84 | ΛCDM borderline |
| **FASE 19** | **Calibrado = 147.09 Mpc (Planck 2018)** | **0.0000** | **+22.27** | **ΛCDM decisivo** |

**Mecanismo do artefato**:

Em FASE 18-E, `rd_bruto ≈ 150.70 Mpc` (E&H) vs `rd_verdadeiro = 147.09 Mpc`. O excesso de +3.61 Mpc em rd fazia com que BAO/DESI observassem ângulos ligeiramente diferentes dos preditos pelo ΛCDM. O otimizador compensava adicionando componente Ωs0 com z_t alto, que:
1. Aumenta H(z) em z > z_t → diminui rs_star → diminui l_A → mantém CMB ok
2. Altera a geometria de modo a reajustar as razões DM/rd e DH/rd aos dados BAO/DESI

Com rd corretamente calibrado, esse "ajuste" não é mais necessário: Ωs0=0 já satisfaz todos os datasets.

### 4.2 Convergência das Três Análises para ΔBIC ≈ +22

| | Fase 17 | Fase 18-E | Fase 19 |
|---|---------|-----------|---------|
| Erro | rd E&H para BAO e l_A | rd correto para BAO, mas E&H bias não removido | rd calibrado ao Planck 2018 |
| ΔBIC | +22.27 (acidental) | +4.84 (artefato) | +22.27 (correto) |

**Conclusão física**: O ΔBIC ≈ +22 que apareceu em FASE 17 era fisicamente correto, mas pela razão errada (cancelamento acidental). FASE 18-E criou um artefato ao corrigir a fórmula CMB sem corrigir rd. FASE 19 restaura ΔBIC ≈ +22, agora pela razão certa.

### 4.3 Escala de Jeffreys

```
|ln(B₁₀)| = 11.14
  > 5.0 → evidência muito forte para ΛCDM (Jeffreys 1961)
```

### 4.4 O que NÃO é certo (limitações)

1. **Calibração aditiva de rd**: O offset de −3.614 Mpc foi calculado em parâmetros Planck. Para outros valores de Ωm·h², o bias E&H pode ser diferente. Uma correção mais rigorosa requereria um mapeamento do bias em função de (Ωm·h², Ωb·h²).

2. **rd no MAP ≠ 147.09 Mpc**: No MAP de FASE 19, rd = 148.18 Mpc (não 147.09), porque os parâmetros MAP diferem ligeiramente dos Planck. O offset de −3.614 Mpc foi calibrado nos parâmetros Planck, não nos MAP.

3. **z_drag ainda via E&H**: A fórmula E&H ainda é usada para a integração numérica (ponto de início da grade). A calibração aditiva de rd corrige o resultado final, mas não o ponto de integração.

---

## 5. TOKEN_VAZIO Restantes

| ID | Gap | Status após FASE 19 |
|----|-----|---------------------|
| G1 | MCMC joint (posterior de Ωs0) | VAZIO — disparar `rll-validacao-cientifica-completa.yml` |
| **G2** | **rd numérico para z_drag** | **✅ FECHADO** — calibração −3.614 Mpc aplicada |
| G3 | Bayes Factor formal ln(B₁₀) via nested sampling | VAZIO — dynesty/multinest |
| G4 (novo) | Mapeamento do bias E&H em (Ωm·h², Ωb·h²) | [H] avaliar se offset é constante em param space |

---

## 6. Arquivos Gerados

| Arquivo | Tipo | Conteúdo |
|---------|------|----------|
| `scripts/rll_fase19_rd_calibrado.py` | Script | Análise com dupla calibração Planck 2018 |
| `results/rll_fase19_rd_calibrado.json` | Resultado | MAP, ΛCDM, profile, dupla calibração |

---

## 7. Rastreabilidade

- **Planck 2018 VI** (arXiv:1807.06209), Tabela 2: `r_drag = 147.09 ± 0.26 Mpc`, `z_drag ≈ 1059`
- **Eisenstein & Hu 1998** (ApJ 496, 605): fórmula z_drag usada como ponto de integração (bias −38 vs Planck)
- **Chen, Huang & Wang 2019** (arXiv:1808.05724): `l_A = π × D_M(z_*) / r_s(z_*)`
- **Cooke, Pettini & Steidel 2018** (arXiv:1710.11129): prior BBN `Ωb·h² = 0.02236 ± 0.00015`
- **DESI DR2 BAO** (arXiv:2503.14738): 7 tracers, 13 dados
- **Moresco 2022**: 33 pontos H(z)
- **Pantheon+SH0ES**: 1624 SNe

---

## 8. Evolução FASE 17 → 19 (síntese)

```
FASE 17:  rd E&H para BAO e l_A → ΔBIC=+22 por acidente (E&H compensava erro CMB)
            ↓ descoberta: l_A usa r_s(z_*), não r_s(z_drag)
FASE 18-C: r_s(z_*) para l_A (correto) + rd numérico E&H para BAO → chi²_CMB ok
            ↓ mas: E&H bias em rd ainda ativo → Ωs0=0.012 aparece como artefato
FASE 18-E: auto-calibração de rs_star (+0.1988 Mpc) → Δchi²=-17, ΔBIC=+4.84
            ↓ G2 identificado: bias E&H em rd = +3.61 Mpc
FASE 19:  dupla calibração (rs_star + rd) → Ωs0=0, ΔBIC=+22.27 ← CONCLUSÃO FÍSICA
```

---

*Documento de auditoria — rastreabilidade epistêmica RAFAELIA-RLL*
