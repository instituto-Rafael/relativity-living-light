# RLL — Ponte Ω7 Modular-Geodésica, Toroidal e Focal — 2026-08-18

**Estado:** `RESEARCH_BRIDGE + CLAIM_GATED`  
**claim_allowed:** `false`

Fonte canônica da sessão: `rafaelmeloreisnovo/Matem-tica-@7475728a92ff3d19382257e5f9579c072ee87b3e`, `papers/2026-08-18_omega7_modular_geodesic_toroidal_focus.md`.

## Relação com formalismos RLL existentes

Esta nota liga, sem identificar ontologicamente, os seguintes blocos já presentes no ecossistema:

```text
modularidade multibase
+ sqrt(3)/2 / trigonometria equilátera
+ toro / esfera / Poincaré
+ derivada / antiderivada
+ matriz multidirecional
+ curvatura/Hessiano em superfícies de energia
```

## Invariantes da sessão

```text
0_modular != TOKEN_VAZIO
ratio_equal != same_geometric_scale
sphere != torus
Poincare_map != sphere
osculating_focus != global_circle_focus
geometric_circulation != physical_vortex
analogy != mechanism
```

Para

\[
\Pi(n)=(n\bmod7,n\bmod14,n\bmod10),
\]

\[
\Pi(7)=(0,7,7),
\qquad
\operatorname{lcm}(7,14,10)=70.
\]

Para seção circular do tubo:

\[
w(\alpha)=2r\sin\alpha.
\]

Sob a definição `w_med=r`:

\[
\alpha=30^\circ.
\]

A aproximação parabólica local fornece

\[
f_{local}=r/2.
\]

Os focos locais radialmente interno/externo

\[
F_\pm(u)=\left(R\pm\frac r2\right)(\cos u,\sin u,0)
\]

recuperam por média a linha central

\[
C(u)=R(\cos u,\sin u,0).
\]

## F_gap

1. `TOKEN_VAZIO_APG`: símbolo/operador APG trigonométrico ainda sem localização inequívoca.
2. Falta contrato canônico entre resíduos `7/14/10` e coordenadas angulares/geométricas.
3. Falta preservar formalmente razão, vetor primitivo e escala em schema executável.
4. Falta generalizar as projeções para centros não coincidentes e rotações arbitrárias.
5. Não há campo de velocidades; portanto `vortex_physical = NOT_ESTABLISHED`.
6. Não há índices de refração/interface; portanto `refraction_physical = NOT_ESTABLISHED`.
7. A parábola osculante é aproximação local; ray tracing focal global não foi demonstrado.
8. `999` como codificação modular e `999 Hz` são objetos distintos; unidade/tempo precisam ser explícitos.
9. Falta execução única com sweep angular, fixtures, hashes, artefatos e CI.

## F_next

### Gate G1 — modular

Implementar e provar por teste:

```text
Omega7ModState(n)
compatibility_7_14_10
phase70
```

### Gate G2 — geometria preservada

Implementar `GeomRational` com razão reduzida + vetor primitivo + escala + orientação.

### Gate G3 — geometria analítica

Validar equilátero→esfera, Bhaskara reta–esfera, seção toroidal, tangentes 30°, foco osculante e recuperação da linha central.

### Gate G4 — sweep

Executar `u,alpha` em `[0,2pi)` com resolução declarada e produzir artefatos auditáveis.

### Gate G5 — física opcional

Somente após G1–G4:

```text
vortex: v -> curl(v) -> flux -> pressure -> boundary conditions
refraction: n1,n2 -> interface -> Snell -> ray tracing -> focal statistics
```

## Claim boundary

```text
math_local_relations = DEFINED_OR_DERIVABLE
geometric_synthesis = PROPOSED_TESTABLE_MODEL
physical_vortex = TOKEN_VAZIO
physical_refraction = TOKEN_VAZIO
universal_law = TOKEN_VAZIO
claim_allowed = false
```

## R3

```text
F_ok   = relações geométricas locais podem ser formalizadas sem colapsar objetos distintos
F_gap  = APG, contratos, execução e física ainda não fechados
F_next = implementar e falsificar primeiro a geometria; física só depois dos gates
```
