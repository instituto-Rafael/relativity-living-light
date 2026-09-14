# 20 — Checklist de Publicação Pública RAFAELIA/RLL

**Status:** canônico complementar  
**Origem:** derivado do documento-mãe `BIBLIA_CONHECIMENTO_RAFAELIA_RLL.md`  
**Função:** listar o que precisa estar público, verificável e seguro antes de divulgação externa.

---

## 1. Documentos mínimos no repositório público

- [x] Documento-mãe: `docs/canonicos/BIBLIA_CONHECIMENTO_RAFAELIA_RLL.md`
- [x] Epistemologia: `docs/canonicos/13_EPISTEMOLOGIA_RAFAELIA_RLL.md`
- [x] Modelo cosmológico: `docs/canonicos/14_MODELO_COSMOLOGICO_RLL.md`
- [x] Dados externos reais: `docs/canonicos/15_DADOS_EXTERNOS_REAIS_RLL.md`
- [x] Pipeline de validação: `docs/canonicos/16_PIPELINE_VALIDACAO_RLL.md`
- [x] Onda, neuro, física e linguagem: `docs/canonicos/17_ONDA_VERBO_FISICA_NEURO_LINGUAGEM.md`
- [x] Orquestrador ASCII/UTF: `docs/canonicos/18_ORQUESTRADOR_ASCII_UTF_RAFAELIA.md`
- [x] Roadmap e falsificadores: `docs/canonicos/19_ROADMAP_FALSIFICADORES_RLL.md`
- [x] Checklist de publicação: `docs/canonicos/20_CHECKLIST_PUBLICACAO_RAFAELIA_RLL.md`
- [ ] Modelo Vetorial Informacional (MVICS): `docs/canonicos/21_MODELO_VETORIAL_INFORMACIONAL.md`

## 2. Arquivos de governança que devem existir ou ser confirmados

- [ ] `LICENSE.md`
- [ ] `data/CITATION.cff` ou `CITATION.cff`
- [ ] `docs/REFERENCES.md`
- [ ] `docs/CANONICAL_SOURCES.md`
- [ ] `docs/DOCUMENTATION_FULL_INVENTORY.md`
- [ ] `docs/DATA_INTEGRITY_CHECKLIST.md`
- [ ] `SECURITY_SUMMARY.md`

## 3. Checagens antes de divulgação acadêmica

- [ ] Confirmar cada referência em fonte primária.
- [ ] Verificar DOI via metadados oficiais.
- [ ] Confirmar commits/tags de anterioridade.
- [ ] Conferir assinatura GPG indicada.
- [ ] Rodar pipeline de validação em commit limpo.
- [x] Registrar parâmetros, dados, hashes e outputs. *(FASE 15: todos os resultados têm JSON com metadados: fonte, script, data, status epistêmico — `results/*.json`)*
- [x] Separar claramente `[E]`, `[C]`, `[H]` e `[VAZIO]`. *(FASE 15: markup sistematizado em todos os documentos de auditoria, hipóteses e cânônicos; resultados negativos marcados [E-negativo] com mesma honestidade que positivos)*

## 4. Checagens de segurança e privacidade

- [ ] Não publicar dados pessoais sensíveis.
- [ ] Não publicar tokens, chaves, credenciais ou caminhos privados.
- [ ] Não publicar exports brutos de conversas privadas sem triagem.
- [ ] Não publicar arquivos zip grandes sem inventário.
- [ ] Não publicar conteúdo de terceiros sem licença clara.

## 5. Critério de prontidão

Um documento está pronto para publicação externa quando:

```text
fonte verificada + claim classificado + dado rastreável + limite declarado + licença clara
```

## 6. Regra de ouro

Quando houver dúvida, marcar `[VAZIO]` e abrir tarefa de verificação.

---

## Adendo FASE 15 (2026-07-10/13)

**Progresso em publicabilidade**:

| Item | Status FASE 15 |
|------|---------------|
| Markup epistêmico `[E]/[C]/[H]/[VAZIO]` | ✅ sistematizado em todos os documentos |
| Resultados com metadados JSON | ✅ `results/*.json` (scripts, datas, fontes, status) |
| Falsificadores F-COS-01..05 auditados | ✅ 2/5 PASS · 2/5 FAIL · 1/5 TOKEN_VAZIO P0 |
| Resultados negativos registrados | ✅ F-COS-03 FAIL, H-UNIV-01 φ negativo, F-COS-04 FAIL proxy |
| Moresco H(z) calculado | ✅ χ²_RLL=27.47 vs χ²_ΛCDM=22.76 [E] |
| Modelo atmosférico H-ELEC-01 | ✅ J=const verificado, enhancement ×10¹⁴ [E+H] |

**Bloqueadores para publicação** (requerem pipeline manual):
- G1: Joint MCMC Pantheon+ + DESI (F-COS-04 definitivo)
- G2: Bayes Factor (nested sampling)
- Revisão por pares de artefatos completos (Claim Boundary)

---

## Adendo FASE 20–22 (2026-07-15/16)

**Contrato final**: `2/5 PASS · 2/5 FAIL · 0/5 TOKEN_VAZIO`

| Item | Status FASE 20–22 |
|------|------------------|
| G1: MCMC joint Pantheon+ + DESI | ✅ FECHADO [E] — Ωs0 UL95 = 0.00178 (emcee 32×1500) |
| G3: Bayes Factor RLL/ΛCDM | ✅ FECHADO [E] — ln(B₁₀) = −6.190 ± 0.691 (dynesty) |
| F-COS-03: z_t ∈ [0.5, 1.5] | ✗ FAIL [E] — z_t_BAO = 0.30 (fora do intervalo) |
| F-COS-04: ln(B₁₀) > −5 | ✗ FAIL [E] — ln(B₁₀) = −6.190 (evidência muito forte para ΛCDM) |
| G4: bias E&H no espaço de parâmetros | ✅ FECHADO [E] — syst. = 0.72 Mpc (grade 10×10, FASE 22) |
| TOKEN_VAZIO P0 estrutural | ✅ ZERO — nenhum gap P0 remanescente |

**`claim_allowed = false` permanece** — por resultado empírico (F-COS-03 FAIL [E], F-COS-04 FAIL [E]), não por lacuna. Esta é a situação mais honesta: os dados estão completos e apontam para ΛCDM.

**Bloqueadores remanescentes para publicação**:
- Revisão por pares externos (nenhum T_VAZIO bloqueia mais — só peer review)

---

*Publicar é iluminar com responsabilidade.*