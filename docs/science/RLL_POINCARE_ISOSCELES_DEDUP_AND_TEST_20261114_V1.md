# RLL Ω — Deduplicação estrutural e testes matemáticos escopados — 2026-11-14

**Autor/proponente:** Rafael Melo Reis · **Produtor:** `instituto-Rafael/relativity-living-light` · **Estado:** `LOCAL_MATH_16_OF_16_PASS / SCIENTIFIC_HOLD / claim_allowed=false`.

## 1. Fonte, contrato e abrangência

- Base auditada: `main@e127d44c1dbe210b5fe021b64d2f877837ca45db`; a branch de auditoria não é a `main`.
- Árvore Git da base: **4.109 blobs**, **3.800 identidades Git de blob**, **211 grupos com SHA de blob repetido**, **309 ocorrências de caminhos acima das 3.800 identidades distintas**. Esses números caracterizam *identidade byte-a-byte de objetos Git*, não deduplicação semântica de equações.
- O levantamento anterior `docs/science/RLL_FORMULA_LITERATURE_EDGE_VECTOR_AUDIT_20260822_V1.md` registra 486 expressões extraídas de 53 fontes e 50 hipóteses adicionais; a soma 536 é limite bruto antes de dedup e não foi promovida a quantidade de fórmulas únicas.
- A auditoria anterior do `papers` particular classificou 18 grupos selecionados de Pitágoras–isósceles–Poincaré. Este repositório público **não incorpora conteúdo privado** desse outro repositório e este checkpoint **não** realiza o cruzamento integral das 486 expressões com o inventário MF-251.

## 2. Duplicações exatas selecionadas e decisão

| SHA de blob Git | Caminhos | Contrato |
|---|---|---|
| `95d643659f31bbb7d2107ebcf1c50562bee9cfb1` | `PapersPub/01_cosmology_pantheon_desi/references.bib` e `PapersPub/02_cosmology_growth_structure_d/references.bib` | **KEEP**; verificar se referências editoriais são intencionalmente compartilhadas |
| `a7eecf05cbdf19b8e649497d1c9f34206d95a266` | `data/rll_latentes/examples/invalid_missing_falsifier.yml` e `tests/fixtures/rll_latentes/invalid_missing_falsifier.yml` | **KEEP**; possíveis papéis de fixture |
| `8f8fde6dc004df1bec75755a74e14c380657e3a4` | `data/rll_latentes/examples/valid_minimal.yml` e `tests/fixtures/rll_latentes/valid_minimal.yml` | **KEEP**; contrato de teste pode exigir cópias |
| `54a0debb03816846bd7363f29b524f0ecac8ed63` | `scripts/pantheon/models_pantheon.py` e `validacao_real/data/models.py` | **KEEP** até auditar imports, execuções e licenças |

O quinto grupo relacionado contém vários arquivos vazios `.gitkeep` e `validation/__init__.py`, uma identidade esperada de arquivos vazios; não é prova de código redundante. Os demais 206 grupos de identidade não foram revisados individualmente. Não apagar, mover, mesclar ou reescrever códigos-fonte por similaridade de hashes.

## 3. Execução e evidência reproduzível

Código: `tests/test_rll_poincare_isosceles_dedup_v1.py`.

Comando local em Python padrão:

```sh
python tests/test_rll_poincare_isosceles_dedup_v1.py
```

**Resultado observado no runtime local desta auditoria:** `Ran 16 tests ... OK` (16/16 testes matemáticos sintéticos). SHA-256 local do script: `538b6678b36976d3324d3c1d8b596ec21bafc1f0797ec1d27d52e95bdd607cac`. SHA-1 de *objeto blob Git* local e confirmado por leitura do GitHub: `b2152ac95778ffeaa6ad8d5064972c47f64ccab7`. SHA-256 local do log: `0c038de3d96a0fbd7f8fe5325ce152a65a3ea2df8a15dc7a34c34251dd065766`.

Escopo dos testes: identidade pitagórica e lei dos cossenos; altitude isósceles e distinção ápice 10° / semiápice 10°; condição equilátera a semiápice 30°; duas alturas não equivalentes; `sqrt(3)/2 != sqrt(3/2)`; área via Gram; restrição de velocidade unitária para o discriminante; ida/volta hiperboloide–bola 7D; não confusão `T^7` versus `S^7`; e invariantes da continuidade do setor logístico RLL.

**P0 científico preservado** (fonte preexistente `docs/science/RLL_MATH_LITERATURE_COHERENCE_AUDIT_20260808.md`):

```text
R(a)=f(a)+(1-f(a))*a^-3
p_doc/(Omega_s0*rho_c0)=-f(a)
C(a)=f'(1-a^-3)       # não nula, em geral
p_cons=-R-R'/3        # fecha continuidade algebricamente
```

A validação confirma a **falha** da hipótese de conservação separada com `p_doc` durante uma transição não trivial, não a aprovação física do modelo. Identidades sintéticas matemáticas e execução local de Python **não** validam cosmologia, convergência G6, dados DESI, Pantheon+ STAT+SYS, hardware ARM ou teorema de Poincaré em 3 dimensões. O fluxo `.github/workflows/poincare-7d-evidence-gate.yml` permanece independente; este registro não afirma que ele foi executado para esta branch.

## 4. Gate, rollback, continuidade

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
G0 Git tree exact blobs=OBSERVED_SCOPED
G1 formulas selected and math tests=LOCAL_PASS_SCOPED
G2 full 486-formula occurrence-level semantic dedup=NOT_RUN
G3 GitHub CI exact-head=NOT_VERIFIED
G4 DESI/Pantheon+ matched-likelihood + G6 convergence=NOT_RUN
G5 physical model closure and external replication=BLOCKED
claim_allowed=false
```

**R3:** `F_ok` = inventário de blobs e 16 testes locais com blob exato verificado; `F_gap` = dedup semântico integral, ligação do modelo físico, CI e prova observacional; `F_next` = inventariar por ID e ocorrência todas as 486 expressões, confrontar em lote fonte/hypótese/exata equivalência, com hashes e controles negativos. Rollback: branch isolada, documentos anteriores intactos, correções em sucessores append-only; nenhum merge, remoção ou claim público.
