# Escopo do hotfix — run 31064223594

Este branch preserva o resultado histórico do workflow como `PASS` e adiciona somente uma auditoria secundária append-only.

Não altera:

- resultados científicos;
- arquivos de dados;
- claims físicos;
- workflows existentes;
- código do builder;
- branch `main` diretamente.

O objetivo é registrar três lacunas adicionais antes de uma futura correção executável:

1. evidência registrada porém ausente;
2. cobertura interna incompleta de checksums;
3. claim Tier 1 sem vínculo de runtime dentro da cápsula.

```text
claim_allowed=false
automatic_merge=false
historical_receipt_rewritten=false
```
