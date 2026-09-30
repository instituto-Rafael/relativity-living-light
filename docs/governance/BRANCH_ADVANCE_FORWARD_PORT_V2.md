# Branch Advance Forward-Port V2

## Objetivo

Transformar `ahead/behind` em decisão auditável, sem merge cego de branches antigas e sem interpretar `behind` alto como perda automática de capacidade.

## Classes

- `ABSORBED_AHEAD_ZERO`: nenhum commit exclusivo contra o `main` atual; não promover código.
- `MERGED_HISTORY_FALSE_AHEAD`: GitHub compare mostra ahead, mas PR foi mesclada em `main`; não duplicar histórico/conteúdo.
- `STACKED_NOT_MAIN_FORWARD_PORTED`: trabalho válido foi mesclado numa branch intermediária, não no `main`; portar somente a superfície técnica comprovável.
- `MATURITY_STRANDED_*`: capacidade chegou a `rll/lab`/`rll/integration`, mas não a `rll/release/main`; forward-portar primitivas atuais e revalidar.
- `DOCS_ONLY_AHEAD`: usar como insumo de revisão, não como mudança operacional automática.

## Invariantes

```text
blind_merge=false
force_update=false
claim_allowed=false
publication_effect=NONE
stale_external_state_promoted=false
unclassified_refs=TOKEN_VAZIO
```

## Avanços forward-portados nesta revisão

1. UTM-185: máscara explícita de vazio em atenção hiperbólica, com testes e fronteira de prova.
2. Workflow contract sync V2: contagem derivada dos workflows executáveis, read-only/fail-closed no CI.
3. GitHub Platform Assurance V2: capacidades locais + Dependency Review/CodeQL com estado externo fresco.
4. Branch Maturity Gate V2: topologia `work → lab → integration → release → main`.
5. Registry V2: dezenas de refs com ahead/behind, classe, evidência e `F_next`.

## TOKEN_VAZIO preservados

- refs ainda não classificados individualmente entre o universo de branches;
- rulesets/required checks/protected environments/secret scanning até receipt atual;
- ativação automática da aresta `rll/release → main` até refresh coerente de `rll/release`;
- Termux/model-training de UTM-185.

## F_next

Executar CI desta PR. Depois, usar o ledger para ampliar a classificação em lotes e criar a aresta dedicada de atualização de `rll/release`, sem reintroduzir conteúdo stale.
