# Histórico de rastreabilidade — consolidação de `to_Add/`

Data da consolidação: 2026-02-25.

## Objetivo
Reduzir `to_Add/` para um papel estritamente de rastreabilidade, evitando duplicação de conteúdo operacional já canônico em `docs/` e `book/`.

## Decisões de merge editorial

- Conteúdo de paper/draft (`PAPER_A_DRAFT.md`) consolidado por precedência em capítulos do livro e na trilha técnica principal.
- Conteúdo de modelo fechado e limites físicos (`MODEL_B_CLOSED.md`, `PHYSICS_LIMITS_C.md`) consolidado nos documentos formais já existentes.
- Conteúdo de auditoria/estrutura/lacunas (`AUDIT_REPORT.md`, `STRUCTURE_D.md`, `TODO_GAPS.md`) considerado redundante frente aos documentos oficiais de gap e roadmap.

## Artefatos removidos do diretório operacional

- `AUDIT_REPORT.md`
- `MODEL_B_CLOSED.md`
- `PAPER_A_DRAFT.md`
- `PHYSICS_LIMITS_C.md`
- `STRUCTURE_D.md`
- `TODO_GAPS.md`
- `LINK_GRAPH.json`
- `TOP_MD_BY_SIZE.csv`
- `RAFAELIA_COSMO_STRUCTURE_D.zip`

## Estado final esperado de `to_Add/`

- `FILE_MANIFEST.csv` (manifest técnico preservado)
- `HISTORICO_RASTREABILIDADE.md` (este histórico)
