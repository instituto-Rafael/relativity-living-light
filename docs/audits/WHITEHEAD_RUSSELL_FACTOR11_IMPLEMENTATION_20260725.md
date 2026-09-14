# Auditoria de implementação — Whitehead–Russell / Ontologia discreta / fator 11

**Data:** 2026-07-25  
**Branch:** `codex/ontology-whitehead-russell-factor11`  
**PR:** `#588`  
**Claim global:** `claim_allowed=false`

## Entrega

| Componente | Estado | Função |
|---|---|---|
| módulo tipado | IMPLEMENTADO | distingue classe, cardinal, palavra e apresentação racional |
| proveniência 77/33 | IMPLEMENTADO | preserva `common_scale=11` sem alterar o valor `7/3` |
| gate físico | IMPLEMENTADO | retorna `TOKEN_VAZIO` sem observável físico |
| schema | IMPLEMENTADO | JSON Schema Draft 2020-12 + fronteira estrutural do repositório |
| ledger | IMPLEMENTADO | registra conhecidos, desconhecidos e claims proibidos |
| testes | IMPLEMENTADOS | 11 testes: tipos, aritmética, gauge, claim gate e CLI sem `PYTHONPATH` |
| validação local | EXECUTADA | 11 testes aprovados; 15 gates; compilação Python aprovada |
| inferência cosmológica | NÃO ALTERADA | nenhum parâmetro ou likelihood foi modificado |
| evidência física do fator 11 | TOKEN_VAZIO | exige morfismo, unidades, previsão e dados |

## Invariantes operacionais

1. `77/33 == 7/3` permanece cálculo exato.
2. `gcd(77, 33) == 11` permanece proveniência exata.
3. `11_word` tem comprimento 2; decimal 11 é outro tipo.
4. observável racional é invariável à escala comum.
5. observável sensível à escala gera `HYPOTHESIS`, nunca promoção automática.
6. `claim_allowed` permanece `false` em todos os caminhos.
7. a implementação não toca no background RLL, datasets ou resultados existentes.

## Revisão adversarial

### Defeito 1 — execução direta do validador

A primeira versão dependia implicitamente de `PYTHONPATH=src`. O defeito foi reproduzido e corrigido com bootstrap explícito de `src/`. Um teste subprocess remove `PYTHONPATH` e executa o comando documentado.

### Defeito 2 — fronteira estrutural dos schemas

Os primeiros workflows do PR mostraram:

```text
schema parse: 34/34 OK
claim boundary: FAIL
```

Causa raiz: o novo schema não continha `description` declarando simultaneamente `structural` e `contract`, exigência de `tools/validate_schemas_claim_boundary.py`.

Correção aplicada:

```json
"description": "Structural contract for typed discrete ontology, factor-11 provenance, and claim-gated physical promotion in RLL."
```

O gate determinístico falhou por propagação desse mesmo passo, não por falha matemática ou cosmológica. Novas execuções foram disparadas após a correção.

## Riscos controlados

- **Erro de tipo:** bloqueado por classes distintas.
- **Confusão entre AIC/Bayes e ontologia:** fora do módulo e explicitamente proibida.
- **Promoção retórica:** bloqueada pelo ledger e pelo gate.
- **Perda da escala 11:** evitada pelo registro de proveniência.
- **Acoplamento físico inventado:** preservado como `TOKEN_VAZIO`.
- **Schema parseável porém incompatível com governança:** coberto pelo validador raiz e pela correção registrada.

## Comandos de reprodução

```bash
python -m pytest -q tests/test_discrete_ontology.py
python tools/validate_discrete_ontology_claim.py --write-report
python tools/validate_schema_contracts.py
```

## Resultado

A entrega transforma o cruzamento em um objeto **compilável, testável, auditável e autocorretivo**, preservando a ontologia como fundação e impedindo que ela seja confundida com observação cosmológica.
