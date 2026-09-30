# Route56 Mirror12 — projeção triangulada 6+6 por eixo de 45°

Date: 2026-09-12
Parent: PR #881 quadratic projection bridge
Claim allowed: **false**

## Construção

Base Route56:
`P(8,2)=56`.

Para cada eixo de 45°:
- CW: `+30,+60,+90,+120,+150,+180`;
- CCW: `-30,-60,-90,-120,-150,-180`.

Logo:
- 12 rotas assinadas por eixo-base;
- 8×12 = 96 projeções direcionais locais;
- 56×12 = 672 projeções sobre Route56;
- 56×12×6 = 4032 células projetadas com os seis POIs acadêmicos.

## Resíduo quadrático

`d=√2-1`.

Para cada offset `φ`:
`p=d cosφ`, `q=d sinφ`, `p²+q²=d²`.

O par `+φ/-φ` é um espelho:
`p(+φ)=p(-φ)`, `q(+φ)=-q(-φ)`.

## Fechamento

`gcd(45,30)=15`.

A união global fecha em 24 direções únicas de 15°.

Os percursos `+180°` e `-180°` coincidem geometricamente, mas permanecem rotas assinadas distintas.

## Boundary

Exact combinatorial/algebraic geometry only.

`PROJECTED_ROUTE != EMPIRICAL_EVIDENCE != PHYSICAL_CLAIM`
`claim_allowed=false`
