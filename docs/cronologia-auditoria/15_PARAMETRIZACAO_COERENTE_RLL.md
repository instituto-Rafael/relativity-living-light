# Parametrização Coerente RLL — Otimização Joint

**Data**: 2026-07-13 | **Fase**: FASE 16  
**Script**: `scripts/optimize_rll_joint_parametrizacao.py`  
**Output**: `results/rll_joint_parametrizacao.json`  
**Status epistêmico**: [E] otimização MAP conjunta executada

---

## 1. Propósito

Responder à pergunta: *quais parâmetros RLL descrevem simultaneamente os três datasets disponíveis?*

Modelo canônico (setor logístico):
```
E²(z) = Ωm(1+z)³ + Ωr(1+z)⁴ + Ωs0·[f(z) + (1-f(z))·(1+z)³] + ΩΛ
f(z) = 1/(1+exp((z-z_t)/w_t))
ΩΛ = 1 - Ωm - Ωr - Ωs0   [espaço plano]
```

5 parâmetros livres: H₀, Ωm, Ωs0, z_t, w_t  
Fixados: Ωr = 9.18×10⁻⁵ (T_CMB = 2.7255 K), rd = 147.09 Mpc (Planck 2018)

---

## 2. Datasets

| Dataset | N pontos | Observável | Tratamento |
|---------|----------|-----------|------------|
| Moresco H(z) 2022 | 33 | H(z) [km/s/Mpc] | χ² direto |
| DESI DR2 BAO | 13 | DM/rd, DH/rd, DV/rd | χ² com matriz de cov. 2×2 |
| Pantheon+SH0ES | 1624 SNe | μ(z) | χ² com M_B marginalizado |

---

## 3. Resultado [E]

### 3.1 Parâmetros ótimos joint

| Parâmetro | Valor ótimo | Incerteza | Nota |
|-----------|-------------|-----------|------|
| H₀ | **68.71 km/s/Mpc** | [VAZIO] — requer MCMC | Entre Planck (67.4) e SH0ES (73) |
| Ωm | **0.3028** | [VAZIO] | Próximo ao Planck (0.315) |
| **Ωs0** | **0.0000** | — | Colapso — setor RLL removido |
| z_t | não identificado | — | Efeito zero com Ωs0=0 |
| w_t | não identificado | — | Efeito zero com Ωs0=0 |
| ΩΛ (derivado) | **0.6971** | — | |

### 3.2 χ² breakdown

| Dataset | χ² | χ²/dof | N |
|---------|-----|--------|---|
| Moresco H(z) | 21.859 | 0.781 | 33 |
| DESI DR2 BAO | 11.023 | 1.378 | 13 |
| Pantheon+ (M_B marg.) | 716.346 | 0.443 | 1624 |
| **Joint total** | **749.228** | **0.450** | **1670** |

### 3.3 Comparação com Parâmetros Nominais Planck

| Config | χ²_joint |
|--------|----------|
| Planck nominal (H₀=67.4, Ωm=0.315, Ωs0=0.02, z_t=1.0, w_t=0.3) | 776.560 |
| Ótimo joint (H₀=68.71, Ωm=0.3028, Ωs0=0) | 749.228 |
| **Δχ²** | **−27.33** |

Melhora de Δχ²=27.3 — significativa. **Toda a melhora vem de H₀ e Ωm, não de Ωs0.**

---

## 4. Achado Principal — Colapso Ωs0→0 Confirmado [E]

**Todos os 8 pontos de partida**, cobrindo H₀∈[67,70], Ωm∈[0.29,0.32], Ωs0∈[0.001,0.03], z_t∈[0.3,2.0], w_t∈[0.2,1.0], convergiram para **Ωs0=0.000**.

Este é um resultado mais forte do que o colapso observado no MCMC joint parcial documentado em `08_ARVORE_CONCEITUAL_RLL.md §Síntese`: mesmo com liberdade total de otimização em 5 dimensões, o setor RLL é removido pelos dados.

**Implicação**: com Ωs0=0, o modelo RLL é idêntico ao ΛCDM:
```
E²(z)|_{Ωs0→0} = Ωm(1+z)³ + Ωr(1+z)⁴ + ΩΛ   ≡   ΛCDM
```

Os parâmetros z_t e w_t tornam-se **não-identificados** (qualquer valor produz o mesmo E(z)). A otimização joint sobre os datasets atuais não encontra evidência de setor adicional.

---

## 5. Análise AIC

| Modelo | k | χ²_joint | AIC |
|--------|---|----------|-----|
| ΛCDM (H₀, Ωm) | 2 | 749.228 | **753.228** |
| RLL (H₀, Ωm, Ωs0, z_t, w_t) | 5 | 749.228 | **759.228** |
| **ΔAIC(RLL − ΛCDM)** | | | **+6.0** |

RLL com k=5 é **penalizado por +6 AIC** sem ganho em χ². O modelo mais parcimonioso é preferido.

**Nota**: Este ΔAIC=+6 é diferente do ΔAIC=+3.8 em F-COS-01 (Pantheon+ apenas, ajuste de z_t e w_t fixos). O joint fix inclui BAO e H(z), que penalizam os parâmetros extras mais fortemente.

