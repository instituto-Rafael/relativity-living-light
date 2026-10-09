# Navigation Hub — Human Comfort Layer

**Bootstrap operacional:** [`START HERE Ω V2.1 DISPATCH`](../presentation/00_START_HERE_RLL.md)

**Objetivo:** chegar ao conteúdo certo em poucos cliques, sem precisar conhecer a árvore inteira do repositório.

> Regra de conforto: escolha primeiro **o que você quer fazer**. Só depois entre em diretórios, registries ou inventários extensos.

## Quero entender o projeto

1. [README principal](../../README.md) — visão geral.
2. [Arquitetura](../../ARCHITECTURE.md) — como as partes se relacionam.
3. [Índice Mestre](../INDICE_MESTRE.md) — documentação canônica por trilhas.
4. [Mapa de rastreabilidade](../RLL_TRACEABILITY_MAP.md) — claims, fontes, evidências e gaps.

## Quero reproduzir resultados

- [Validação e status](../../VALIDATION_STATUS.md)
- [Matriz de reprodutibilidade](../../REPRODUCIBILITY_MATRIX.md)
- [Receipts](../../receipts/)
- [Results](../../results/)
- [Scripts](../../scripts/)
- [Tests](../../tests/)

## Quero auditar coesão operacional

- [Fechamento de coesão operacional RLL](../governance/RLL_OPERATIONAL_COHESION_CLOSURE_20261008.md)
- [Excelência operacional](../governance/OPERATIONAL_EXCELLENCE_EXECUTION_FRAMEWORK.md)
- [Carta de integridade operacional](../governance/OPERATIONAL_EXCELLENCE_INTEGRITY_CHARTER.md)
- [Modelo operacional de GitHub Actions](../governance/GITHUB_ACTIONS_OPERATING_MODEL.md)
- [Receipt do fechamento](../../receipts/2026-10-08_RLL_OPERATIONAL_COHESION_CLOSURE_V1.json)
- [Correção de proveniência e observação CI — PR #1076](../../receipts/2026-10-08_RLL_PR1076_PROVENANCE_CI_OBSERVATION_V2.json)

## Quero auditar segurança, privacidade ou LGPD

- [Mapa LGPD / privacidade V1](../governance/LGPD_PRIVACY_NAVIGATION_V1.md)
- [Governança de segurança e privacidade](../governance/RLL_DEVELOPMENT_SECURITY_GOVERNANCE_V1.md)
- [Resposta a incidentes](../governance/RLL_INCIDENT_RESPONSE_V1.md)
- [Registro de riscos de segurança/privacidade](../../data/governance/RLL_SECURITY_PRIVACY_RISK_REGISTER_V1.json)
- [Registro de finalidade de uso de dados](../../data/governance/RLL_DATA_USE_PURPOSE_REGISTRY_V1.json)
- [Security policy](../../.github/SECURITY.md)

## Quero achar um arquivo solto da raiz

- [Índice de todos os arquivos soltos da raiz](ROOT_FILES_INDEX.md)

Esse índice classifica cada arquivo sem movê-lo: entrada, governança, documento, código, registry, legacy ou artefato.

## Quero contribuir sem quebrar canonicidade

1. Consulte [DOCUMENTATION_ORGANIZATION_MASTER](../DOCUMENTATION_ORGANIZATION_MASTER.md).
2. Consulte [CANONICAL_SOURCES](../CANONICAL_SOURCES.md).
3. Se o arquivo for novo, escolha `docs/`, `data/`, `results/`, `scripts/`, `tools/`, `tests/` ou `receipts/` em vez da raiz.
4. Se substituir um documento antigo, marque sucessor/legacy antes de mover.

## Quero conteúdo científico

- [Núcleo canônico](../canonicos/)
- [Science](../science/)
- [Dados reais](../../data/real/)
- [Papers/publicação](../../PapersPub/)
- [Book](../../book/)

## Quero legado, ingestão ou material ainda não promovido

- [`newadd/`](../../newadd/)
- [`to_Add/`](../../to_Add/)
- [`news/`](../../news/)
- itens `LEGACY_REVIEW` no [índice da raiz](ROOT_FILES_INDEX.md)

> Estar no repositório não torna um arquivo canônico. Use o estado de governança e os backlinks.

## Mapa mental curto

```text
README
  ↓
START HERE Ω V2.1 DISPATCH
  ↓
CURRENT_STATE / μREAD≤3
  ↓
NAVIGATION_HUB  ← você está aqui
  ├─ ciência ─────────→ docs/science + docs/canonicos + data/real
  ├─ execução ────────→ scripts + tools + tests
  ├─ evidência ───────→ results + receipts + provenance
  ├─ governança ──────→ docs/governance + data/governance
  ├─ privacidade/LGPD → LGPD_PRIVACY_NAVIGATION_V1
  └─ arquivos soltos ─→ ROOT_FILES_INDEX
```

## Usabilidade e acessibilidade

- títulos curtos e previsíveis;
- uma finalidade por link;
- caminho canônico antes do inventário bruto;
- legacy separado de material ativo;
- sem depender de cor para comunicar estado;
- arquivos grandes de inventário ficam como auditoria, não como primeira tela.

## Estados que este hub não fecha

- `TOKEN_VAZIO_HUMAN_USABILITY`: falta smoke test humano em Android/desktop.
- `TOKEN_VAZIO_SCREEN_READER_KEYBOARD_AUDIT`: acessibilidade física ainda não foi observada.
- `TOKEN_VAZIO_LEGAL_COMPLIANCE_REVIEW`: engenharia LGPD não equivale a parecer jurídico.
