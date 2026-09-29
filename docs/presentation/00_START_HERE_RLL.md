# START HERE Ω V2.1 DISPATCH — RLL

**Version:** `Ω V2.1`  
**State:** `ACTIVE_BOOTSTRAP_ROUTER`  
**Claim gate:** `claim_allowed=false`

> Este arquivo é **roteador**, não depósito. O START HERE global/Drive continua sendo a autoridade de memória e despacho federado; este arquivo materializa a rota do produtor RLL dentro deste repositório.

## Dispatch

```text
INTENT
  → CURRENT_STATE
  → μREAD (≤3 raízes, depth=1)
  → ROUTE / SOURCE_MIN
  → AUTHORITY
  → ACT
  → EVIDENCE
  → μWRITE
  → R3
  → STOP
```

## 1. CURRENT_STATE — leia primeiro

- [`05_CURRENT_STATE_RLL.md`](05_CURRENT_STATE_RLL.md) — estado compacto; máximo de três nós ativos.

Não comece pelo inventário completo. Não reconstrua estado varrendo o repositório inteiro.

## 2. μREAD — escolha no máximo três raízes

| Intenção | SOURCE_MIN | Autoridade nesta rota |
|---|---|---|
| Entender/navegar | [`../navigation/README.md`](../navigation/README.md) | documentação RLL |
| Auditar claim/evidência | [`../RLL_TRACEABILITY_MAP.md`](../RLL_TRACEABILITY_MAP.md) + [`../../receipts/`](../../receipts/) | source/receipt |
| Executar/validar | [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md) + [`../../tests/`](../../tests/) | producer repo + CI |
| Privacidade/LGPD | [`../governance/LGPD_PRIVACY_NAVIGATION_V1.md`](../governance/LGPD_PRIVACY_NAVIGATION_V1.md) | governança técnica; não parecer jurídico |
| Arquivos soltos/legacy | [`../navigation/ROOT_FILES_INDEX.md`](../navigation/ROOT_FILES_INDEX.md) | índice + manifesto de migração |

## 3. ROUTE / SOURCE_MIN

Use a menor fonte suficiente. Uma tarefa não ganha autoridade por abrir mais arquivos.

```text
SOURCE_MIN ≤ 3
missing SOURCE      → BLOCK
missing AUTHORITY   → BLOCK
missing EVIDENCE    → TOKEN_VAZIO / PENDING
```

## 4. AUTHORITY

```text
Drive / START HERE global → memória, índices federados, receipts privados
RLL GitHub producer       → implementação, schemas, testes, CI e artefatos públicos
docs/INDICE_MESTRE        → navegação documental canônica do RLL
docs/RLL_TRACEABILITY_MAP → claims/evidência/gaps
```

## 5. ACT → EVIDENCE

Executar não é provar claim:

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`

Todo ACT material deve apontar para teste, run, receipt ou TOKEN_VAZIO explícito.

## 6. μWRITE

Após delta material:

- atualizar apenas o índice/estado pertinente;
- gravar receipt quando houver execução/evidência;
- preservar histórico em vez de reescrever silenciosamente;
- não transformar START HERE em log.

## 7. R3

Finalizar trabalhos materiais com:

```text
F_ok   = o que foi materializado/provado
F_gap  = o que continua faltando
F_next = próximo delta de maior valor
```

## 8. Histórico / rollback

`START HERE — A-A auditar — RAFAELIA` e predecessores são **precedente/rollback**, não bootstrap ativo.

## Rotas de apresentação secundárias

- [`10_EVIDENCE_RESULTS.md`](10_EVIDENCE_RESULTS.md)
- [`20_PAPERS_REPRODUCIBILITY.md`](20_PAPERS_REPRODUCIBILITY.md)
- [`index.html`](index.html)

Essas páginas ajudam apresentação; não substituem CURRENT_STATE, autoridade, source ou receipt.
