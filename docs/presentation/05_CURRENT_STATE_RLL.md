# 05 — CURRENT STATE RLL · HOTSTATE V2.1

**State:** `ACTIVE_COMPACT_ROUTING_STATE`  
**Max active roots:** `3`  
**Claim gate:** `claim_allowed=false`

Este arquivo é estado operacional curto. Histórico, inventários extensos e narrativa longa ficam fora daqui.

## Active node 1 — Navigation / repository hygiene

- `docs/presentation/00_START_HERE_RLL.md` = dispatcher V2.1.
- `docs/navigation/README.md` = hub humano por objetivo.
- `docs/navigation/ROOT_FILES_INDEX.md` = apresentação dos arquivos soltos.
- Wave 2A = conteúdo de 6 itens legacy movido para `docs/legacy/root/`; raiz preserva stubs.

## Active node 2 — Evidence / scientific state

- Entrada de claim: `docs/RLL_TRACEABILITY_MAP.md`.
- Estado de validação: `VALIDATION_STATUS.md`.
- Evidência executada: `receipts/` + `results/`.
- `claim_allowed=false` continua a fronteira padrão.

## Active node 3 — Governance / privacy

- `docs/governance/LGPD_PRIVACY_NAVIGATION_V1.md`.
- `data/governance/RLL_LGPD_NAVIGATION_PRIVACY_V1.json`.
- `PRIVACY_BY_DESIGN != LEGAL_COMPLIANCE_CERTIFICATION`.

## Current R3

**F_ok:** Navigation Hub + LGPD gate merged; Wave 2A legacy destinations/stubs materialized; V2.1 dispatcher being bound to the repository.

**F_gap:** backlink graph is not yet complete; stub removal safety is not proven; human mobile/accessibility smoke remains TOKEN_VAZIO.

**F_next:** validate blob preservation + backlinks + V2.1 routing; then Wave 2B for `INDEX_FIRST` documents with explicit canonical destinations.
