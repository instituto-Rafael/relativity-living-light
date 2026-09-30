---
name: analisador-vectra
description: Audita integração Vectras/QEMU/Android separando fonte, build, boot, runtime e evidência física.
aliases: [vectra-audit, qemu-route, android-runtime-audit]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Analisador Vectra

Camadas: fonte → build → artefato → assinatura → instalação → boot → runtime → workload → evidência física.

QEMU/proot/emulação não equivale a execução física Android. APK existente não equivale a launch bem-sucedido. Use receipts separados por camada.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Ligar build/boot/runtime a receipts por ambiente.
