# RLL A1.3 — Série super-horizonte local do componente

**Data:** 2026-09-22  
**Estado:** CANDIDATE / CI_PENDING  
**claim_allowed:** false

## Proveniência imediata

A1.2 foi incorporado em `rll/lab` pelo PR #957, merge
`6c451eedc704fdd54beee2e13e954473eee7c074`.

O run científico canônico `35721844002` produziu:

```text
state = A1_2_GAUGE_VARIABLE_REGULARIZATION_PASS_IC_OPEN
cases = 9/9 PASS
stiffness = 5 LOW / 3 MODERATE / 1 HIGH
class_camb_unlock = false
token_resolution = NOT_RESOLVED
```

O caso HIGH é:

```text
(z_t,w_t) = (10,0.05)
max |q_w|   = 210.621933305...
max |c_a^2| = 71.312612113...
asymptotic_points = 1633
```

Esse resultado não é descartado; ele permanece como requisito explícito para
qualquer solver posterior.

## Limite inicial do fundo

Para todo ((z_t,w_t)) finito do sweep A1:

[
z	oinfty
quadRightarrowquad
f(z)	o0,qquad
ho_spropto a^{-3},
]

e, no candidato conservado:

[
w_s	o0,qquad q_w	o0,qquad c_a^2	o0.
]

O gate usa (z=10^4) como verificação numérica do limite declarado, sem
substituir a identidade assintótica.

## Subproblema de referência

Defina

[
x=k	aull1,
qquad
U_s=(1+w_s)	heta_s.
]

No subproblema **local do componente**, adotamos:

[
mathcal H=rac1	au,
qquad
Psi=Psi_0,
qquad
Phi'=0
]

através da ordem retida. Isso é uma referência de potencial congelado, não a
solução Einstein–Boltzmann completa.

Com (w_s=q_w=c_a^2=0) e (c_{s,m rest}^2=1), escrevendo
(U_s=k,v_s), as equações reduzidas são:

[
rac{ddelta_s}{dx}
=
-v_s-rac{3}{x}delta_s-rac{9}{x^2}v_s,
]

[
rac{dv_s}{dx}
=
rac{2}{x}v_s+delta_s+Psi_0.
]

## Série regular

Procure:

[
rac{delta_s}{Psi_0}
=d_0+d_2x^2+d_4x^4+cdots,
]

[
rac{v_s}{Psi_0}
=v_1x+v_3x^3+v_5x^5+cdots.
]

A recorrência exata dá:

[
d_0=-rac32,qquad
v_1=rac12,
]

[
d_2=v_3=-rac1{28},
]

[
d_4=rac1{280},
qquad
v_5=rac1{840}.
]

Logo:

[
oxed{
rac{delta_s}{Psi_0}
=
-rac32-rac{x^2}{28}+rac{x^4}{280}+O(x^6)
}
]

e

[
oxed{
rac{U_s}{kPsi_0}
=
rac{x}{2}-rac{x^3}{28}+rac{x^5}{840}+O(x^7)
}.
]

As seis relações de recorrência são testadas com aritmética racional exata.

## Relação adiabática líder

Se o mesmo modo primordial de radiação satisfaz
(delta_gamma/Psi_0=-2), então:

[
rac34delta_gamma
=
-rac32Psi_0
=
delta_s+O(x^2).
]

Portanto o coeficiente líder é compatível com a condição adiabática usual.

**Importante:** os coeficientes de ordem superior dependem do potencial
congelado. Correções métricas e anisotropic stress de neutrinos podem alterá-los.

## O que A1.3 não fecha

Ainda permanecem:

- sistema inicial Einstein + fótons + neutrinos completamente acoplado;
- anisotropic stress de neutrinos;
- normalização primordial;
- transformação explícita para o gauge síncrono/variáveis de CLASS;
- transformação independente para CAMB;
- residual Bianchi/Einstein perturbado;
- convergência do solver e paridade de observáveis.

Assim:

```text
A1.3_COMPONENT_LOCAL_IC_PASS
!=
FULL_COSMOLOGICAL_INITIAL_CONDITIONS
```

## R3

F_ok: limite inicial do fundo + série regular local + recorrência exata +
compatibilidade adiabática líder tornam-se executáveis.

F_gap: métrica/radiação/neutrinos acoplados, normalização, mapas de solver,
constraints e integração.

F_next: consumir CI; se PASS, construir o sistema leading-order acoplado,
mantendo os coeficientes locais como controle e não como axioma universal.
