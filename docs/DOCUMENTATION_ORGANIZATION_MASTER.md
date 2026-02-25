# Organização Integral de Documentação e Artefatos
## Relativity Living Light — estrutura técnica, canônica e auditável

**Versão:** 1.2 (merge editorial de `to_Add/` com rastreabilidade)
**Data:** 2026-02-25

---

## 1) Objetivo formal

Este documento estabelece um **mapa único de organização** para:
- documentos técnicos centrais;
- documentos autorais/conceituais;
- documentos soltos na raiz;
- artefatos compactados (`.zip`);
- controle explícito de duplicatas por basename;
- destino editorial oficial do conteúdo originalmente reunido em `to_Add/`.

A finalidade é eliminar ambiguidade, elevar governança do acervo e sustentar manutenção de longo prazo em padrão técnico-profissional auditável.

---

## 2) Política de canonicidade (regra oficial)

### 2.1 Regra-base por basename
Quando existir mais de um arquivo com o mesmo basename (ex.: `10_FAQ_COMPLETO.md`) em pastas diferentes:

1. **Canônico oficial:** arquivo em `docs/canonicos/` (quando existir).
2. **Histórico/legado:** cópias na raiz, em `RMR/` e em `news/archive_legacy/`.
3. **Obrigação de aviso:** todo arquivo não canônico deve iniciar com aviso curto apontando para o arquivo canônico.
4. **Índices oficiais (`README`, `INDICE_MESTRE`)** devem listar apenas caminhos canônicos na seção principal.
5. **Links de preservação histórica** devem ficar em seção separada: **Arquivo/Legacy**.

### 2.2 Critério quando não existir `docs/canonicos/`
Na ausência de equivalente em `docs/canonicos/`, a canonicidade é definida por esta ordem:
1. arquivo referenciado em `docs/CANONICAL_SOURCES.md`;
2. arquivo em `docs/` (fora de arquivos de rascunho/snapshot);
3. arquivo fora de `docs/` é tratado como legado até promoção explícita.

---

## 3) Inventário de duplicatas relevantes por basename

| Basename | Canônico oficial | Históricos/legado mapeados |
|---|---|---|
| `00_COMO_LER.md` | `docs/canonicos/00_COMO_LER.md` | `00_COMO_LER.md`, `RMR/00_COMO_LER.md` |
| `06_COMPARACOES_DETALHADAS.md` | `docs/canonicos/06_COMPARACOES_DETALHADAS.md` | `06_COMPARACOES_DETALHADAS.md`, `RMR/06_COMPARACOES_DETALHADAS.md` |
| `09_GLOSSARIO_COMPLETO.md` | `docs/canonicos/09_GLOSSARIO_COMPLETO.md` | `09_GLOSSARIO_COMPLETO.md`, `RMR/09_GLOSSARIO_COMPLETO.md`, `news/archive_legacy/09_GLOSSARIO_COMPLETO.md`, `news/archive_legacy/1/09_GLOSSARIO_COMPLETO.md` |
| `09_GLOSSARIO_COMPLETO-1.md` | `docs/canonicos/09_GLOSSARIO_COMPLETO.md` | `09_GLOSSARIO_COMPLETO-1.md`, `RMR/09_GLOSSARIO_COMPLETO-1.md` |
| `10_FAQ_COMPLETO.md` | `docs/canonicos/10_FAQ_COMPLETO.md` | `10_FAQ_COMPLETO.md`, `RMR/10_FAQ_COMPLETO.md`, `news/archive_legacy/10_FAQ_COMPLETO.md`, `news/archive_legacy/1/10_FAQ_COMPLETO.md` |
| `11_DOCUMENTO_PRIORIDADE.md` | `docs/canonicos/11_DOCUMENTO_PRIORIDADE.md` | `11_DOCUMENTO_PRIORIDADE.md`, `RMR/11_DOCUMENTO_PRIORIDADE.md`, `news/archive_legacy/11_DOCUMENTO_PRIORIDADE.md`, `news/archive_legacy/1/11_DOCUMENTO_PRIORIDADE.md` |

> Escopo desta rodada: duplicatas documentais críticas para navegação e leitura oficial.

---

## 4) Arquitetura documental canônica

### 4.1 Trilhas oficiais

**A. Trilha científica (core)**
- `README.md`
- `docs/Relativity_Living_Light.md`
- `docs/BOOSTERS.md`
- `docs/Results.md`
- `docs/REFERENCES.md`
- `docs/ROADMAP_VALIDACAO.md`
- `docs/COMPARACAO_DESI_2025.md`
- `docs/PLANO_ABCD_JWST_AGN_SMBH.md`

**B. Trilha de governança e organização**
- `docs/ADMIN.md`
- `docs/DOCUMENTATION_ORGANIZATION_MASTER.md`
- `docs/RELEASE_NOTES_HISTORY.md`
- `docs/ANALISE_DIRETORIOS_E_MDS_SOLTOS.md`
- `docs/CANONICAL_SOURCES.md`

**C. Série canônica RMR consolidada**
- `docs/canonicos/00_COMO_LER.md`
- `docs/canonicos/06_COMPARACOES_DETALHADAS.md`
- `docs/canonicos/09_GLOSSARIO_COMPLETO.md`
- `docs/canonicos/10_FAQ_COMPLETO.md`
- `docs/canonicos/11_DOCUMENTO_PRIORIDADE.md`

---

