# z_t Scan — Resultado Real (Falsificador F-COS-03)

**Data**: 2026-07-07 | **Fase**: FASE 8 (executado) / FASE 15 (documentado)  
**Status epistêmico**: [E] resultado numérico de scan executado  
**Script**: `scripts/slingshot_zt_falsification.py`  
**Output**: `results/zt_scan/summary.json`

> *Documento análogo ao `09_PANTHEON_RESULTADO_REAL.md` para o scan de z_t com dados H(z)+BAO.*

---

## 1. Propósito

O falsificador **F-COS-03** exige que z_t (centro da transição logística RLL) esteja no intervalo
`[0.5, 1.5]` quando ajustado contra dados observacionais H(z) + DESI DR2 BAO.

Este documento registra o resultado do scan executado em FASE 8 com parâmetros nominais
(Ωs0=0.02, w_t=0.3, H₀=67.4, Ωm=0.315), varrendo z_t ∈ {0.3, 0.5, 0.7, 0.9, 1.0, 1.2, 1.5, 1.8, 2.0}.

---

## 2. Dados do Scan

### 2.1 χ² por valor de z_t

| z_t | χ²_Hz | χ²_BAO | χ²_total |
|-----|-------|--------|----------|
| **0.3** | 27.013 | **31.084** | **58.098** ← mínimo total/BAO |
| 0.5 | 27.075 | 32.399 | 59.474 |
| 0.7 | 27.202 | 34.002 | 61.204 |
| 0.9 | 27.376 | 35.598 | 62.974 |
| 1.0 | 27.465 | 36.293 | 63.758 |
| 1.2 | 27.605 | 37.339 | 64.944 |
| 1.5 | 27.603 | 37.947 | 65.550 |
| 1.8 | 27.183 | 37.421 | 64.604 |
| **2.0** | **26.606** | 36.460 | 63.066 ← mínimo Hz |

### 2.2 Mínimos por componente

| Dataset | z_t de mínimo χ² |
|---------|-----------------|
| DESI DR2 BAO | **z_t = 0.3** |
| Moresco H(z) | **z_t = 2.0** |
| Total (Hz + BAO) | **z_t = 0.3** |

---

## 3. Resultado dos Falsificadores Internos

Três sub-falsificadores de F-COS-03 avaliados pelo protocolo `05_slingshot_zt_falsification.yml`:

| Sub-falsificador | Descrição | Threshold | Resultado | Status |
|-----------------|-----------|-----------|---------|--------|
| F_ZT_01 | Curvatura de χ²_BAO em torno do mínimo — detecta preferência | Δχ² < 2.92 OU curvatura ≠ null | Δχ²=2.917; curvatura=null (sem mínimo local) | **FAIL** |
| F_ZT_02 | Consistência entre z_t_BAO e z_t_Hz — requer acordo entre datasets | \|z_t_BAO − z_t_Hz\| < 0.2 | \|0.3 − 2.0\| = 1.7 | **FAIL** |
| F_ZT_03 | w_eff(z=0) em z_t=0.5 — verifica que setor não cruza zero em z baixo | w_eff(z=0) < −0.85 | −0.841 (margem: +0.009) | **FAIL** |

**Veredicto de F-COS-03** [E]: **FAIL**

---

## 4. Interpretação Epistêmica

### 4.1 Por que z_t ótimo ≠ [0.5, 1.5]?

O scan mostra que χ²_BAO é **monotonicamente decrescente** conforme z_t diminui de 2.0 para 0.3. Não há mínimo local no intervalo [0.5, 1.5] — o vetor χ²_BAO(z_t) é uma rampa monotônica (curvatura = null em F_ZT_01).

Isso significa que, com parâmetros nominais (Ωs0=0.02, w_t=0.3), o BAO prefere z_t fora do intervalo fisicamente motivado. O modelo RLL, nessa configuração, não tem preferência interna por nenhum z_t no range de interesse.

### 4.2 Interpretação do F_ZT_02 (discordância Hz vs BAO)

- z_t_BAO = 0.3 (setor RLL mínimo impacto no BAO, parâmetro fora do intervalo)
- z_t_Hz = 2.0 (setor RLL com transição em z alto, também fora do intervalo, apenas por outro extremo)
- Discordância: 1.7 (muito acima do threshold 0.2)

Isso confirma que os dois datasets puxam z_t em direções opostas — inconsistência interna do modelo com parâmetros nominais.

### 4.3 F_ZT_03: resultado marginal

w_eff(z=0) em z_t=0.5 = −0.841, threshold < −0.85. A margem é de apenas +0.009 — quase passando. Isso indica que a assinatura w_eff > 0 do setor padrão pode ser parcialmente suprimida com otimização fina de w_t, mas os outros dois falsificadores já invalidam F-COS-03.

### 4.4 Relação com colapso Ωs0→0

O resultado de F-COS-03 FAIL é consistente com o colapso Ωs0→0 no otimizador joint (documentado em `08_ARVORE_CONCEITUAL_RLL.md §Síntese`): o modelo RLL com Ωs0 nominal não encontra um regime onde z_t seja preferido pelos dados BAO. O otimizador resolve a tensão removendo o setor (Ωs0→0), ao invés de ajustar z_t para dentro do intervalo.

---

## 5. Status do Falsificador F-COS-03

```
F-COS-03: z_t ∈ [0.5, 1.5] — scan slingshot  FAIL [E]

Resultado: z_t_BAO_ótimo = 0.3, fora de [0.5, 1.5]
Sub-falsificadores: F_ZT_01 FAIL, F_ZT_02 FAIL, F_ZT_03 FAIL (por margem)
Status epistêmico: [E] scan executado com parâmetros nominais Planck

Desbloqueador para revisão: MCMC joint (G1) — otimização livre de (H0, Ωm, Ωs0, z_t, w_t)
pode encontrar configuração onde z_t ∈ [0.5, 1.5] é preferido com Ωs0 > 0.
F-COS-03 revisionável quando G1 executar.
```

---

## 6. Atualização do STATUS de Falsificadores (pós este documento)

| ID | Status anterior | Status atual |
|----|----------------|-------------|
| F-COS-01 | TOKEN_VAZIO (CI) | ✅ PASS — ΔAIC=3.805 [E] |
| F-COS-02 | TOKEN_VAZIO (CI) | ✅ PASS — χ²_red=0.4387 [E] |
| **F-COS-03** | TOKEN_VAZIO (CI) | **✗ FAIL — z_t_BAO=0.3 ∉ [0.5,1.5] [E]** |
| F-COS-04 | TOKEN_VAZIO P0 | ✗ FAIL (proxy BIC) — ln(B₁₀)=−6.24 [C] |
| F-COS-05 | PASS 93.81 | ✅ PASS — 93.81 [E] |

**Resumo atualizado**: 2/5 PASS · 2/5 FAIL ([E] + proxy [C]) · 1/5 TOKEN_VAZIO P0

**Nota de integridade**: resultado FAIL é registrado com a mesma honestidade que PASS. F-COS-03 FAIL **não invalida** o modelo — indica que com parâmetros nominais e otimização marginal, o z_t preferido pelos dados BAO é 0.3. MCMC joint pode revelar configuração diferente com Ωs0 > 0.

---

*Documento criado em FASE 15 (2026-07-10) para registrar resultado de FASE 8.*  
*Referências: `results/zt_scan/summary.json`, `CONTRATO_FALSIFICADORES_RLL.md`, `11_AUDIT_FINAL_STATUS.md §4`.*
