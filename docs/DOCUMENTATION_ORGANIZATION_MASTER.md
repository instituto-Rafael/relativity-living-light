# Organização Integral de Documentação e Artefatos
## Relativity Living Light — estrutura técnica, canônica e auditável

**Versão:** 1.3 (hub de navegação + privacidade/LGPD)
**Data:** 2026-09-29

---

## Escopo deste arquivo

Este documento define a **organização mestre** da documentação e a governança entre índices.

- Consolida regras de canonicidade e estrutura documental.
- Define matriz oficial `índice -> finalidade -> público`.
- Não substitui o conteúdo de cada índice especializado.

---

## Matriz oficial de índices

| Índice | Finalidade | Público principal |
|---|---|---|
| [`README.md`](../README.md) | Porta de entrada: visão geral, contexto e encaminhamento inicial. | Novos leitores, colaboradores e revisores externos. |
| [`docs/navigation/README.md`](navigation/README.md) | Hub por intenção/tarefa; reduz profundidade e evita depender da árvore física. | Todos os usuários, inclusive navegação rápida em mobile. |
| [`docs/navigation/ROOT_FILES_INDEX.md`](navigation/ROOT_FILES_INDEX.md) | Índice completo dos arquivos soltos da raiz com papel e decisão de migração. | Curadoria, manutenção e usuários que encontram arquivos fora das pastas canônicas. |
| [`docs/governance/LGPD_PRIVACY_NAVIGATION_V1.md`](governance/LGPD_PRIVACY_NAVIGATION_V1.md) | Mapa técnico LGPD/privacidade e fronteiras de compliance. | Mantenedores, segurança, privacidade e revisão jurídica. |
| [`docs/INDICE_MESTRE.md`](INDICE_MESTRE.md) | Navegação canônica por trilhas e caminhos oficiais. | Mantenedores, autores de documentação e usuários recorrentes. |
| [`docs/DOCUMENTATION_FULL_INVENTORY.md`](DOCUMENTATION_FULL_INVENTORY.md) | Inventário bruto completo (`.md`/`.zip`) com metadados de varredura. | Auditoria documental, curadoria e manutenção técnica. |

---

## 1) Objetivo formal

Este documento estabelece um **mapa único de organização** para:
- documentos técnicos centrais;
- documentos autorais/conceituais;
- documentos soltos na raiz;
- artefatos compactados (`.zip`);
- controle explícito de duplicatas por basename.

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

## 5) Inventário técnico de artefatos compactados (.zip)

1. `data/RelativityLivingLight_v4_bundle.zip`
2. `data/relativity_bundle_results.zip`
3. `docs/rll_revisado_v2.zip`

Recomendação contínua: manter checksum e data de geração para cadeia de custódia documental.

---

## 6) Padrão de atualização contínua

1. Ao criar/editar documentação duplicada, aplicar regra de aviso de canonicidade no não canônico.
2. Ao mudar documento oficial, atualizar `docs/INDICE_MESTRE.md` (seção oficial) e opcionalmente seção **Arquivo/Legacy**.
3. Ao adicionar novo documento da série canônica, atualizar `docs/CANONICAL_SOURCES.md`.
4. Ao incluir novo `.zip`, atualizar este inventário e `docs/ZIP_CONTENT_INDEX.md`.

### Procedimento operacional do inventário completo (`.md`/`.zip`)

1. Regenerar o inventário publicado com o script autoral:

   ```bash
   python3 tools/docs_inventory.py
   ```

2. Validar consistência entre contagem publicada e contagem real:

   ```bash
   python3 tools/docs_inventory.py --check
   ```

3. Confirmar no cabeçalho de `docs/DOCUMENTATION_FULL_INVENTORY.md`:
   - origem canônica `tools/docs_inventory.py`;
   - fronteira medida por `git ls-files`;
   - total de arquivos catalogados.

4. Em caso de conflito nos seis artefatos gerados (`docs/DOCUMENTATION_FULL_INVENTORY.md`, `docs/REAL_NUMBERS_REPORT.md`, `docs/YML_WORKFLOWS_INDEX.md`, `data/results/repo_inventory.json`, `data/results/repo_inventory.tsv`, `data/results/repo_inventory_summary.json`), resolver aceitando a árvore de código/documentação desejada e regenerar o inventário uma única vez com `python3 tools/docs_inventory.py`. Não editar os artefatos gerados manualmente.

5. Em caso de divergência, publicar novamente o inventário antes de merge/release.

---

## 7) Artefatos de varredura integral

- Inventário amplo: [`docs/DOCUMENTATION_FULL_INVENTORY.md`](DOCUMENTATION_FULL_INVENTORY.md)
- Índice de zip: [`docs/ZIP_CONTENT_INDEX.md`](ZIP_CONTENT_INDEX.md)
- Fontes canônicas: [`docs/CANONICAL_SOURCES.md`](CANONICAL_SOURCES.md)

---

## 8) Decisão canônica única de execução científica

A execução científica operacional deste repositório passa a usar **exclusivamente** a árvore:

- `docs/` → definição conceitual, equações, critérios e governança;
- `data/` → dados de entrada e módulos/scripts de execução;
- `results/` → saídas geradas, tabelas e relatórios de comparação.

Regra operacional: todo fluxo executável novo deve seguir `data/` → `results/`, com documentação em `docs/`.

## 9) Mapeamento de equivalências do ZIP `to_Add/RAFAELIA_COSMO_STRUCTURE_D.zip`

Extração realizada em pasta temporária para inspeção estática e migração seletiva.

| Arquivo no ZIP | Equivalência no repositório | Decisão |
|---|---|---|
| `core/equations.md` | `docs/Relativity_Living_Light.md`, `book/04_formalismo_equacao_unificada.md` | **Migrado** para `docs/modules/structure_d_equations.md` |
| `core/agn_feedback_bridge.md` | `docs/PLANO_ABCD_JWST_AGN_SMBH.md`, `book/22_validacao_jwst_agn_smbh.md` | **Migrado** para `docs/modules/structure_d_agn_feedback_bridge.md` |
| `code/cosmo.py` + `models.py` | `docs/rll_two_radiation_model.py` (sobreposição parcial) | **Migrado** para `data/pipelines/structure_d/` |
| `code/growth.py` | `docs/crescimento_estrutural.py` (sobreposição parcial) | **Migrado** para `data/pipelines/structure_d/` |
| `code/likelihood.py` | `docs/panteon_likelihood.py` (escopo mais amplo) | **Migrado** para `data/pipelines/structure_d/` |
| `code/run_all.py` | Sem equivalente direto modular no fluxo atual | **Migrado** para `data/pipelines/structure_d/run_all.py` |
| `code/make_example_data.py` | Sem equivalente direto para geração toy local | **Migrado** para `data/pipelines/structure_d/make_example_data.py` |
| `data/README.md` | documentação de inputs | **Migrado** para `data/inputs/structure_d/README.md` |
| `results/README.md` | documentação de outputs | **Migrado** para `results/structure_d/README.md` |
| `README.md`, `requirements.txt`, `paper/draft.md` (ZIP) | já cobertos por `README.md`, `requirements.txt`, acervo documental do repo | **Não migrado** (redundante) |

## 10) Status de `to_Add/`

`to_Add/` fica definido como **histórico de ingestão**. Não é diretório operacional do pipeline científico.
Todo conteúdo com papel ativo deve ser promovido explicitamente para `docs/`, `data/` ou `results/`.
