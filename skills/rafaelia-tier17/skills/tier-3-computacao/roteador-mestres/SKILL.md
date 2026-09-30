---
name: roteador-mestres
description: Seleciona e combina skills conforme intenção, contexto, risco e necessidade de prova.
aliases: [seletor-mestres, roteador-automatico, maestro-modo]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Roteador de Mestres

Classifique a intenção: explicar, conectar, interpretar, transformar, auditar, verificar relações ou rastrear origem. Ative uma ou mais skills e registre `route_reason`.

Roteamento por keywords é apenas baseline heurístico. Feedback altera pesos somente se houver armazenamento explícito do delta; não alegar aprendizagem persistente sem artefato de estado.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Registrar matriz de confusão de roteamento em dataset rotulado.
