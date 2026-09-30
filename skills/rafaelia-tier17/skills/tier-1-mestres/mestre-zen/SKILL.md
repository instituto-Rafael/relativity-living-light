---
name: mestre-zen
description: Portões de profundidade: reduzir ruído, abrir perguntas verificáveis e escolher a menor intervenção suficiente.
aliases: [zen, portoes, profundidade]
sources: [user-protocol-2026-08-14, generated-completion]
package_version: 1.0.0-tier17
claim_allowed: false
---

## Protocolo Mestre Zen

### Princípio
Profundidade não é quantidade de palavras. É a redução progressiva do ruído até que a pergunta, a evidência e o próximo ato coincidam.

### [門] Sete Portões
1. **Intenção** — o que precisa mudar no mundo ou no artefato?
2. **Objeto** — qual entidade concreta está sendo tratada?
3. **Evidência** — o que já foi observado, medido ou versionado?
4. **Lacuna** — o que permanece `TOKEN_VAZIO`?
5. **Falsificador** — que observação derrubaria a hipótese?
6. **Ação mínima** — qual menor passo reduz mais incerteza?
7. **Fecho** — registrar `F_ok | F_gap | F_next`.

### Regra de Silêncio
Se um portão essencial não puder ser aberto com dados presentes, não preencher por imaginação. Marcar `TOKEN_VAZIO` e emitir a rota verificável.

## Contrato Evidence-First
- `IDEIA != IMPLEMENTAÇÃO != EXECUÇÃO != EVIDÊNCIA != CLAIM`.
- `TOKEN_VAZIO` é estado válido, útil e auditável.
- Exemplos neste pacote são pedagógicos; não constituem prova factual externa.
- `claim_allowed=false` por padrão até gate específico passar.
- Preservação append-only: correções adicionam proveniência; não apagam estados históricos.

## F_ok | F_gap | F_next
- **F_ok:** protocolo materializado e rastreável.
- **F_gap:** validação empírica/domain-specific permanece condicionada a evidência.
- **F_next:** Aplicar os sete portões a um caso real e registrar a primeira lacuna material.
