# Doc 20 — Grafo Epistêmico de Sessão FASE 17–20

**Data**: 2026-07-16 | **Método**: ψ→χ→Δ→Σ | **claim_allowed**: false

> *"Cada afirmação deve ter proveniência, tipo, tempo e estado epistêmico explícitos — ou não é afirmação, é ruído."* — RAFAELIA

---

## 1. Motivação: Sessão como Grafo Epistêmico

Nas FASES 17–20, o trabalho de análise produziu um conjunto de artefatos interligados: papers externos, código computacional, resultados numéricos e decisões metodológicas. Tratá-los como texto linear perde a estrutura causal e epistêmica.

O esquema ψ→χ→Δ→Σ propõe que cada sessão seja representada como um **grafo temporal multiplex** com tipos de nós e arestas explícitos, preservando TOKEN_VAZIO onde evidência não existe.

**Saída concreta desta fase**: 12 artefatos em `results/session_grafo_fase17_20/`, gerados pelo script determinístico `scripts/build_session_grafo_fase17_20.py`.

---

## 2. Schema de Afirmações Atômicas C_i

Cada afirmação no `claims.jsonl` tem 12 campos (conforme gerado por `build_session_grafo_fase17_20.py`):

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `claim_id` | string | Identificador único (ex: C-F19-01) |
| `text` | string | Texto proposicional completo |
| `type` | string | EMPIRICAL / METHODOLOGICAL / INTERPRETIVE / TOKEN_VAZIO |
| `origin` | string | Sessão ou fase de origem (ex: "results/rll_fase19_rd_calibrado.json §rd") |
| `time` | ISO 8601 | Data aproximada da afirmação |
| `scope` | string | Descrição do escopo e limitações da afirmação |
| `evidence` | string | Tipo de evidência (ex: "numerical_integration", "bayesian_mcmc") |
| `status` | string | VERIFICADO_NA_FONTE / HIPÓTESE / TOKEN_VAZIO / REFUTADO |
| `confidence` | float | [0,1] — 0.95 = epistêmico firme |
| `dependencies` | array | IDs de claims ou papers que esta pressupõe |
| `falsifier` | string | Condição que refutaria esta afirmação |
| `claim_allowed` | bool | Sempre false — fronteira epistêmica RLL |

---

## 3. Tipos de Nós (18 tipos)

| Tipo | Exemplos nesta sessão |
|------|-----------------------|
| SOURCE | Planck 2018 VI, E&H 1998 |
| PAPER | planck_2018_vi, eisenstein_hu_1998 |
| DATASET | Pantheon+SH0ES, DESI DR2, Moresco 2022 |
| CLAIM | C-F17-01 … C-F20-04 |
| CONCEPT | rd_calibration, rs_star_calibration, E&H_bias |
| FORMULA | E²(z), f(z), rd_correction |
| VARIABLE | Ωs0, H₀, rd, z_drag |
| METHOD | emcee MCMC, dynesty nested sampling |
| EXPERIMENT | EXP-01 MCMC G1, EXP-02 Nested G3 |
| RESULT | rll_fase19_rd_calibrado.json, rll_fase20_mcmc_bayes.json |
| REPOSITORY | instituto-rafael/relativity-living-light |
| FILE | scripts/rll_fase19_rd_calibrado.py |
| COMMIT | PR #551, #553, #554 |
| ACTION | FASE18E_implementada, PR553_merged |
| DECISION | usar_rd_planck, usar_emcee_g1 |
| AUDIT_DOC | Doc 17, Doc 18, Doc 19 |
| CONTRADICTION | CONTRADICTION-01 (Ωs0=0.012 vs Ωs0≈0) |
| GAP | G1, G2, G3 (fechados), G4 (aberto) |

**Contagem nesta sessão**: 44 entidades em `results/session_grafo_fase17_20/entities.jsonl`

---

## 4. Tipos de Arestas (14 tipos)

