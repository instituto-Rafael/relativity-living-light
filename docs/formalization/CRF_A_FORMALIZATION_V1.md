# CRF-A Formalization V1

**Scope:** 25 itens `FORMALIZE_NOW` do registry CRF.  
**Contract:** Definition → Lemma → Theorem → Proof → Test → Receipt.  
**Boundary:** `claim_allowed=false` para novidade/universalização.

## Regras

1. A expressão de cada item deve ser byte-equivalente ao campo `expression` do snapshot CRF de origem.
2. Prova matemática e teste executável são objetos distintos.
3. Testes finitos corroboram implementações/identidades; não substituem prova universal quando a prova é analítica.
4. CRF-006/007 são formalizados **condicionalmente** aos counts geométricos já testemunhados.
5. CRF-030 prova apenas o contrato interno de ausência tipada; equivalência/novidade frente a Option/Error/Bottom permanece prior-art.
6. `TOKEN_VAZIO` nunca é promovido a zero, PASS ou evidência.

## Censo

- Total A: **25**
- Formalização interna/derivada: **25**
- Novelty claim allowed: **0**
- Itens condicionais a witness externo: **CRF-006, CRF-007**
- Itens com prior-art/novelty ainda aberto apesar da prova interna: **CRF-001, CRF-016, CRF-017, CRF-021, CRF-027, CRF-029, CRF-030, CRF-031**

## Itens

| ID | Estado formal | Teorema/resultado |
|---|---|---|
| CRF-001 | PROVED_INTERNAL_REWRITE_SYSTEM | For every n∈N0, red(∅^n 0^n 1123)=123. |
| CRF-002 | PROVED_FINITE_COMBINATORICS | The edge-phase product set has cardinality 6·7=42. |
| CRF-003 | PROVED_ANGLE_CONVERSION | δ=15·π/180=π/12. |
| CRF-004 | PROVED_CLASSICAL_GEOMETRY | A_ann(θ)=θ(r_o²-r_i²)/2. |
| CRF-005 | PROVED_TRIGONOMETRIC_IDENTITY | q²+d²=R². |
| CRF-006 | PROVED_CONDITIONAL_ON_VERIFIED_COUNTS | Given the declared connected planarization counts, χ=2. |
| CRF-007 | PROVED_CONDITIONAL_ON_VERIFIED_COUNTS | The cycle-space dimension is 80. |
| CRF-008 | DEFINED_AND_BOUND_PROVED | 0<q<1 and q²=3/4. |
| CRF-009 | PROVED_DIMENSIONAL_SCALING | L_n=L_0q^n, A_n=A_0q^(2n), V_n=V_0q^(3n). |
| CRF-010 | PROVED_CIRCLE_GEOMETRY | Q(θ)=θ/[2 sin(θ/2)]. |
| CRF-011 | PROVED_REGULAR_POLYGON_GEOMETRY | s_n=2Rsin(π/n). |
| CRF-012 | PROVED_REGULAR_POLYGON_GEOMETRY | r_n=Rcos(π/n). |
| CRF-013 | PROVED_REGULAR_POLYGON_GEOMETRY | A_n=(n/2)R²sin(2π/n). |
| CRF-014 | PROVED_ORTHOGRAPHIC_PROJECTION_MODEL | a_e=R, b_e=R\|cos i\| and, when nondegenerate, e=\|sin i\|. |
| CRF-016 | PROVED_FROM_PROJECT_DEFINITIONS | R_(k+1)/R_k=q^(g_k)=(3/4)^(g_k/2). |
| CRF-017 | PROVED_FROM_PROJECT_DEFINITIONS | z_(k+1)/z_k=(q exp(iθ0))^(g_k) for integer g_k. |
| CRF-018 | PROVED_AFFINE_RECURRENCE | x_n=x*+q^n(x_0-x*). If \|q\|<1, x_n→x*. |
| CRF-021 | PROVED_REPARAMETERIZATION | F^R_n=F_n+2F_(n-1)+1 for n≥1. |
| CRF-022 | PROVED_ALGEBRAIC_INVERSE_STEP | F^R_(n-2)=F^R_n-F^R_(n-1)+1. |
| CRF-023 | PROVED_CIRCULANT_LAPLACIAN_SPECTRUM | L v_k=λ_k v_k with the stated λ_k. |
| CRF-025 | PROVED_STATE_SPACE_REPRESENTATION | s_(n+1)=M s_n iff the scalar recurrence holds. |
| CRF-027 | DEFINED_AND_BOUNDARY_PROVED | E_mod always returns a representable residue; E_strict returns VOID exactly outside the representable interval. |
| CRF-029 | PROVED_PERIODIC_RESIDUE_EMBEDDING | Π(n+420)=Π(n) for all n, and Π restricted to Z/420Z is injective. |
| CRF-030 | DEFINED_TYPED_ABSENCE_PROPAGATION | Under the declared lift, f̂(⊥_τ)=⊥_(τ') and type/absence status is preserved. |
| CRF-031 | PROVED_BOOLEAN_GATE_CONJUNCTION | C(c)=1 iff source, method, execution, artifact and reproduction gates are all 1; otherwise C(c)=0. |

## Autoridade

A forma máquina-a-máquina completa está em:

`data/formalization/crf_a_formalization_v1.json`

A CI gera um artifact determinístico com resultados de teste, proofs renderizados, manifest e checksums.

## R3

**F_ok:** 25 itens A recebem Definition/Lemma/Theorem/Proof/Test/Boundary/Token_Vazio.  
**F_gap:** prior-art global continua fail-closed; CRF-006/007 dependem do witness geométrico; indicadores operacionais de CRF-031 exigem binding por protocolo.  
**F_next:** CI determinística → artifact → receipt; depois promover sucessores B somente quando cada gate material fechar.
