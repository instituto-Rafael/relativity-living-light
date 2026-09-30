---
name: escriba-hebreu
description: Triple-shadow semantics — três camadas de significado em cada palavra.
aliases: [triple-shadow, tres-sombras, semantica-profunda]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Escriba Hebreu

### Três Sombras
- **S1 Manifesto:** texto/definição observável; confiança pode ser alta quando citável.
- **S2 Intencional:** contexto/autoria; requer proveniência e pode envolver inferência.
- **S3 Latente:** possibilidades futuras; sempre hipótese até materialização.

### Luminosidade
Uma combinação ponderada só é válida se os pesos forem declarados. Padrão pedagógico: `L=0.5*S1+0.3*S2+0.2*S3`; status `HEURISTIC`, não lei universal.

### Gate
S3 nunca pode retroativamente ser registrada como fato de S1.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Calibrar pesos somente com corpus/feedback versionado.
