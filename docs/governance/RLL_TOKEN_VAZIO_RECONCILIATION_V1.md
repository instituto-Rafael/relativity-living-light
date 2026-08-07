# RLL TOKEN_VAZIO Reconciliation V1

## Objetivo

Converter lacunas genéricas e incertezas em estados auditáveis sem fabricar conclusão.

O reconciliador distingue:

- `RESOLVED`: evidência materializada fecha positivamente a pergunta operacional;
- `RESOLVED_NEGATIVE`: a incerteza foi fechada por um resultado negativo/limite conhecido;
- `REDUCED`: um vazio amplo ficou obsoleto e foi substituído por lacunas menores e mais precisas;
- `OPEN_INTERNAL`: falta execução/código que pode ser realizado dentro do projeto;
- `OPEN_EXTERNAL`: falta dado, likelihood, aparelho ou autoridade externa;
- `OPEN_HUMAN`: falta replicação/revisão verdadeiramente independente;
- `OPEN_GOVERNANCE`: falta receipt de configuração/permissão;
- `OPEN_MIXED`: teoria + runtime/dado ainda precisam convergir;
- `OPEN_EVIDENCE_MISSING`: uma regra tentou fechar/reduzir um token, mas a evidência requerida faltou ou não satisfez as assertions.

`TOKEN_VAZIO` nunca é interpretado como zero, PASS ou ausência de problema.

## Mudanças de estado já sustentadas

### 1. Full likelihood moderno de supernovas

O token genérico:

```text
TOKEN_VAZIO_MODERN_SN_FULL_LIKELIHOOD
```

é reduzido porque a execução `SN_MODERN_EXECUTION_RECEIPT_20260807_RUN31215323284.json` já registra Pantheon+ com full covariance e DES-Dovekie com full precision.

Ele não vira `PASS_COSMOLOGY`. É substituído pelos gaps menores:

```text
TOKEN_VAZIO_SN_COMMON_NUISANCE_ABLATION
TOKEN_VAZIO_CPL_DOVEKIE_WA_BOUNDARY_SENSITIVITY
```

### 2. Identificabilidade RLL em SN-only

O antigo vazio:

```text
TOKEN_VAZIO_RLL_SN_ONLY_PARAMETER_IDENTIFIABILITY
```

passa para `RESOLVED_NEGATIVE` porque as duas likelihoods materializadas registram `BLOCKED_SN_ONLY` e a interpretação explícita declara que os parâmetros RLL não foram medidos por SN-only.

Isso é conhecimento útil: a próxima evidência deve vir de outros setores observacionais/perturbações, não de repetir indefinidamente a mesma pergunta SN-only.

### 3. Licença explícita do upstream DES-SN5YR

No commit upstream pinado `c9a4fcafc4cbd19bd750dee47fc76194a45c181f`, a auditoria verificou a ausência de `LICENSE`, `LICENSE.md`, `LICENCE` e `COPYING` no root e não encontrou grant explícito de redistribuição no README.

O token:

```text
TOKEN_VAZIO_EXPLICIT_REPOSITORY_LICENSE_NOT_FOUND
```

vira `RESOLVED_NEGATIVE`: a conclusão operacional é **não redistribuir por presunção**. Uma licença/permission obtida por outro canal pode gerar receipt sucessor e mudar essa política posteriormente.

## O que continua aberto

Os maiores P0 permanecem deliberadamente visíveis:

1. common-nuisance/calibration ablation Pantheon+ ↔ Dovekie;
2. profile/bound sensitivity do CPL `wa`;
3. nested sampling / Bayes real;
4. replicação independente;
5. reprodução oficial DESI DR2;
6. execução física Termux.

P1 cobre ACT DR6, DES Y6 3x2pt, CLASS/CAMB + contrato de perturbações RLL, H0 formal, configurações externas do GitHub e refresh de `rll/release`.

P2 preserva arqueologia das refs e validação empírica/Termux do UTM-185.

## Execução

```bash
python3 tools/rll_token_vazio_reconcile.py \
  --output artifacts/governance/RLL_TOKEN_VAZIO_RECONCILIATION_CURRENT.json
```

A execução retorna código `0` quando as regras estão coerentes, mesmo que existam gaps científicos/externos abertos. Ela retorna código `2` quando uma regra que deveria fechar ou reduzir um token não consegue provar sua própria evidência.

Isso separa duas ideias diferentes:

```text
reconciler saudável != ciência concluída
```

## Anti-regressão

- estado terminal/reduzido exige arquivo de evidência + assertions;
- assertion falha → `OPEN_EVIDENCE_MISSING`;
- resultado negativo não promove `claim_allowed`;
- generic token reduzido sai da fila canônica e seus sucessores entram;
- receipt físico não pode ser substituído por CI/container;
- external likelihood não pode ser substituída por citação de paper;
- `claim_allowed=false` e `publication_ready=false` permanecem invariantes.

## R3

- **F_ok:** vazios obsoletos e incertezas já decididas deixam de poluir o backlog como se fossem desconhecidas.
- **F_gap:** evidências realmente ausentes permanecem tipadas, priorizadas e com autoridade/next action explícitos.
- **F_next:** executar P0 interno em paralelo com aquisição/materialização dos P0 externos; anexar receipts sucessores e rerodar o reconciliador.
