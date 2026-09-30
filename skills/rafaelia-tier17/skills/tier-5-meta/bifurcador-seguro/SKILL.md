---
name: bifurcador-seguro
description: Preserva hipóteses concorrentes em branches conceituais sem apagar alternativas ou colapsar incerteza.
aliases: [safe-fork, hipoteses-paralelas, branch-semantico]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Bifurcador Seguro

Quando H1 e H2 não podem ser distinguidas pelos dados atuais, preserve ambas. Registre pressupostos, evidências comuns, evidências exclusivas e teste discriminante.

Nunca resolver bifurcação por preferência estética. `TOKEN_VAZIO_DISCRIMINATOR` é estado válido.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Registrar teste discriminante executável para cada bifurcação.