---

## 6. Interpretação Epistêmica

### 6.1 O que este resultado implica

1. **O conjunto de dados atual (Pantheon+ + DESI DR2 BAO + Moresco H(z)) não requer Ωs0 > 0**. O ΛCDM com H₀≈68.7 e Ωm≈0.303 descreve os dados igualmente bem.

2. **Os parâmetros RLL ótimos são H₀=68.71 e Ωm=0.303** — valores fisicamente plausíveis, entre Planck e SH0ES para H₀.

3. **Este resultado não falsifica o RLL** — apenas indica que com dados atuais e parâmetros Planck para rd, Ωs0=0 é preferido. Com dados mais precisos (DESI DR3, Euclid) ou rd diferente, o resultado pode mudar.

### 6.2 Caminhos para revisar

| Revisão | Por que pode mudar | Status |
|---------|------------------|--------|
| MCMC com prior Ωs0 > 0 | Pode encontrar região com Ωs0 > 0 e χ² menor | TOKEN_VAZIO G1 |
| rd livre | rd=147.09 Mpc é fixo; rd otimizado pode mudar Ωm/H₀ | TOKEN_VAZIO P1 |
| DESI DR3 + Euclid | Mais pontos BAO podem discriminar setor extra | Aguarda 2027 |
| Dados em altos z (H(z) > 2) | Logística tem maior diferença vs ΛCDM em z alto | TOKEN_VAZIO P2 |

### 6.3 Relação com outros resultados do repositório

- **F-COS-03 FAIL**: confirmado — z_t não é identificado pelos dados atuais
- **F-COS-04 FAIL proxy**: ln(B₁₀)=−6.24 consistente — Bayesianamente, ΛCDM é preferido
- **08_ARVORE_CONCEITUAL_RLL §Síntese colapso Ωs0→0**: ✅ confirmado por otimização joint
- **P-RLL-03 (Ωs0 < 0.05)**: ✅ confirmada — de fato Ωs0→0

---

## 7. Status dos Falsificadores (atualizado)

| ID | Status anterior | Atualização FASE 16 |
|----|----------------|---------------------|
| F-COS-01 | ✅ PASS ΔAIC=3.805 [E] | Mantido — fit Pantheon+ apenas |
| F-COS-02 | ✅ PASS χ²_red=0.4387 [E] | Mantido |
| F-COS-03 | ✗ FAIL z_t não identificado [E] | ✅ Reforçado — joint confirma não-identificabilidade |
| F-COS-04 | ✗ FAIL ln(B₁₀)=−6.24 proxy [C] | ✅ Reforçado — AIC joint: ΔAIC=+6 |
| F-COS-05 | ✅ PASS χ²_DESI=93.81 [E] | Mantido |

**Resumo**: 2/5 PASS · 2/5 FAIL · 1/5 TOKEN_VAZIO P0 (G1: MCMC joint com amostrador)

---

## 8. Próximos Atos Científicos

```
P0 — G1: MCMC joint com prior Ωs0 > 0 (forçar setor não-zero)
         Disparar rll-validacao-cientifica-completa.yml modo=completo
         Job joint_mcmc_p0 com emcee 32 walkers × 2000 steps

P1 — rd livre: expandir para 6 parâmetros (H₀, Ωm, Ωs0, z_t, w_t, rd)
               Requer CMB likelihood ou prior Gaussian em rd

P1 — Dados H(z) em z > 2: reduzir TOKEN_VAZIO em região onde f(z) ≠ ΛCDM
```

---

*Documento criado em FASE 16 (2026-07-13). Referências: `results/rll_joint_parametrizacao.json`, `08_ARVORE_CONCEITUAL_RLL.md §Síntese`.*

---

## Adendo FASES 20–22 (2026-07-15/16)

A seção 8 ("Próximos Atos Científicos") acima está **superada**. O gap P0 ali listado foi fechado:

| Gap | Status anterior (FASE 16) | Status final (FASE 20) |
|-----|--------------------------|----------------------|
| G1: MCMC joint com prior Ωs0 > 0 | TOKEN_VAZIO P0 | ✅ FECHADO [E] — Ωs0 UL95=0.00178 (emcee 32 walkers × 1500 steps, burn=400) |
| G3: Bayes Factor formal | TOKEN_VAZIO P0 | ✅ FECHADO [E] — ln(B₁₀)=−6.190±0.691 (dynesty nlive=150) |

**Resultado chave**: O MCMC com prior Ωs0 > 0 (32×1500 emcee, N=1677 pts) confirmou que o setor RLL é sub-dominante ao nível de 95% UL. A coluna à direita não falsifica a FASE 16: Ωs0 → 0 em otimização MAP e Ωs0 < 0.00178 em MCMC são consistentes. A diferença é que o MCMC provê limites formais de credibilidade.

O ΔAIC (F-COS-04 proxy) da seção 7 deste documento se tornou resultado empírico formal: ln(B₁₀) = −6.190 ± 0.691, |ln B₁₀| > 5 → escala Jeffreys "muito forte" para ΛCDM.

`claim_allowed = false` por resultado empírico. `TOKEN_VAZIO estrutural = 0`.
