# RLL — Índice de coeficientes D, matemática e laboratório de ondas V1

**Autoria/proponente:** Rafael Melo Reis — RAFAELIA  
**Data:** 2026-10-08  
**Estado:** NAVIGATION_AND_EVIDENCE_BOUNDARY; **produtor documental institucional**; sem alteração científica, claim_allowed=false.  
**Copyright (c) 2026 Rafael Melo Reis. SPDX-License-Identifier: LicenseRef-RAFCODE-Research-Commercial-0.1.**

## START HERE — rotas curtas

Este é um **índice**, não uma nova teoria nem uma substituição do registry. Use 1–3 roots pertinentes; profundidade inicial 1. Material antigo continua no mesmo caminho. A incorporação de novas provas no RLL exige aprovação no produtor e um falsificador.

1. **Modelo formal:** [`data/formulas/RAFAELIA_FORMAL_UNIFIED_CORE.md`](../../data/formulas/RAFAELIA_FORMAL_UNIFIED_CORE.md) e [`docs/formulas/RAFAELIA_SYMBOL_TABLE.md`](../formulas/RAFAELIA_SYMBOL_TABLE.md).
2. **Cosmologia/dinâmica efetiva:** [`docs/modules/structure_d_equations.md`](../modules/structure_d_equations.md), [`docs/FORMULAS_CANONICAS_INDEX.md`](../FORMULAS_CANONICAS_INDEX.md), [`docs/RLL_FRONTIER_STRUCTURE_INDEX.md`](../RLL_FRONTIER_STRUCTURE_INDEX.md).
3. **Aplicação experimental sintética, não cosmológica:** [EstudioAudio PR#57](https://github.com/rafaelmeloreisnovo/EstudioAudio/pull/57), [auditoria de operadores](https://github.com/rafaelmeloreisnovo/EstudioAudio/blob/feature/wave-physics-lab-readonly-20261008/docs/ROADMAPS_IA_HUMANOS/WAVE_LAB_D_COEFFICIENTS_OPERATOR_AUDIT_V1.md), [nota do Papers](https://github.com/rafaelmeloreisnovo/papers/blob/research/wave-lab-d-coefficients-20261008/research_notes/2026-10-08_D_COEFFICIENTS_WAVE_LAB_BRIDGE_V1.md).

**Autoridade:** este repositório institucional é o destino indicado pelo guard de autoridade do fork ([RLL fork PR #35](https://github.com/rafaelmeloreisnovo/relativity-living-light/pull/35), bloqueado de maneira intencional). O fork é [rafaelmeloreisnovo/relativity-living-light](https://github.com/rafaelmeloreisnovo/relativity-living-light). Os arquivos formal core, symbol table e `structure_d_equations` verificados têm **blobs Git idênticos** nas duas linhagens: respectivamente `8a8ab4c59f13fb6976c382e3e31c10d96780a07d`, `6cb2b435e492d0e099602ec1c5fd542763472622` e `dde00b0356013cb9cbce80d84fd3c2f8dc7c29f3`. O guard do fork fornece uma indicação operacional explícita: **mudanças científicas pertencem à branch/PR do Instituto**. Identidade de conteúdo por si só não dá autoridade; nenhuma migração automática de registry ou alteração científica é autorizada.

Na linhagem institucional, e **não na `main` do fork** na verificação de 2026-10-08, estão:
- [`data/governance/RLL_FORMULA_TEST_MATRIX_MF0001_MF0251_V1.json`](https://github.com/instituto-Rafael/relativity-living-light/blob/53671d2430347f01184fad8a99ca0ced2b0fe2c4/data/governance/RLL_FORMULA_TEST_MATRIX_MF0001_MF0251_V1.json): 251 entradas tipadas; itens `FORMAL`, de contexto e hipóteses não devem somar como 251 leis.
- [`data/formulas/RAFAELIA_168_FORMULAS_AUTORAIS_2026-09-12.md`](https://github.com/instituto-Rafael/relativity-living-light/blob/53671d2430347f01184fad8a99ca0ced2b0fe2c4/data/formulas/RAFAELIA_168_FORMULAS_AUTORAIS_2026-09-12.md): 168 candidatas/composições, não 168 novos resultados físicos.
- [`docs/science/RAFAELIA_CLASSICAL_MATH_FORMULA_AUDIT_20260808.md`](https://github.com/instituto-Rafael/relativity-living-light/blob/53671d2430347f01184fad8a99ca0ced2b0fe2c4/docs/science/RAFAELIA_CLASSICAL_MATH_FORMULA_AUDIT_20260808.md): auditoria de identidades clássicas, correções e definições condicionais.
- [`docs/RLL_NOVOEXPORT_FORMULA_ATLAS.md`](https://github.com/instituto-Rafael/relativity-living-light/blob/53671d2430347f01184fad8a99ca0ced2b0fe2c4/docs/RLL_NOVOEXPORT_FORMULA_ATLAS.md): contagens de **candidatos/ocorrências**, não novas fórmulas validadas.

## Namespace de D — eliminar colisões

| Namespace / símbolo | Fonte | Papel | Regra de não promoção |
|---|---|---|---|
| `D_graph[i]` = `D_i` | RAFAELIA_FORMAL_UNIFIED_CORE | ganho discreto adaptativo, `D_i=D0(1-tanh P_i)+Dneg*H(T_i-Theta_i)` | não chamar `m²/s` sem mapear escala/tempo |
| `D_graph0` = `D0` | mesmo formal core | ganho de base / retroalimentação entrópica | não confundir com `D_growth(z=0)` |
| `D_graph_neg` | mesmo formal core | mudança de ramo negativa | não confundir com potência RF negativa |
| `D_growth(z)` | structure_d_equations | fator de crescimento cosmológico sob convenções próprias | não herdar `D_graph` |
| `D_geom_theta` | Matem-tica- crosswalk PBIP | correção angular `-2ab cos theta` | unidade comprimento² |
| `D_quad` | Matem-tica- crosswalk PBIP | `C-B²/(4A)` | polinômio A≠0; domínio próprio |
| `D_distance(p,q)` | Fibonacci inverse ruler | métrica escolhida | não é ganho do grafo |
| `D_magnetic` | Papers phone observatory | declinação magnética | nem todos os telefones têm magnetômetro |

## Dados soltos na raiz: preservar, indexar, não mover

| Arquivo histórico | Tratamento |
|---|---|
| [`Matemática.md`](../../Matem%C3%A1tica.md) | texto histórico de fórmulas; remeter aos índices formais antes de citar |
| [`MathRaf.md`](../../MathRaf.md) | material histórico; ler correções formais antes de tratar período/ciclo como teorema |
| [`Numprimod.md`](../../Numprimod.md) | observações de números/resíduos; ligar por IDs e testes específicos, não fundir à física |
| [`ATLAS_CANONICO.md`](../../ATLAS_CANONICO.md) | índice topológico anterior, não sobrescrever inventário |
| [`docs/RLL_NEXT_SAFE_ACTIONS_INDEX.md`](../RLL_NEXT_SAFE_ACTIONS_INDEX.md) | ações documentais seguras de RLL/cosmologia; manter separado do plano de laboratório |

Nenhum desses documentos foi movido, renomeado ou reescrito por esta rota.

## Derivada, primitiva, inversa, reversa: contratos

Para ramo fixo `h=H(T-Theta)`:
- `partial_P D=-D0 sech² P`;
- `Integral_P D=D0(P-log cosh P)+Dneg*h*P+C`;
- `P=artanh(1-(D-Dneg*h)/D0)` se D0>0, h conhecido, argumento ∈(-1,1);
- a transição `T=Theta` é **descontínua**, logo não possui derivada clássica do degrau ali;
- a razão finita histórica `L=(T_t-T_(t-1))/(T_(t-1)+eps)` é um **proxy**, não a diferença logarítmica exata `log1p(L)`. Requer `T_t+eps>0` e `T_(t-1)+eps>0` para ambos;
- `reverse graph traversal != inverse function != reverse physical time`;
- permutações exigem relabeling coerente de estados, coeficientes e adjacência.

O núcleo do EstudioAudio implementa uma **fixture de roda undirecionada com 7 nós** (centro grau 6, anel grau 3), não a malha hexagonal completa do documento RLL. Baseline fixo `D=+0.10`, contraste `D=-0.10`, com stop em 32 passos ou magnitude 8; comparação somente **SIMULATION_ONLY_NOT_PHYSICAL_D**.

## Gates e filas

| Etapa | Status permitido | Evidência/autoridade |
|---|---|---|
| Fórmulas RLL no Git | SOURCE_PRESENT | blobs vinculados; sem claims |
| Operadores Java D, inversas/log/permutação | PASS_HOST no run 37739102478, HEAD a14bff18b4bf35906070e09bbb564e964b24458b | apenas fixture de host |
| Novo simulador W7 | IMPLEMENTED_UNTESTED até CI terminal HEAD | EstudioAudio produtor |
| APP Android completo | NOT_RUN / PENDING | CI de build do HEAD |
| Áudio e RF físico | TOKEN_VAZIO_UNCALIBRATED | fabricante/Android/experimento controlado |
| Fonte RLL cosmológica | BLOQUEADO para ponte automática | requer modelo físico e datasets adequados |
| Contagem total ~609 | TOKEN_VAZIO_UNRECONCILED | registry de IDs/deduplicação antes de afirmar |
| Autoridade dos PRs | INSTITUTE_CANONICAL_BRANCH_POLICY_OBSERVED | guard do fork; independent review ainda necessária antes de merge |

**P0 rádio:** nem leitura de cache nem cálculo do modelo podem modificar canal, potência, frequência, estado do modem, Bluetooth/Wi-Fi ou política GNSS. Somente leitura de APIs autorizadas; nenhum controle RF novo por este índice.

## Reconstrução humana/IA sem fricção

`Instituto RLL ATLAS → este índice D → fonte formal exata → estudo Papers → produtor EstudioAudio PR → teste CI exact-head → receipt físico → revisão de claim`.

Dados/fórmulas originais **não** foram migrados; o índice só acrescenta relações. Rollback: fechar PR da branch documental. Divergência factual deve gerar um sucessor auditável, nunca apagamento silencioso.

**R3:** F_ok = rotas tipadas e arquivos de raiz reconhecidos; F_gap = autoridade bifurcada, validação física e contagem deduplicada; F_next = consolidar CI sintética, build Android, receipt físico e revisões científicas independentes.
