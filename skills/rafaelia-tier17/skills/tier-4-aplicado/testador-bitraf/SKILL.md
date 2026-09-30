---
name: testador-bitraf
description: Testa propriedades formais e implementadas de BITRAF sem promover hipótese a prova.
aliases: [bitraf-test, gf2-audit, bitraf-gates]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Testador BITRAF

Separe objeto formal, codificação, implementação e segurança. Testes possíveis: determinismo, avalanche, colisões empíricas, uniformidade, rank/kernel em GF(2) quando aplicável, invertibilidade, ciclos, distância e testes de adulteração.

Passar em hash/HMAC não prova automaticamente ECC, caos, invertibilidade ou segurança de construção. Cada propriedade possui gate próprio.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Congelar vetores de teste e separar propriedades provadas das empíricas.
