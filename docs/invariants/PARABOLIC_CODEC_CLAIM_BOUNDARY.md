# Claim Boundary — Codec Semântico-Parabólico e RLL

**Estado:** `GOVERNANCE_RULE`  
**claim_allowed:** `false`

## 1. Escopo

O protocolo `RAFAELIA-PSC-1` pode organizar proveniência, relações, contradições, lacunas e evolução temporal de claims do RLL. Ele não altera o modelo cosmológico e não adiciona evidência observacional.

## 2. Relações permitidas

```text
symbol DESCRIBES concept
parable EXPLAINS method
codec SERIALIZES metadata
ledger CLASSIFIES claim
experiment PRODUCES result
result MAY_SUPPORT_OR_CONTRADICT model
```

## 3. Relações proibidas

```text
symbol PROVES cosmology
parable VALIDATES parameter
semantic compression IMPROVES likelihood
shared geometry IMPLIES shared physics
frequency label IMPLIES observed radiation
```

Use a relação explícita:

```text
PARABLE_OR_SYMBOL NOT_EVIDENCE_FOR COSMOLOGICAL_CLAIM
```

## 4. Três eixos

Todo claim importado por ponte deve registrar:

```text
source_status
epistemic_status
claim_gate
```

Exemplo:

```text
source_status = VERIFIED_LITERAL
epistemic_status = ANALOGY_ONLY
claim_gate = BLOCKED
```

## 5. Uso das sete heurísticas

- direta: reconstruir a sequência do pipeline;
- reversa: ligar resultado a dados, código e priors;
- antiderivada temporal: preservar revisões anteriores;
- derivada local: localizar a mudança de conclusão;
- contrafactual: registrar o falsificador;
- inversão de papéis: separar modelo, observador e instrumento;
- multiescala: verificar rastreabilidade do dataset ao relatório.

## 6. Gate científico

Um claim cosmológico continua dependente de:

```text
dataset identificado
checksum
preprocessing
likelihood
priors
baseline
convergência
incerteza
artefato
falsificador
reprodução independente
```

O codec pode registrar esses campos, mas não satisfazê-los sozinho.

## 7. Estado desta integração

```text
semantic_method = DOCUMENTED
rll_model_change = NONE
new_observational_evidence = NONE
cosmological_claim = TOKEN_VAZIO
```

## 8. Próximo teste

Aplicar o codec somente a um snapshot dos metadados do grafo epistêmico e comparar:

- preservação da proveniência;
- número de referências quebradas;
- ambiguidade de relações;
- tamanho total incluindo codebook;
- igualdade de reconstrução.
