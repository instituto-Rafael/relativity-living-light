---
name: skill-creator-maestria
description: Cria novas skills governadas a partir de lacunas recorrentes, com schema, exemplos, testes e receipts.
aliases: [skill-factory, meta-skill, criador-governado]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Skill Creator Maestria

Crie uma skill somente quando uma lacuna recorrente justificar uma unidade reutilizável. Gere `SKILL.md`, `schema.json`, `exemplos.md`, `teste.md`, relações e proveniência.

Gate de promoção: clareza de escopo, entradas/saídas, invariantes, pelo menos um teste positivo e um negativo, e nenhuma claim sem evidência.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Criar score de promoção baseado em testes executados.
