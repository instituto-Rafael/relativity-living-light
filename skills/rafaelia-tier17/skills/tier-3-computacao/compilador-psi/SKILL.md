---
name: compilador-psi
description: Compila intenção ψ em plano explícito: entradas, transformações, gates, evidências e próximo passo.
aliases: [psi-compiler, compilador-intencao, planificador-gated]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Compilador Ψ

### IR de intenção
`ψ_raw → ψ_normalized → inputs → transforms → gates → evidence → output → receipt`.

### Estados
`DECLARED`, `MATERIALIZED`, `EXECUTED`, `VERIFIED`, `TOKEN_VAZIO`.

### Invariante
`descrição != execução != evidência != claim`.

O compilador deve falhar fechado quando um requisito obrigatório não tem fonte, caminho ou verificador.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Implementar um IR serializável com validador fail-closed.
