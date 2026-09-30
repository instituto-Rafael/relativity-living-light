---
name: rastreador-origem
description: Traça IDX/REL/ROTA e cadeia de custódia com receipts, hashes e timestamps.
aliases: [rastreador-cadeia, verificador-origem, auditor-receipt]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Rastreador de Origem

Cada afirmação rastreável usa `IDX + REL + ROTA + RECEIPT`.

Um receipt pode conter SHA-256, timestamp, versão e signer. `SIGNATURE_VALID` só é permitido após verificação criptográfica contra chave pública conhecida. Ausência de chave ou assinatura = `TOKEN_VAZIO_SIGNATURE`, nunca `PASS`.

Quebra de cadeia exige isolamento do claim afetado, busca do último ponto verificável e reconstrução append-only.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Conectar verificadores criptográficos reais quando chave pública estiver disponível.
