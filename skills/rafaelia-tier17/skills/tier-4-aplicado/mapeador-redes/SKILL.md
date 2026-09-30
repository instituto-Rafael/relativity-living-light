---
name: mapeador-redes
description: Mapeia nós, arestas, comunidades, rotas, lacunas e proveniência em redes complexas.
aliases: [network-mapper, mapa-grafos, topologia-redes]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Mapeador de Redes

Gerar: inventário de nós, tipos de aresta, direção, peso, proveniência, comunidades, hubs, pontes, componentes, rotas e lacunas.

Cada aresta deve distinguir `OBSERVED`, `DERIVED`, `INFERRED`, `HYPOTHETICAL`. O mapa não transforma inferência em evidência.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Emitir grafo versionado com provenance por aresta.
