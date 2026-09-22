# RLL A1.2 — Gauge e regularização da variável de momento

**Data:** 2026-09-22  
**Estado:** CANDIDATE / CI_PENDING  
**claim_allowed:** false

## Objetivo

A1.1 passou os nove gates necessários de fundo, mas ainda não fornece uma teoria
perturbativa completa. A1.2 congela uma linguagem de referência e elimina a
divisão explícita por \(1+w_s\) da variável de momento principal.

## Gauge de referência

```text
ds^2 = a^2[-(1+2 Psi)d tau^2 + (1-2 Phi) delta_ij dx^i dx^j]
```

Definições:

```text
delta_s = delta rho_s / rho_s
theta_s = divergência de velocidade em Fourier
U_s     = (1+w_s) theta_s
q_w     = d ln(1+w_s) / d ln a
c_a^2   = w_s - q_w/3
```

O sound speed do candidato permanece explícito:

```text
c_s,rest^2 = 1
```

como hipótese A1.1, não como propriedade derivada do fundo RLL.

## Equações candidatas

```text
delta_s'
 = -U_s
   + 3(1+w_s) Phi'
   - 3 H (c_s^2-w_s) delta_s
   - 9 H^2 (c_s^2-c_a^2) U_s/k^2
```

e

```text
U_s'
 = H [q_w-(1-3c_s^2)] U_s
   + c_s^2 k^2 delta_s
   + (1+w_s) k^2 Psi
```

A segunda forma vem de derivar \(U_s=(1+w_s)\theta_s\) e é comparada
numericamente à forma em \(\theta_s\) longe do limite \(1+w_s=0\).

## Gate executável

O gate A1.2:

1. verifica ausência de crossing fantasma no sweep declarado;
2. evita dividir por pontos com \(1+w_s\le10^{-12}\);
3. mede \(q_w\), \(c_a^2\) e o coeficiente efetivo de \(U_s\);
4. verifica equivalência algébrica das formas \(\theta_s\leftrightarrow U_s\);
5. classifica rigidez como LOW/MODERATE/HIGH sem transformar rigidez em
   falsificação física automática.

## Proveniência externa

- Ma & Bertschinger (1995), arXiv:astro-ph/9506072: gauges e equações lineares.
- CLASS `explanatory.ini`: `cs2_fld` é o sound speed no frame comóvel do fluido.
- CAMB `symbolic.py`: sound speed de dark energy é tratado no rest frame.

Essas referências sustentam a semântica da representação, não validam o RLL.

## Lacunas preservadas

- super-horizon initial conditions: `TOKEN_VAZIO`;
- mapa A1.2 → CLASS: `TOKEN_VAZIO`;
- mapa A1.2 → CAMB: `TOKEN_VAZIO`;
- residual completo Einstein/Bianchi: `TOKEN_VAZIO`;
- convergência de solver e observáveis: `TOKEN_VAZIO`.

Logo:

```text
A1.2_REGULARITY_PASS != PERTURBATION_CLOSURE_RESOLVED
```

## R3

F_ok: gauge de referência + variável U_s + C01/C02 candidatos + gate de
regularidade falsificável.

F_gap: IC, mapas independentes CLASS/CAMB, Bianchi/constraints, integração
completa e observáveis.

F_next: consumir CI A1.2; se PASS, derivar IC no mesmo contrato e só então
implementar os dois backends independentes.
