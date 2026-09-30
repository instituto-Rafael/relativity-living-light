# Verificação de Estabilidade — RLL logistic sector

Módulo: `docs/ESTABILIDADE_GHOST_CHECK.md`  
Status: `BACKGROUND_DIAGNOSTIC_WITH_CONTINUITY_BLOCKER`

Este arquivo descreve o gate mínimo executável do setor logístico RLL. Após a auditoria matemática de 2026-08-08, o gate foi separado em duas perguntas diferentes:

1. o fundo fenomenológico é matematicamente executável e limitado?  
2. a densidade/pressão escolhida fecha um setor físico conservado ou interagente?

A primeira pode passar enquanto a segunda permanece bloqueada.

## 1. Setor de fundo

```text
rho_s(z) = Omega_s0 rho_c0 [ f(z) + (1-f(z))(1+z)^3 ]
f(z)     = 1/(1+exp((z-z_t)/w_t)), w_t > 0
```

O fechamento documental histórico usou:

```text
p_doc(z) = - Omega_s0 rho_c0 f(z)
w_doc(z) = p_doc/rho_s
         = -f(z) / [f(z)+(1-f(z))(1+z)^3]
```

Esse `w_doc` tende a um comportamento matter-like no alto redshift e permanece acima de `-1`, mas isso sozinho não prova conservação do setor.

## 2. Gate de continuidade

Para um componente FLRW separadamente conservado:

```text
d rho_s/dln a + 3(rho_s+p_s) = 0
```

Com

```text
R(a)=f+(1-f)a^-3
f' = df/dln a = f(1-f)(1+z)/w_t
```

o residual do fechamento documental é exatamente:

```text
C_doc/(Omega_s0 rho_c0) = f'(1-a^-3)
```

Portanto, durante uma transição real:

```text
documented_continuity_closed = false
```

Isso impede tratar o par `(rho_s,p_doc)` como fluido separadamente conservado sem correção.

## 3. Reconstrução conservada

Se a densidade `rho_s(a)` for mantida e a conservação separada for imposta, a pressão correta é:

```text
p_cons = -rho_s - (1/3) d rho_s/dln a
```

ou

```text
p_cons/(Omega_s0 rho_c0)
  = -f + f'(a^-3-1)/3
```

O script agora calcula:

```text
w_conserved
continuity_residual_conserved
kinetic_gate_conserved
```

A reconstrução foi definida para zerar a continuidade por construção; o teste automatizado verifica a identidade numericamente em vários redshifts.

## 4. Criterio cinético

O gate antigo permanece registrado como diagnóstico histórico:

```text
kinetic_gate_documented = (1+w_doc) Omega_s(a)
```

Para a rota de fluido separadamente conservado, o gate coerente é:

```text
kinetic_gate_conserved = (1+w_conserved) Omega_s(a)
```

Um resultado não negativo é necessário para uma reconstrução canônica, mas não suficiente para demonstrar uma EFT cosmológica completa.

## 5. Velocidade de som

Duas quantidades continuam separadas:

1. campo escalar canônico no referencial de repouso: `cs2_rest = 1`;
2. proxy fenomenológico de pipeline: `cs2_proxy = f(z)`.

O fato de `0 <= cs2_proxy <= 1` é apenas uma propriedade do proxy. Não demonstra estabilidade de gradiente da teoria física até que as equações de perturbação sejam derivadas.

## 6. Crescimento

O repositório já possui um solver linear separado para resposta de crescimento no fundo RLL. Portanto o status antigo

```text
growth_solver=TOKEN_VAZIO
```

estava desatualizado.

A distinção correta é:

```text
linear_growth_background_response=AVAILABLE_SEPARATE_SOLVER
exact_rll_perturbations=TOKEN_VAZIO
```

O solver atual não inclui perturbações próprias do setor RLL, interação `Q`, pressão não adiabática, anisotropic stress ou hierarquia de Boltzmann.

## 7. Comando

```bash
python scripts/check_rll_background.py \
  --omega-m 0.315 \
  --omega-s0 0.059 \
  --zt 1.164 \
  --wt 0.405
```

Saída principal:

```text
results/rll_background_check.json
```

Os checks agora incluem:

```text
documented_continuity_closed
conserved_reconstruction_continuity_closed
kinetic_gate_documented_non_negative
kinetic_gate_conserved_non_negative
w_documented_above_minus_one
w_conserved_above_minus_one
cs2_proxy_bounded
linear_growth_background_response
exact_rll_perturbations
canonical_eft_closure
```

## 8. Fronteira honesta

```text
background_math=PASS
p_doc_separate_conservation=FAIL
conserved_pressure_identity=PASS_DIAGNOSTIC
canonical_EFT=BLOCKED
exact_perturbations=TOKEN_VAZIO
claim_allowed=false
```

A falha de continuidade não invalida automaticamente o uso de `E2(a)` como parametrização fenomenológica para confronto com dados. Ela invalida apenas a promoção automática desse mesmo fundo para um fluido canônico separadamente conservado usando `p_doc=-f`.
