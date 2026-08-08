# Auditoria do artefato RLL Scientific Navigation — run 31064223594

## Estado auditado

```text
artifact_integrity=PASS
workflow_execution=PASS
scientific_validation=NOT_CLAIMED
claim_allowed=false
artifact_sha256=419ec4beca36ec978c2bd514090ed85aa26533af5a95f835e741a6557b845105
commit_sha=cbe0d6b32c43639b8dc281355ff368a3ba607d66
head_sha=0e69fc00c2209f0bb3cb9692d4d1f1e9ad2d03cd
run_id=31064223594
```

## F_ok

- O ZIP abre sem erro e possui 15 arquivos.
- O SHA-256 local coincide com o digest registrado pelo upload do GitHub Actions.
- O workflow terminou com sucesso; todas as etapas operacionais concluíram `success`.
- A suíte do builder concluiu `4 passed`.
- As quatro cápsulas validam contra os schemas.
- Os seis registros `TOKEN_VAZIO` têm `claim_weight=0`.
- `claim_allowed=false` está preservado no manifesto, receipts e cápsulas.
- O boundary é correto: navegação/proveniência não equivalem a validação física.

## F_gap encontrados após a auditoria do próprio artefato

### GAP-1 — Evidência registrada, ausente e não tipada

O registry declara dois `evidence_paths` para `real-data-complete`:

1. `results/structure_d/model_comparison_real.csv`;
2. `results/structure_d/model_comparison_real_fit_metadata.json`.

A cápsula contém somente o primeiro. O segundo retorna 404 no commit auditado.

O builder cria `TOKEN_VAZIO` automático somente para `required_paths`; evidências ausentes são silenciosamente ignoradas. Por isso `missing_required_paths={}` não significa que todo o conjunto registrado foi localizado.

Estado correto:

```text
TV-RLL-REALDATA-FIT-METADATA=OPEN
claim_weight=0
```

### GAP-2 — `BUILD.log` fora da cadeia interna de checksums

O ZIP possui 15 arquivos. `CHECKSUMS.sha256` cobre 13 arquivos e exclui:

- o próprio `CHECKSUMS.sha256`, corretamente;
- `BUILD.log`, incorretamente para uma verificação interna autônoma.

O digest externo do ZIP protege o pacote completo, portanto não há corrupção observada. A lacuna é de fechamento interno.

### GAP-3 — Claim Tier 1 excede a evidência contida na cápsula

A claim permitida afirma:

```text
Tier 1 numerical diagnostics executed under their declared inputs
```

Mas a cápsula Tier 1 possui estado `METADATA_READY`, apenas três arquivos-fonte hashificados e informa que os artefatos de runtime exigem uma execução concreta.

Uma execução Tier 1 separada terminou com sucesso no mesmo conjunto de checks, mas o bundle não liga essa execução a um `run_id`, receipt ou hash de artifact. Portanto, dentro desta cápsula, a redação correta é:

```text
Tier 1 workflow, implementation and tests were located and hashed
```

ou deve ser anexado um receipt concreto da execução Tier 1.

### GAP-4 — Gate de contagem aceita ledger excedente

O workflow usa:

```python
if manifest.get("open_token_vazio_count") > token_count:
    fail()
```

A invariante forte deveria ser igualdade:

```python
if manifest.get("open_token_vazio_count") != token_count:
    fail()
```

No artefato atual ambos são 6, então o resultado presente continua PASS. O defeito é preventivo: registros extras no ledger poderiam passar sem aparecer no manifesto.

### GAP-5 — Grafo representa somente objetos localizados

O `DEPENDENCY_GRAPH.json` possui 4 mecanismos, 13 artefatos e 13 arestas. Não representa:

- `TOKEN_VAZIO` como nós;
- evidências registradas porém ausentes;
- artefatos de runtime esperados;
- arestas `blocks_claim` e `requires_evidence`.

Logo, ele é um grafo de presença, não ainda um grafo completo de dependência científica.

### GAP-6 — `F_gap` e `F_next` são semanticamente iguais

As duas seções repetem as mesmas ações. A régua mais útil é:

```text
F_gap  = condição ausente ou incompatibilidade observada
F_next = operação mínima que pode reduzir essa condição
```

## Invariante real do bundle

```text
NAVIGATION_PASS
iff
ZIP_DIGEST_MATCH
and WORKFLOW_SUCCESS
and SCHEMA_VALID
and CHECKSUMS_VALID_FOR_DECLARED_SET
and CLAIM_BOUNDARY_FALSE
and EVERY_REGISTERED_ABSENCE_IS_TYPED
and MANIFEST_LEDGER_COUNTS_EQUAL
```

No estado atual:

```text
ZIP_DIGEST_MATCH=true
WORKFLOW_SUCCESS=true
SCHEMA_VALID=true
CHECKSUMS_VALID_FOR_DECLARED_SET=true
CLAIM_BOUNDARY_FALSE=true
EVERY_REGISTERED_ABSENCE_IS_TYPED=false
MANIFEST_LEDGER_COUNTS_EQUAL=true
```

Portanto:

```text
workflow_result=PASS
bundle_maturity=VERIFIED_LIMITED_WITH_HOTFIX_GAPS
scientific_claim=BLOCKED
```

## F_next priorizado

1. Tipar `model_comparison_real_fit_metadata.json` como evidência ausente ou removê-lo formalmente do registry.
2. Gerar `WORKFLOW_RECEIPT.json` antes do checksum final e regenerar `CHECKSUMS.sha256` depois de `BUILD.log` existir.
3. Trocar a validação de contagem de `>` para `!=`.
4. Estreitar a claim Tier 1 ou ligar a cápsula ao run/artifact concreto.
5. Acrescentar nós `TOKEN_VAZIO`, `expected_runtime_artifact` e relações de bloqueio no grafo.
6. Separar descrição do gap da ação `F_next`.

## Fechamento

Este artefato é uma evidência real de que o mecanismo de navegação foi executado e empacotado de forma determinística. Ele não é evidência de confirmação física do RLL, superioridade cosmológica, revisão independente ou reprodução em Termux.
