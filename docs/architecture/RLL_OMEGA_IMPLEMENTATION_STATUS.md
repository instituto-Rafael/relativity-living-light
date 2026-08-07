# RLL Ω — Estado de Implementação e Lacunas Remanescentes

**Data:** 2026-07-14  
**Branch:** `audit/omega-opposition-validity-20260714`  
**Limite:** implementação metodológica; não valida o modelo RLL.

## Implementado

- `src/rll_photonic/omega_adapter.py`
  - resíduo normalizado com incerteza observacional e de modelo;
  - classificação ordenada entre `R_TOKEN_VAZIO`, `R_OUT_OF_DOMAIN`, `R_NUMERICAL`, `R_CALIBRATION`, `R_INSTRUMENT`, `R_TRANSPORT`, `R_MATTER_FIELD` e `R_PHYSICS`;
  - magnitude do resíduo não promove automaticamente `R_PHYSICS`;
  - gate por oposição com `SUPPORTED_ONLY`, `REFUTED_ONLY`, `BOTH`, `NEITHER`, `SCOPE_SPLIT` e `TOKEN_VAZIO`;
  - verificações mínimas de intensidade e polarização.
- `scripts/rll_omega_residual_audit.py`
  - leitura de fixture JSON;
  - cálculo dos resíduos normalizados;
  - emissão de relatório `rll.omega_residual_audit.v1`;
  - modo `--strict` para invariantes fotônicos.
- `schemas/rll_omega_residual_input.schema.json`
  - contrato de entrada, checks, pesos, domínio e proveniência.
- `examples/rll_omega_residual_example.json`
  - fixture sintética explicitamente não física.
- testes locais: 10 casos sintéticos.
- workflow isolado: `.github/workflows/rll-omega-adapter.yml`.

## Ordem de exclusão

```text
PROVENIENCIA / INCERTEZA
  -> DOMINIO
  -> NUMERICO
  -> CALIBRACAO
  -> INSTRUMENTO
  -> TRANSPORTE
  -> MATERIA-CAMPO
  -> CANDIDATO FISICO
```

A classe `R_PHYSICS` significa apenas que os checks declarados anteriores passaram e que existe um candidato físico registrado. Não significa descoberta, validação ou nova lei.

## Lacunas ainda abertas

1. o executor ainda não consome datasets cosmológicos reais;
2. não está conectado às likelihoods existentes;
3. não existe propagação de covariância matricial completa;
4. `physics_candidate` é declaração de entrada e exige revisão independente;
5. não há comparação entre instrumentos ou populações observacionais;
6. não há penalização por complexidade, AIC, BIC ou evidência bayesiana neste adaptador;
7. o schema não consegue impor igualdade de comprimento entre arrays; essa regra é verificada pelo executor;
8. falta validação contra dados reais e replicação externa;
9. o repositório usado neste PR é `rafaelmeloreisnovo/relativity-living-light`; a sincronização com o repositório canônico da organização deve permanecer uma decisão separada e revisada.

## Próximo gate

Conectar o adaptador primeiro a uma fixture observacional pública e versionada, com operador identidade e resposta instrumental declarada. A integração à likelihood real só deve ocorrer após teste de regressão que demonstre que o adaptador não altera resultados quando todos os resíduos são compatíveis com o modelo de referência.

## Estado epistêmico

```text
IMPLEMENTADO_COM_TESTE_SINTETICO:
  - normalização
  - classificação ordenada
  - oposição por escopo
  - invariantes mínimos
  - CLI e schema

TOKEN_VAZIO:
  - evidência observacional real
  - integração likelihood
  - covariância completa
  - replicação independente
  - promoção física
```
