# References — Crescimento Estrutural e Structure D

**Status:** `bibliography_curated_v1.0`  
**Canonical BibTeX:** [`references.bib`](references.bib)

## Referências internas rastreáveis

- `RAFAELIA_COSMO_STRUCTURE_D/paper/draft.md`
- `docs/PERTURBACOES_CRESCIMENTO.md`
- `docs/FRONTS_CLASSCAMB_VS_LN1PZ.md`
- `docs/modules/structure_d_equations.md`
- `docs/modules/structure_d_agn_feedback_bridge.md`
- `newadd/04_TM_m_inferencia_paper_ready.md`

## Referências externas canônicas

1. **Li & Zhang.** *IDECAMB: an implementation of interacting dark energy cosmology in CAMB.* arXiv:2306.01593. Chave: `LiZhang2023IDECAMB`.  
   Aplicação: rota interagente deve explicitar (Q), (delta Q) e transferência de momento; background (Q(a)) sozinho não fecha perturbações.

2. **Pan et al.** *Consistent Initial Conditions for Early Modified Gravity in Effective Field Theory.* arXiv:2506.17411. Chave: `Pan2025ConsistentICs`.  
   Aplicação: `C07` exige ICs super-horizonte compatíveis com as equações congeladas; copiar ICs de GR não é default válido.

3. **Lesgourgues.** *The Cosmic Linear Anisotropy Solving System (CLASS) III: Comparision with CAMB for LambdaCDM.* arXiv:1104.2934. Chave: `Lesgourgues2011CLASSCAMB`.  
   Aplicação: paridade exige implementações independentes, inputs físicos equivalentes e sweep de convergência. O ~0,01% histórico para ΛCDM é referência, não tolerância automática do RLL.

4. **Wang, Yu & Wu.** *Reassessing Evidence for Dark-Sector Interactions with Dynamical Dark Energy and DESI DR2.* arXiv:2609.03062. Chave: `Wang2026DarkSectorDESIDR2`.  
   Aplicação: (P(k)), (fsigma_8), RSD, lensing e clustering devem atuar como falsificadores de rotas com interação/crescimento.

## Regra de citação

Toda equação/adaptação externa deve registrar uma chave BibTeX e o papel da referência:
`DATA_AUTHORITY | IMPLEMENTATION_REFERENCE | COMPARATOR | FALSIFIER_GUIDE`.

A equação do paper não se torna equação RLL por citação. A implementação RLL deve ter derivação própria ou permanecer `TOKEN_VAZIO`.

## Política

Não substituir referências internas por cópias soltas sem registrar a origem. Se uma referência interna for promovida a trecho do manuscrito, registrar a transformação no `data_manifest.md`.
