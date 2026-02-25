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

## Registro de integridade (SHA-256 da revisão anterior)

Os hashes abaixo foram calculados a partir do conteúdo da revisão imediatamente anterior (`HEAD~1`) para manter cadeia de custódia mínima dos itens removidos.

| arquivo removido | sha256 |
|---|---|
| `AUDIT_REPORT.md` | `3513f5d48b4099cd0ccfb6e8e94ded8b56fc9d6042b5b5b521d4ab66ff507ace` |
| `MODEL_B_CLOSED.md` | `eee9976b0b8bef3b6c3a075cb14d202e11bd671e8a14cf379230b0b2f71bb782` |
| `PAPER_A_DRAFT.md` | `44abf8d93ef9580d30ac3589cbd835ee0542d1b50ca64be9aac0c6430b8b77d1` |
| `PHYSICS_LIMITS_C.md` | `6e57af304a845310c380f434fc73de9b0568694e19dad6476059a4aadca8e172` |
| `STRUCTURE_D.md` | `02e81cdf40fe177b2591b7968849828a0262a2f9f5cf2932194735bcfc5d3fce` |
| `TODO_GAPS.md` | `f01cef2d4412cb012c419da13ef1b80b8956342f4362278384d8fecc8a7b8cf7` |
| `LINK_GRAPH.json` | `17dcb77be539431a421db7af4a7952ecc364da2d7b1fc186c2a6bd4a5b0c763c` |
| `TOP_MD_BY_SIZE.csv` | `66a99a95f248618e86c645bb1066aa1db941dd1b35c7328061c20ea20cbc55ca` |
| `RAFAELIA_COSMO_STRUCTURE_D.zip` | `db3fa53131ab7922b47d5645e9bedb23f4110317fd5724ef97c84df55b744b92` |

## Estado final esperado de `to_Add/`

- `FILE_MANIFEST.csv` (manifest técnico preservado)
- `HISTORICO_RASTREABILIDADE.md` (este histórico)
