# Lagrangiano Efetivo — EFT mínima do setor logístico RLL

Módulo: `docs/LAGRANGIANO_EFT.md`  
Status: `BLOCKED_UNTIL_CONSERVATION_OR_INTERACTION_SEMANTICS_SELECTED`

## 1. Objetivo

O RLL possui um setor logístico de fundo cosmológico. Uma parametrização de `H(z)` pode ser testada fenomenologicamente sem microfísica completa, mas uma reconstrução como campo escalar canônico exige uma condição adicional: a densidade e a pressão usadas no mapeamento devem formar um setor covariantemente consistente.

A ação canônica de referência continua sendo:

```text
S = integral d4x sqrt(-g) [ R/(16 pi G) + L_m + L_r + L_phi ]
L_phi = -1/2 g^{mu nu} partial_mu phi partial_nu phi - V(phi)
```

Com assinatura `(-,+,+,+)`, para campo homogêneo:

```text
rho_phi = K + V
p_phi   = K - V
K       = phi_dot^2 / 2
w       = p_phi/rho_phi
```

Logo, para um setor canônico já fechado:

```text
K(a) = (1+w(a)) rho_phi(a)/2
V(a) = (1-w(a)) rho_phi(a)/2
```

## 2. Fundo logístico implementado

Defina

```text
f(z) = 1/(1+exp((z-z_t)/w_t)), w_t > 0
R(a) = f(a) + (1-f(a)) a^-3
```

com `a=(1+z)^-1`.

O fundo implementado é:

```text
rho_s(a) = Omega_s0 rho_c0 R(a)
E2(a)    = Omega_m a^-3 + Omega_Lambda + Omega_s0 R(a)
```

Historicamente os documentos também atribuíram:

```text
p_doc(a) = - Omega_s0 rho_c0 f(a)
w_doc(a) = -f(a)/R(a)
```

Essa razão é algebraicamente bem definida e continua útil como descrição do fechamento documental original. A auditoria de 2026-08-08 mostrou, porém, que ela não fecha a equação de continuidade de um componente separadamente conservado durante a transição.

## 3. Gate de continuidade

Para um fluido FLRW separadamente conservado:

```text
d rho_s / d ln a + 3 (rho_s + p_s) = 0
```

A derivada exata da transição é:

```text
df/dln a = f(1-f)(1+z)/w_t
```

E

```text
dR/dln a = (df/dln a)(1-a^-3) - 3(1-f)a^-3
```

Usando `p_doc`, o residual adimensional é:

```text
C_doc/(Omega_s0 rho_c0)
  = dR/dln a + 3(R-f)
  = (df/dln a)(1-a^-3)
```

Portanto:

```text
p_doc + rho_s + separate_conservation = FAIL during a genuine transition
```

O residual só zera identicamente quando a transição deixa de variar (`df/dln a=0`) ou no ponto específico `a=1`.

## 4. Duas rotas físicas possíveis

### 4.1 Rota A — fluido efetivo separadamente conservado

Se `rho_s(a)` for preservada como densidade física do setor e o setor conservar separadamente, a pressão é determinada pela continuidade:

```text
p_cons = -rho_s - (1/3) d rho_s/dln a
```

Em unidades de `Omega_s0 rho_c0`:

```text
p_cons_factor = -f + (df/dln a)(a^-3 - 1)/3
```

Assim:

```text
w_cons(a) = p_cons/rho_s
          = [-f + (df/dln a)(a^-3-1)/3]
            / [f+(1-f)a^-3]
```

Somente depois dessa reconstrução é permitido aplicar diretamente:

```text
K_cons(a) = (1+w_cons) rho_s / 2
V_cons(a) = (1-w_cons) rho_s / 2
```

E, para um campo escalar canônico minimamente acoplado:

```text
d phi / d ln a = M_Pl sqrt(3 Omega_s(a) [1+w_cons(a)])
```

O código `scripts/check_rll_background.py` agora calcula `w_conserved`, `kinetic_gate_conserved` e o residual reconstruído.

### 4.2 Rota B — setor interagente

Se o projeto decidir preservar `p_doc=-Omega_s0 rho_c0 f`, então a continuidade precisa conter uma fonte/troca. Com a convenção

```text
d rho_s/dln a + 3(rho_s+p_s) = Q_s/H
```

o termo requerido é:

```text
Q_s/H = Omega_s0 rho_c0 (df/dln a)(1-a^-3)
```

Nesse caso precisa existir um setor receptor com troca igual e oposta para preservar a conservação total. Como o fundo atual mantém matéria como `a^-3` e Lambda constante, essa compensação ainda não está implementada.

```text
interaction_closure=TOKEN_VAZIO
```

## 5. Velocidade de som

Para campo escalar canônico no referencial de repouso:

```text
cs2_rest = 1
```

O pipeline também calcula:

```text
cs2_proxy(z) = f(z)
```

Esse objeto permanece apenas um proxy limitado em `[0,1]`. Ele não deve ser promovido a velocidade de som física das perturbações sem derivação.

## 6. Comando executável

```bash
python scripts/check_rll_background.py \
  --omega-m 0.315 \
  --omega-s0 0.059 \
  --zt 1.164 \
  --wt 0.405
```

Saída:

```text
results/rll_background_check.json
```

O relatório diferencia explicitamente:

```text
w_documented
w_conserved
continuity_residual_documented
continuity_residual_conserved
kinetic_gate_documented
kinetic_gate_conserved
linear_growth_background_response=AVAILABLE_SEPARATE_SOLVER
exact_rll_perturbations=TOKEN_VAZIO
```

## 7. O que está fechado

- fundo logístico `E2(a)` executável;
- derivada analítica de `f` e de `rho_factor`;
- residual exato de continuidade para o fechamento documental;
- reconstrução de pressão/equação de estado exigida por conservação separada;
- teste numérico do fechamento reconstruído;
- distinção entre proxy de `cs2` e `cs2_rest=1` canônico.

## 8. O que permanece aberto

- escolher formalmente entre fluido conservado, setor interagente ou puro fundo fenomenológico;
- inverter `a(phi)` e produzir `V(phi)` somente após essa escolha;
- se interagente, especificar o setor receptor e `Q` covariantemente;
- correções de loop e naturalidade;
- equações completas de perturbação do novo setor;
- Boltzmann/CLASS/CAMB parity;
- propagação posterior de incertezas em `f'`, `w`, `K` e `V`;
- evidência Bayesiana canônica unificada com covariâncias completas.

## 9. Critério de claim

```text
background_phenomenology=PASS
separate_conservation_with_p_doc=FAIL
conserved_effective_fluid_reconstruction=IMPLEMENTED_DIAGNOSTIC
canonical_scalar_physical_closure=BLOCKED
interacting_sector=TOKEN_VAZIO
```

Nenhuma semelhança com quintessência, DESI ou uma forma logística autoriza claim de mecanismo físico antes da escolha de semântica e da validação das perturbações.