| Tipo | Semântica | Exemplos |
|------|-----------|---------|
| SUPPORTS | A evidencia B | Planck 2018 VI → rd_calibration |
| CONTRADICTS | A conflita com B | E&H 1998 ↔ Planck 2018 VI (Δrd=+3.61 Mpc) |
| DERIVED_FROM | B derivado de A | eh_bias ← E&H 1998 |
| CITES | A referencia B | script → E&H 1998 |
| USES_METHOD | A aplica método B | EXP-01 MCMC → emcee |
| USES_DATA | A usa dataset B | EXP-01 → Pantheon+ |
| IMPLEMENTS | A código implementa B conceito | script → rd_calibration |
| TESTS | A testa B | EXP-01 MCMC → C-F20-01 |
| FALSIFIES | A refuta B | CONTRADICTION-01 → C-FASE18E-Ωs0 |
| REQUIRES | A depende de B | C-F20-01 → C-F19-01 |
| SUPERSEDES | A substitui B | rll_fase19_rd_calibrado.json → rll_fase18e_calibrado.json |
| DUPLICATES | A duplica B | — (nenhum nesta sessão) |
| ANALOGOUS_TO | A análogo a B | — (nenhum nesta sessão) |
| **NOT_EVIDENCE_FOR** | A **não** evidencia B | C-F17-01 → validação RLL |

A aresta `NOT_EVIDENCE_FOR` é crítica: o diagnóstico de que Ωs0=0.012 era artefato (C-F17-01) **não constitui evidência de superioridade do modelo RLL** — é resultado do bias, não do modelo.

---

## 5. Grafo Multiplex Temporal G_t

```
G_t = (V, E_sem, E_bib, E_exec, E_epi, E_temp)
```

| Camada | Conteúdo | Arquivo |
|--------|----------|---------|
| E_sem | Relações semânticas (SUPPORTS, CONTRADICTS...) | relations.jsonl |
| E_bib | Citações bibliográficas (CITES) | sources.bib + relations.jsonl |
| E_exec | Cadeia computacional (IMPLEMENTS, PRODUCES, TESTS) | relations.jsonl |
| E_epi | Estado epistêmico dos nós (VERIFICADO, TOKEN_VAZIO...) | entities.jsonl |
| E_temp | Ordem temporal FASE 17→18→19→20 | actions.jsonl |

---

## 6. Tabela Completa de Afirmações C_i

| ID | Texto | Tipo | Status | Confiança | Falsificador |
|----|-------|------|--------|-----------|--------------|
| C-F17-01 | Ωs0=0.012 (FASE18-E) era artefato do viés E&H em rd — não sinal físico | METHODOLOGICAL | VERIFICADO_NA_FONTE | 0.97 | Ωs0>0 persistir com rd=rd_Planck |
| C-F18-01 | Calibração rs_star=+0.1988 Mpc → chi²_CMB(Planck 2018)=0.021 | EMPIRICAL | VERIFICADO_NA_FONTE | 0.99 | chi²_CMB>1 com mesma calib |
| C-F18-02 | Bias E&H: rd_EH=150.704 Mpc vs rd_Planck=147.09 Mpc → Δ=+3.614 Mpc | EMPIRICAL | VERIFICADO_NA_FONTE | 0.99 | rd_Planck revisado para ≈rd_EH |
| C-F19-01 | Calibração rd=−3.614 Mpc corrige viés E&H; rd_calib=147.09 Mpc | EMPIRICAL | VERIFICADO_NA_FONTE | 0.99 | rd_Planck revisado >148 Mpc |
| C-F19-02 | Com rd correto, MAP RLL: Ωs0→0 (9e-17), idêntico ao ΛCDM | EMPIRICAL | VERIFICADO_NA_FONTE | 0.98 | Ωs0_MAP>0.001 com rd calibrado |
| C-F19-03 | ΔBIC=+22.27 (RLL−ΛCDM) → evidência forte para ΛCDM na escala Jeffreys | INTERPRETIVE | VERIFICADO_NA_FONTE | 0.95 | ΔBIC<6 com mesmos dados |
| C-F20-01 | Ωs0 < 0.00178 (95% UL, MCMC emcee 32×1500, n=1677) | EMPIRICAL | VERIFICADO_NA_FONTE | 0.93 | MCMC não convergir ou UL>0.01 |
| C-F20-02 | ln(B₁₀)=−6.190±0.691 (dynesty nested sampling, nlive=150) | EMPIRICAL | VERIFICADO_NA_FONTE | 0.96 | ln(B₁₀)>−5 ou erro>2 |
| C-F20-03 | |ln(B₁₀)|=6.19 > 5.0 → evidência muito forte para ΛCDM (escala Jeffreys 1961) | INTERPRETIVE | VERIFICADO_NA_FONTE | 0.95 | Escala Jeffreys revisada |
| C-F20-04 | G4: bias E&H varia em espaço de parâmetros (Ωm·h², Ωb·h²) — não uniforme | TOKEN_VAZIO | TOKEN_VAZIO | 0.70 | Grade rd_EH(Ωm,Ωb) mostra variação<1% |

