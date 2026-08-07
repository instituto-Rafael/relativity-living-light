# Run 31066012098 — Reconciliação de evidência V1

`claim_allowed=false` · append-only · sem reescrita do commit histórico

## Fato material

Os ZIPs `pantheon-fit-results` e `bayes-factor-results` foram novamente baixados por artifact ID e validados por:

1. digest SHA-256 externo do GitHub;
2. CRC do ZIP;
3. `CHECKSUMS.sha256` interno;
4. parsing dos JSONs e logs.

## Pantheon

O job da run falhou com:

```text
ModuleNotFoundError: No module named 'models'
```

Consequência:

```text
ΔAIC desta run = TOKEN_VAZIO_EXECUTION_FAILURE
classe = P
```

O bloco `reference` dentro do JSON histórico não foi promovido a resultado da run.

## Bayes/BIC

O log materializa:

```text
BIC_LCDM = 138.907755
BIC_RLL  = 150.244294
ΔBIC     = 11.336539
ln(B10)  = -ΔBIC/2 = -5.6682695
```

Classificação:

```text
BIC proxy = C
F-COS-04 = FAIL, porque -5.6682695 <= -5
real Bayes / nested sampling = P / TOKEN_VAZIO
```

## Correção de arquitetura

O successor receipt não altera `cfcd8b4915fef664486bc0d93ee2a2bb6d84ec65`. Ele acrescenta uma camada explícita que distingue:

- bytes preservados;
- execução falha;
- cálculo reconstruído;
- inferência Bayes real ausente.

## Escopo recusado neste repositório

Conversation 004, imagens 0001–0040, OpCore94, `export1gb.zip`, `omega_msgs.jsonl` e `zone53` pertencem à autoridade longitudinal/privada. Podem fornecer receipts sanitizados ao RLL, mas não devem trazer o corpus bruto para este repositório público.
