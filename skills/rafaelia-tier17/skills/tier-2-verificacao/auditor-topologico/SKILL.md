---
name: auditor-topologico
description: Valida integridade estrutural: sombras, fluxo, coerência, rastreabilidade e feedback.
aliases: [auditor-estrutura, validador-coerencia, checker-topologia]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Auditor Topológico

Valide cinco famílias: três sombras, fluxo, coerência multidimensional, rastreabilidade e feedback. Cada check é `PASS|FAIL|TOKEN_VAZIO|NOT_APPLICABLE`.

`saude = checks_PASS / checks_APLICAVEIS`.

Faixas padrão são configuráveis; não tratar thresholds heurísticos como propriedade matemática intrínseca. Contradição esperada vira `BIFURCACAO`; contradição não modelada vira `ERROR_OR_GAP`.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Versionar thresholds e pesos por domínio.
