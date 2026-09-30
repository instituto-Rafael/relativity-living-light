---
name: verificador-grafos
description: Testa coerência relacional e propriedades esperadas de grafos.
aliases: [checar-grafos, validador-conexoes, coerencia-relacional]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Verificador de Grafos

Valide identidade de nós, arestas, caminhos, hubs, comunidades, fluxo e — quando matematicamente definido — espectro Laplaciano.

Métricas opcionais: conectividade, modularidade, centralidade, componentes, densidade e distância. Não afirmar estabilidade sem comparação temporal ou baseline.

Ao detectar anomalia, retorne causa candidata + evidência + alternativa + teste discriminante.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Adicionar baselines temporais e falsificadores por propriedade.