## 5) Merge editorial de `to_Add/` (origem → destino final)

### 5.1 Critério de precedência aplicado

Para evitar duplicação operacional e colisão de narrativa, o merge de `to_Add/` segue a prioridade:

1. **Documentos canônicos já existentes** com escopo equivalente em `docs/` e `book/`.
2. **Análises formais de lacuna/roadmap já consolidadas** (`docs/POST_PHD_FORMAL_GAP_ANALYSIS.md`, `docs/ROADMAP_VALIDACAO.md`).
3. **Apenas metadados de rastreabilidade** permanecem em `to_Add/`.

Resultado: conteúdos de `to_Add/` que repetiam estrutura de paper, roadmap, lacunas e auditoria foram absorvidos por referência aos arquivos canônicos existentes e marcados como histórico.

### 5.2 Tabela de mapeamento (origem em `to_Add/` → destino final)

| Origem (`to_Add/`) | Tipo final | Destino final no repo | Decisão editorial |
|---|---|---|---|
| `PAPER_A_DRAFT.md` | Capítulo (`book/*.md`) | `book/01_fundamentos_visao_geral.md`, `book/11_metodologia_pipeline_validacao.md`, `book/23_resultados_estatisticos.md` | Estrutura de paper já coberta pelo livro e pela trilha técnica; origem arquivada para histórico. |
| `MODEL_B_CLOSED.md` | Seção técnica (`docs/*.md`) | `docs/Relativity_Living_Light.md`, `docs/LAGRANGIANO_EFT.md` | Definição cosmológica já incorporada no formalismo técnico; origem arquivada. |
| `PHYSICS_LIMITS_C.md` | Seção técnica (`docs/*.md`) | `docs/POST_PHD_FORMAL_GAP_ANALYSIS.md` | Limites físicos e agenda de prova já cobertos no gap formal; origem arquivada. |
| `STRUCTURE_D.md` | Seção técnica (`docs/*.md`) | `docs/DOCUMENTATION_ORGANIZATION_MASTER.md`, `docs/DATA_INTEGRITY_CHECKLIST.md` | Estrutura/CI/artefatos já descritos em governança; origem arquivada. |
| `AUDIT_REPORT.md` | Seção técnica (`docs/*.md`) | `docs/POST_PHD_FORMAL_GAP_ANALYSIS.md`, `docs/ROADMAP_VALIDACAO.md` | Diagnóstico e próximos passos já consolidados; origem arquivada. |
| `TODO_GAPS.md` | Seção técnica (`docs/*.md`) | `docs/ROADMAP_VALIDACAO.md`, `docs/ANALISE_DIRETORIOS_E_MDS_SOLTOS.md` | Lacunas operacionais e links quebrados já tratáveis pelos documentos oficiais; origem arquivada. |
| `FILE_MANIFEST.csv` | Metadado de rastreabilidade | `to_Add/FILE_MANIFEST.csv` | Preservado (manifest técnico). |
| `LINK_GRAPH.json` | Histórico arquivado | `to_Add/HISTORICO_RASTREABILIDADE.md` | Referência histórica consolidada em histórico textual; JSON bruto removido do diretório operacional. |
| `TOP_MD_BY_SIZE.csv` | Histórico arquivado | `to_Add/HISTORICO_RASTREABILIDADE.md` | Estatística de inventário preservada no histórico; CSV bruto removido. |
| `RAFAELIA_COSMO_STRUCTURE_D.zip` | Histórico arquivado | `to_Add/HISTORICO_RASTREABILIDADE.md` | Snapshot preservado apenas como registro histórico de merge; artefato removido para evitar duplicação operacional. |

### 5.3 Estado final de `to_Add/`

Após o merge editorial, `to_Add/` passa a conter apenas:
- `FILE_MANIFEST.csv` (manifest de rastreabilidade);
- `HISTORICO_RASTREABILIDADE.md` (histórico das decisões, artefatos descontinuados e hashes de integridade).

---

## 6) Inventário técnico de artefatos compactados (.zip)

1. `data/RelativityLivingLight_v4_bundle.zip`
2. `data/relativity_bundle_results.zip`
3. `docs/rll_revisado_v2.zip`

Recomendação contínua: manter checksum e data de geração para cadeia de custódia documental.

---

## 7) Padrão de atualização contínua

1. Ao criar/editar documentação duplicada, aplicar regra de aviso de canonicidade no não canônico.
2. Ao mudar documento oficial, atualizar `docs/INDICE_MESTRE.md` (seção oficial) e opcionalmente seção **Arquivo/Legacy**.
3. Ao adicionar novo documento da série canônica, atualizar `docs/CANONICAL_SOURCES.md`.
4. Ao incluir novo `.zip`, atualizar este inventário e `docs/ZIP_CONTENT_INDEX.md`.
5. Para novos materiais temporários, evitar acúmulo em `to_Add/`: promover direto ao canônico (`docs/`/`book/`) ou registrar somente no histórico.

---

## 8) Artefatos de varredura integral

- Inventário amplo: [`docs/DOCUMENTATION_FULL_INVENTORY.md`](DOCUMENTATION_FULL_INVENTORY.md)
- Índice de zip: [`docs/ZIP_CONTENT_INDEX.md`](ZIP_CONTENT_INDEX.md)
- Fontes canônicas: [`docs/CANONICAL_SOURCES.md`](CANONICAL_SOURCES.md)