---

## 7. Relações Selecionadas (25+ arestas tipadas)

| Origem | Tipo | Destino | Nota |
|--------|------|---------|------|
| planck_2018_vi | SUPPORTS | C-F19-01 | rd_Planck=147.09 Mpc Tabela 2 |
| planck_2018_vi | SUPPORTS | C-F18-01 | chi²_CMB com params Planck |
| eisenstein_hu_1998 | CONTRADICTS | planck_2018_vi | Δrd=+3.61 Mpc pela fórmula EH |
| C-F17-01 | NOT_EVIDENCE_FOR | [validação RLL] | diagnóstico ≠ sinal do modelo |
| C-F17-01 | DERIVED_FROM | eh_bias | causa do artefato |
| rll_fase19_rd_calibrado.py | IMPLEMENTS | rd_calibration | correção numérica |
| rll_fase19_rd_calibrado.py | PRODUCES | rll_fase19_rd_calibrado.json | artefato principal |
| rll_fase19_rd_calibrado.json | SUPERSEDED_BY | — | (supersede de FASE18-E) |
| rll_fase18e_calibrado.json | SUPERSEDES | — | supersedida por FASE19 |
| rll_fase19_rd_calibrado.json | SUPPORTS | C-F19-01 | resultado numérico confirma |
| rll_fase19_rd_calibrado.json | SUPPORTS | C-F19-02 | Ωs0_MAP≈0 com rd correto |
| rll_fase20_mcmc_bayes.py | CLOSES | G1 | MCMC posterior de Ωs0 |
| rll_fase20_mcmc_bayes.py | CLOSES | G3 | Bayes Factor formal |
| foreman_mackey_2013 | USED_IN | rll_fase20_mcmc_bayes.py | emcee EnsembleSampler |
| speagle_2020 | USED_IN | rll_fase20_mcmc_bayes.py | dynesty NestedSampler |
| jeffreys_1961 | SUPPORTS | C-F20-03 | escala de interpretação |
| rll_fase20_mcmc_bayes.json | SUPPORTS | C-F20-01 | os0_upper95=0.00178 |
| rll_fase20_mcmc_bayes.json | SUPPORTS | C-F20-02 | lnB10=−6.190±0.691 |
| CONTRADICTION-01 | RESOLVES | C-F17-01 | Ωs0 0.012→0 explicado |

---

## 8. Contradição Resolvida

**CONTRADICTION-01**: Ωs0=0.012 (FASE 18-E) vs Ωs0≈0 (FASE 19–20)

- **Mecanismo**: rd_EH superestimado por +3.614 Mpc → otimizador compensava com Ωs0>0 para manter E(z) consistente com BAO
- **Resolução (FASE 19)**: Calibração aditiva rd_corr = rd_EH + (rd_Planck − rd_EH,Planck) → Ωs0_MAP colapsa a 9×10⁻¹⁷ (efetivamente zero)
- **Status**: RESOLVIDA — rll_fase18e_calibrado.json supersedido; toda análise subsequente usa rd calibrado

---

## 9. TOKEN_VAZIO — Estado Final

