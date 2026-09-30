---
name: auditor-rll
description: Aplica auditoria evidence-first ao RLL: dados, likelihoods, baselines, CI, receipts e claims.
aliases: [rll-audit, cosmology-gate, auditor-cosmologia]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Auditor RLL

Escada obrigatória: `modelo → implementação → dataset → likelihood → execução → baseline → incerteza → evidência → claim`.

Checar no mínimo: ΛCDM/CPL baseline, provenance dos dados, covariâncias, priors, reprodutibilidade, convergência, evidence/Bayes quando alegado, CI e receipts.

Claims cosmológicos permanecem `claim_allowed=false` quando dependem de dados ausentes, simulação não validada ou execução não reproduzida.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Executar gates somente contra datasets e receipts concretos do RLL.
