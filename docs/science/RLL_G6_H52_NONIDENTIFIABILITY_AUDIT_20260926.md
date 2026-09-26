# RLL Δ — G6 H52 Non-identifiability Audit — 2026-09-26

**Autor:** RAFAEL MELO REIS  
**PR:** #992  
**Tested head:** `a3ee19d0a1a6deb54289ca38e5cbc59ee6c10558`  
**Workflow run:** `36233516529`  
**Estado:** `VERIFIED_LIMITED_CI`  
**claim_allowed:** `false`

## Pergunta atacada

A hipótese sucessora H52 perguntava se a falha de mistura do G6 era
materialmente causada pela não-identificabilidade de `z_t` e `w_t`
quando `Omega_s0 -> 0`.

O teste foi preregistrado antes da observação. Os dois braços preservaram
a mesma likelihood G4/G5, dados, covariâncias, seeds, walkers, comprimento
de cadeia e threshold `Rhat <= 1.10`.

## Validação executada

A execução CI `G6 H52 Nonidentifiability Audit` completou com sucesso:

1. ambiente científico mínimo — PASS;
2. testes unitários e fronteiras H52 — PASS;
3. proposal RNG emcee determinístico — PASS;
4. materialização Pantheon pinada — PASS;
5. reconstrução G4 — PASS;
6. congelamento G5 — PASS;
7. execução H52 — PASS;
8. verificação fail-closed — PASS;
9. artifact + checksums — PASS.

Artifact: `10903273097`  
Artifact SHA-256: `d8c03a113a979793dfcb7093723b6e39679fd30635e16eb0da35f6a48baef703`

## Resultado observado

| medida | free-shape | fixed-shape diagnóstico |
|---|---:|---:|
| max Rhat | 1.0216841816 | 1.0045413066 |
| gate Rhat <= 1.10 | PASS | PASS |
| Omega_s0 q95 | 0.2307281293 | 0.0081437197 |

Redução absoluta de max Rhat:

```text
0.0171428750
```

Redução do excesso `Rhat-1`:

```text
79.057053 %
```

Estado preregistrado obtido:

```text
LONGER_CHAIN_SUFFICIENT_H52_NOT_REQUIRED_FOR_CONVERGENCE
```

## Interpretação

O resultado **não suporta a necessidade de H52 para recuperar convergência**:
o braço livre, com `z_t` e `w_t` ainda livres, já passou o gate ao usar a
cadeia mais longa.

Isso reduz a incerteza causal do bloqueio antigo: a falha anterior de Rhat é
compatível com amostragem curta e não exige congelar a liberdade de forma.

O braço fixed-shape melhora adicionalmente o diagnóstico de mistura, mas essa
melhora não deve ser convertida em preferência física. A redução forte de
`Omega_s0 q95` também é esperada ao restringir graus de liberdade e **não é
comparação de evidência entre modelos**.

## Promoção permitida

```text
MCMC_CONVERGENCE
  -> RESOLVED_LIMITED_SUCCESSOR_BACKGROUND_G4_G5
```

Não promover:

```text
NESTED_SEED_STABILITY          = TOKEN_VAZIO
RLL_PERTURBATION_CLOSURE       = TOKEN_VAZIO
RLL_CLASS_CAMB_IMPLEMENTATION  = TOKEN_VAZIO
INDEPENDENT_REPLICATION        = TOKEN_VAZIO
claim_allowed                  = false
```

## Redução de incerteza

**Sim, observada.** Há duas reduções distintas:

- operacional: ambos os braços agora satisfazem o gate de convergência;
- diagnóstica: o max Rhat cai de 1.021684 para 1.004541 no braço controlado,
  equivalente a redução de ~79.06% do excesso acima de 1.

A conclusão mais conservadora é que a cadeia longa basta para remover o
bloqueio MCMC no escopo background G4/G5. H52 permanece útil como diagnóstico,
não como mecanismo necessário.

## Próximo Δ

Executar estabilidade de evidência nested multiseed sobre a mesma likelihood
hash-bound, sem alterar thresholds após observar resultados.

## Fronteira

Este receipt não valida fisicamente o RLL, não altera a preferência
observacional anterior por LambdaCDM, não fecha perturbações e não libera
implementação RLL em CLASS/CAMB.