| ID | Descrição | Status | Prioridade | Resultado |
|----|-----------|--------|-----------|-----------|
| G1 | MCMC joint posterior Ωs0 | ✅ FECHADO | — | Ωs0 UL95=0.00178 (emcee 32×1500) |
| G2 | rd numérico correto (remove bias E&H) | ✅ FECHADO | — | rd=147.09 Mpc (calibração −3.614 Mpc) |
| G3 | Bayes Factor formal ln(B₁₀) | ✅ FECHADO | — | −6.190±0.691 (dynesty, Jeffreys: muito forte) |
| G4 | Mapeamento bias E&H em (Ωm·h², Ωb·h²) | ⬜ TOKEN_VAZIO | P3/H | Baixa prioridade; calibração aditiva funciona |

---

## 10. Heurísticas H1–H8 (aplicação nesta fase)

| H | Nome | Aplicação concreta |
|---|------|--------------------|
| H1 | Proveniência antes de embeddings | Cada C_i tem `source`, `origin`, `time` explícitos antes de `status` |
| H2 | Deduplicação bibliográfica determinística | `sources.bib` usa arXivID/DOI como chave; sem duplicatas |
| H3 | Estado epistemológico obrigatório | Todos os 10 claims têm `status` (VERIFICADO_NA_FONTE ou TOKEN_VAZIO) |
| H4 | Ausência tem três valores | `gaps.jsonl` usa: `FECHADO` / `TOKEN_VAZIO` / `not_examined` |
| H5 | Separar semântica de evidência | `NOT_EVIDENCE_FOR` para C-F17-01 vs validação do modelo RLL |
| H6 | Baseline antes do modelo sofisticado | MCMC emcee (baseline) → dynesty nested sampling (sofisticado) |
| H7 | Divisão temporal | Experimentos em sequência cronológica: FASE 17→18→19→20 |
| H8 | Fórmula só após operacionalização | `formulas.yaml` tem variáveis, domínio e dados antes de qualquer ajuste simbólico |

---

## 11. Artefatos Gerados (`results/session_grafo_fase17_20/`)

| Arquivo | Conteúdo | Tamanho |
|---------|----------|---------|
| `session_manifest.json` | Metadados da sessão; claim_allowed=false | 1.2 KB |
| `claims.jsonl` | 10 afirmações atômicas C_i (schema 10 campos) | 7.2 KB |
| `sources.bib` | 10 entradas BibTeX com DOI/arXiv | 4.0 KB |
| `entities.jsonl` | 44 nós tipados (18 tipos) | 6.9 KB |
| `relations.jsonl` | 44 arestas tipadas (14 tipos) | 4.6 KB |
| `contradictions.jsonl` | 1 registro (CONTRADICTION-01, RESOLVIDA) | 0.8 KB |
| `gaps.jsonl` | 4 registros G1-G4 (3 FECHADO, 1 TOKEN_VAZIO) | 1.9 KB |
| `actions.jsonl` | 7 ações documentadas | 1.5 KB |
| `formulas.yaml` | 6 fórmulas com variáveis e domínio | 3.5 KB |
| `experiments.yaml` | 3 experimentos (EXP-01 MCMC, EXP-02 Nested, EXP-03 Profile) | 3.4 KB |
| `graph.graphml` | Grafo GraphML com nós e arestas tipados | 15.8 KB |
| `report.md` | Relatório de síntese (tabela C_i, cadeia, contradição) | 5.4 KB |

**Script gerador**: `scripts/build_session_grafo_fase17_20.py` (determinístico, stdlib Python, offline)

---

## 12. Rastreabilidade de PRs

| PR | FASE | Conteúdo | Status |
|----|------|----------|--------|
| #551 | FASE 18 | rs_star calibração (+0.1988 Mpc), chi²_CMB=0.021 | ✅ MERGED 2026-07-14 |
| #553 | FASE 19 | rd calibração (−3.614 Mpc), Ωs0→0, ΔBIC=22.27 | ✅ MERGED 2026-07-14 |
| #554 | FASE 20 | MCMC G1 (Ωs0 UL95=0.00178), Bayes Factor G3 (ln(B₁₀)=−6.190) | ✅ MERGED 2026-07-15 |

---

*claim_allowed: false — grafo registra relações candidatas entre afirmações, fontes, código e artefatos. Não constitui prova de superioridade do modelo RLL. Revisão por pares requerida antes de qualquer afirmação pública.*
