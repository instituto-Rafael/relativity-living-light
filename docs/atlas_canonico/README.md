# Atlas Canônico Numerado

Router para `ATLAS-GPT-PROJECT-000001-V1`.

## Entrada
- `ATLAS_CANONICO_NUMERADO_V1.md`: inventário humano completo de 280 itens.
- `atlas.schema.yaml`: contrato de tipagem, estados, relações e proveniência.
- `relations_v1.tsv`: sementes de relações tipadas entre objetos/registries.
- `RECEIPT_2026-09-22.md`: receipt de materialização.

## Princípio
URL/pasta é a porta de entrada; o **ID canônico** é a unidade de identidade.

```
URL raiz -> Atlas -> IDs -> relações -> evidências -> fontes
```

## Compatibilidade
Não renumerar nem apagar registries históricos (`TH-*`, `PRM-*`, Ω300, GETP-369). O Atlas os referencia por relações tipadas.

## Gates
`SOURCE != ARTEFATO != EXECUÇÃO != EVIDÊNCIA != CLAIM`  
`TOKEN_VAZIO != 0`  
`IMPLEMENTED_UNTESTED != PASS`

Correções são append-only via `supersedes`; histórico não é apagado.
