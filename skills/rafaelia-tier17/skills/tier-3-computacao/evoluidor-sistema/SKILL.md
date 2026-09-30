---
name: evoluidor-sistema
description: Evolui artefatos por deltas append-only, preservando invariantes, regressões e estados TOKEN_VAZIO.
aliases: [evolucao-controlada, delta-append-only, anti-regressao]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Evoluidor de Sistema

Produza somente deltas auditáveis. Antes de cada evolução: congelar invariantes, medir baseline, declarar hipótese de mudança, aplicar delta, executar testes, comparar e registrar regressões.

Nunca apagar resultado negativo para melhorar score. Estados antigos permanecem endereçáveis por commit/hash/receipt.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Adicionar diff semântico e regressão automática por invariantes.
