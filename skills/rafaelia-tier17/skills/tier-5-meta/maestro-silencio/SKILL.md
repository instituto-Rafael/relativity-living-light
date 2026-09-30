---
name: maestro-silencio
description: Decide quando não inferir: TOKEN_VAZIO, coleta mínima, espera por evidência e resposta de baixa entropia.
aliases: [silence-gate, token-vazio, abstencao-coerente]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Maestro do Silêncio

Silêncio operacional = recusar inferência desnecessária. Use quando a resposta exigiria inventar fato, completar cadeia ausente ou converter possibilidade em certeza.

Saída mínima: o que é conhecido, o que é `TOKEN_VAZIO`, por que importa e qual próximo ato verificável reduz a lacuna.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Medir redução de erro por abstenção versus resposta forçada.
