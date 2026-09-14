# Grafo Epistêmico de Sessão FASE 17–20

**Sessão**: SESSION_FASE17_20_2026-07-14_15  
**Método**: ψ→χ→Δ→Σ (reanálise epistêmica)  
**Branch histórica**: `claude/rll-cronologia-auditoria-qyvn83`  
**Escopo congelado**: FASE 17–20  
**Estado corrente acoplado**: FASE 22 via `current_state_overlay.json`  
**claim_allowed**: false

> Este diretório preserva um snapshot histórico. Estados posteriores não são reescritos retroativamente: entram por sobreposição explícita, com fonte, transição e limitação residual.

---

## Evolução FASE 17→20: Tabela de Afirmações

| ID | Texto (resumido) | Estado no snapshot | Estado corrente | Dependências |
|----|-----------------|-------------------|----------------|-------------|
| C-F17-01 | Ωs0=0.012 era artefato E&H | VERIFICADO_NA_FONTE | SUPERSEDED preservado | C-F18-02, C-F19-01 |
| C-F18-01 | rs_star calib +0.1988 Mpc → chi²_CMB≈0 | VERIFICADO_NA_FONTE | VERIFIED_LIMITED | planck_2018_vi, chen_2019 |
| C-F18-02 | Bias E&H: Δrd=+3.614 Mpc | VERIFICADO_NA_FONTE | VERIFIED_LIMITED | planck_2018_vi, eisenstein_hu_1998 |
| C-F19-01 | rd calib −3.614 Mpc corrige viés no ponto Planck | VERIFICADO_NA_FONTE | VERIFIED_LIMITED | C-F18-02 |
| C-F19-02 | Com rd correto, Ωs0→0 | VERIFICADO_NA_FONTE | VERIFIED_LIMITED | C-F19-01, C-F17-01 |
| C-F19-03 | ΔBIC=+22.27 → ΛCDM forte | VERIFICADO_NA_FONTE | proxy substituído por nested sampling | C-F19-02 |
| C-F20-01 | Ωs0 UL95=0.00178 (MCMC) | VERIFICADO_NA_FONTE | VERIFIED_LIMITED; cadeia ainda curta | C-F19-01 |
| C-F20-02 | ln(B₁₀)=−6.190±0.691 (dynesty) | VERIFICADO_NA_FONTE | VERIFIED_LIMITED | C-F19-01 |
| C-F20-03 | Evidência muito forte para ΛCDM (Jeffreys) | VERIFICADO_NA_FONTE | VERIFIED_LIMITED | C-F20-02 |
| C-F20-04 | G4: bias E&H varia no espaço paramétrico | TOKEN_VAZIO no snapshot | VERIFIED_LIMITED na FASE 22 | C-F19-01, grid FASE22 |

---

## Cadeia paper→claim→código→teste→artefato

```text
planck_2018_vi  ──SUPPORTS──► rd_calibration
                                     │
                                IMPLEMENTS
                                     │
                         rll_fase19_rd_calibrado.py
                                     │
                     ┌───────────────┤
                     │           PRODUCES
                     │               │
                  CLOSES        rll_fase19_rd_calibrado.json
                     │               │
                    G2          SUPPORTS──► C-F19-01 (rd calib OK)
                                     │
                                SUPPORTS──► C-F19-02 (Ωs0→0)
                                     │
                                SUPPORTS──► C-F19-03 (ΔBIC=+22.27)

foreman_mackey_2013 ──USED_IN──► rll_fase20_mcmc_bayes.py
speagle_2020        ──USED_IN──► rll_fase20_mcmc_bayes.py
                                           │
                      ┌────────────────────┤
                      │                PRODUCES
                      │                    │
                CLOSES: G1, G3     rll_fase20_mcmc_bayes.json
                                           │
                                SUPPORTS──► C-F20-01 (Ωs0 UL95=0.00178)
                                SUPPORTS──► C-F20-02 (ln(B₁₀)=−6.190)
                                SUPPORTS──► C-F20-03 (Jeffreys: muito forte)

rll_fase22_g4_eh_bias_grid.py ──PRODUCES──► rll_fase22_g4_eh_bias_grid.json
                                           │
                                        CLOSES
                                           │
                           G4: TOKEN_VAZIO(snapshot)
                                → VERIFIED_LIMITED(current)
                                           │
                       residual: CAMB/RECFAST por passo = TOKEN_VAZIO

C-F17-01 ──NOT_EVIDENCE_FOR──► [superioridade do modelo RLL]
```

---

## Contradição Resolvida

| ID | Conflito | Mecanismo | Resolução |
|----|----------|-----------|-----------|
| CONTRADICTION-01 | Ωs0=0.012 (FASE18-E) vs Ωs0≈0 (FASE19-20) | rd_EH +3.61 Mpc → otimizador compensava com Ωs0>0 | Calibração rd correta → Ωs0 colapsa a zero; FASE18-E SUPERSEDED |

---

## Estado dos gaps: snapshot e presente

| ID | Estado no snapshot FASE 20 | Estado até FASE 22 | Resultado / limitação |
|----|----------------------------|---------------------|------------------------|
| G1 | FECHADO | FECHADO | Ωs0 UL95=0.00178; convergência ainda pode ser aprofundada |
| G2 | FECHADO | FECHADO | calibração −3.614 Mpc no ponto Planck |
| G3 | FECHADO | FECHADO | −6.190±0.691, favorecendo ΛCDM |
| G4 | TOKEN_VAZIO [H] | VERIFIED_LIMITED / CLOSED_AS_QUANTIFIED_SYSTEMATIC | grade 10×10; sistemático posterior 0.7214 Mpc; CAMB/RECFAST por passo continua TOKEN_VAZIO P1 |

O fechamento de G4 elimina a lacuna desconhecida, não o sistemático. A sobreposição não promove `claim_allowed`, não apaga o snapshot e não substitui análise de precisão.

---

## Heurísticas H1–H8 Aplicadas

| H | Nome | Aplicação |
|---|------|-----------|
| H1 | Proveniência antes de embeddings | Cada C_i tem source, origin, time explícitos |
| H2 | Deduplicação bibliográfica determinística | sources.bib usa DOI/arXivID como chave |
| H3 | Estado epistemológico obrigatório | claims e gaps têm estado explícito |
| H4 | Ausência tem escopo temporal | TOKEN_VAZIO do snapshot não é confundido com estado atual |
| H5 | Separar semântica de evidência | NOT_EVIDENCE_FOR para diagnóstico vs superioridade RLL |
| H6 | Baseline antes do modelo sofisticado | MCMC → nested sampling → análise sistemática G4 |
| H7 | Divisão temporal | FASE 17–20 preservada; FASE 22 acoplada por overlay |
| H8 | Fórmula só após operacionalização | fórmulas têm variáveis, domínio, dados e artefatos |

---

## Referências Cruzadas

- `current_state_overlay.json` — transição temporal G4 e limitação residual.
- `claims.jsonl` — afirmações atômicas C_i.
- `sources.bib` — referências bibliográficas.
- `entities.jsonl` / `relations.jsonl` — nós e arestas tipadas.
- `graph.graphml` — grafo histórico FASE 17–20.
- `docs/cronologia-auditoria/21_FASE22_G4_EH_BIAS_GRID.md` — evidência de atualização corrente.

---

*Snapshot gerado por `scripts/build_session_grafo_fase17_20.py`; estado corrente sincronizado por `scripts/build_session_grafo_current_state_overlay.py`; claim_allowed: false.*
