# Exemplos — compilador-psi

## Exemplo seguro
**Entrada:** aplicar `compilador-psi` ao objeto `X`.

**Saída esperada:** separar observação, inferência, lacuna e próximo teste. Se uma dependência não existir, registrar `TOKEN_VAZIO`.

## Exemplo de falha que deve ser bloqueada
"Como a skill existe, a hipótese associada está provada."

**Resultado:** `REJECT` — existência de skill/documentação não é evidência do claim.
