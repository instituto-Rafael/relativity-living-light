# RLL Evidence Classes V1 — E / C / H / P

Estado: `ACTIVE_GOVERNANCE`  
`claim_allowed=false`

## Invariante

```text
catálogo/checkpoint != bytes materializados
valor calculado != observação direta
proxy Bayes/BIC != evidência Bayesiana real
contexto de sessão != memória longitudinal
```

Todo resultado científico novo deve declarar `evidence_class`.

| Classe | Nome | Regra |
|---|---|---|
| `E` | Empírico/extraído | Extraído diretamente de bytes materializados e ligado a hash/receipt. |
| `C` | Calculado | Produzido por método explícito a partir de entradas materializadas. Não herda a classe `E`. |
| `H` | Hipotético/inferido | Hipótese, aproximação ou interpretação ainda sem fechamento material suficiente. |
| `P` | Prometido/checkpoint | A etapa está catalogada ou foi tentada, mas o valor não foi materializado. Deve usar `value=null` e estado `TOKEN_VAZIO_*`. |

## Promoção permitida

```text
P --materialização + hash--> E
E --método declarado-------> C
H --teste + receipt--------> E ou C
```

Não existe promoção automática de `C` para `E`.

## Caso canônico: run 31066012098

- o ZIP Pantheon existe e possui digest válido (`E` para a custódia dos bytes);
- o job Pantheon falhou antes de calcular as métricas; portanto, `ΔAIC` nessa run é `P`;
- os BICs de ΛCDM e RLL estão materializados no log;
- `ln(B10) ≈ −ΔBIC/2` é `C`;
- nested sampling / evidência Bayes real continua `P`.

Valores Pantheon obtidos por outra rota full-covariance podem ser ligados como referência independente, mas não podem ser reatribuídos retroativamente à run falha.

## Contrato mínimo

Um resultado `E` ou `C` exige:

```json
{
  "metric": "nome",
  "value": 1.0,
  "evidence_class": "C",
  "state": "CALCULATED_*",
  "method": "método explícito",
  "source_receipts": [
    {"artifact": "arquivo.zip", "sha256": "..."}
  ],
  "claim_allowed": false
}
```

Um resultado `P` exige:

```json
{
  "metric": "nome",
  "value": null,
  "evidence_class": "P",
  "state": "TOKEN_VAZIO_*",
  "source_receipts": [],
  "claim_allowed": false
}
```

## Fronteira de repositório

O RLL público recebe código, schemas, hashes, receipts sanitizados e resultados científicos claim-bounded. Corpus conversacional, chunks privados, provider IDs privados, keystores e material longitudinal bruto permanecem fora desta autoridade pública.
