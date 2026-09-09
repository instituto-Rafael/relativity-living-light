# RLL — Área de Requerimento, Procedimento e Autocrítica por Rigor V2

**Data:** 2026-09-06  
**Estado:** `RESEARCH_METHOD / FAIL_CLOSED / APPEND_ONLY / claim_allowed=false`  
**Preset padrão:** `MAX_RIGOR_MATHEMATICS`

## 1. Objetivo

Fechar o processo de pesquisa sem depender de memória operacional:

`REQUERIMENTO → NORMALIZAÇÃO → ESCOPO → FONTE → DEDUP → FORMALIZAÇÃO → EVIDÊNCIA → FALSIFICADOR → RIGOR → NIBIGUIRI → DEPENDÊNCIAS → GATES → REVISÃO → TRANSIÇÃO → RECEIPT`

Toda etapa não terminal deve possuir `next_action`. Ausência de próximo passo é erro estrutural.

## 2. Cinco superfícies

1. **REQUERIMENTO** — quem pediu, qual unidade T/H, qual objetivo do claim, preset e data.
2. **PRESET/TUNING** — política versionada de rigor; pesos/thresholds são política autoral, não constantes científicas.
3. **PROCEDIMENTO** — P00..P14, com estado, ação, evidência, rollback e next_action.
4. **EVIDÊNCIA/CLAIM** — INFO_PRIME, claim-state canônico, prova, contraevidência, falsificador, prior art e dependências.
5. **EVENTOS/ROLLBACK** — syslog append-only com event_id/run_id/trace_id/source_commit/transição/razão.

## 3. Claim-state canônico

O V2 liga diretamente ao `knowledge_ecosystem/claim_state_ledger.md`:

`RAW_ORAL, RAW_NOTE, METAFORA, PARABOLA_DIDATICA, HIPOTESE, REF_REQUIRED, TOKEN_VAZIO, SOURCE_LINKED, METHOD_DEFINED, EVIDENCE_LINKED, RESULT_REPRODUCED, PEER_OR_REVIEW_READY, CLAIM_ALLOWED, CLAIM_BLOCKED`.

Nenhum alias local (`PASS_EXACT`, `HYPOTHESIS`, etc.) pode substituir o vocabulário canônico.

## 4. RIGOR-12

Cada unidade usa RG01..RG12. Cada célula aceita:

- `TOKEN_VAZIO`: ainda não auditado, nunca é zero;
- `0..4`: avaliação observada;
- `NOT_APPLICABLE_WITH_REASON`: somente com motivo e se o preset autorizar.

A saída nunca usa uma nota isolada. Emite:

`coverage, observed_score, lower_bound, upper_bound, rigor_class, hard_gate_status, blockers, decision`.

## 5. Hard gates

Hard gate é fail-closed se:

- `TOKEN_VAZIO`;
- `N/A`;
- valor inválido;
- valor numérico abaixo do mínimo do preset.

Logo, nota baixa em gate material não pode virar `ELIGIBLE_FOR_REVIEW`.

## 6. Classes monotônicas

`R0 → R1 → R2 → R3 → R4 → R5 → R6`

Uma classe só é alcançada se todas as classes anteriores puderem ser alcançadas.

`R6_EXACT_PROVEN` exige:
- coverage=1 no conjunto aplicável;
- `proof_status=PROVEN`;
- statement formal;
- todos os hard gates em 4;
- nenhuma contraevidência crítica não resolvida.

## 7. Preset / tuning

### MAX_RIGOR_MATHEMATICS
Padrão para as 48 unidades matemáticas. Usa:
- 96 lentes Nibiguiri V2;
- Relation Calculus 12;
- A–E disponível para análise de ordem;
- resultados negativos append-only;
- revisão independente requerida para claim permitido;
- mudança de claim/method/evidence/source torna assessment `STALE_REVIEW_REQUIRED`.

### FORMAL_PROOF
Mais estrito para teoremas/provas.

### DIAGNOSTIC_FAIL_CLOSED
Diagnóstico estrutural; nunca é promoção automática.

## 8. Autocrítica V2

O Nibiguiri completo já existente no RLL é `8 famílias × 12 direções = 96 lentes`.

Para 48 unidades e 12 dimensões de rigor:

`48 × 12 × 96 = 55.296`

endereços adversariais possíveis.

Isso é espaço de obrigação, não quantidade de análises concluídas.

A autocrítica também deve atacar:
- o score;
- a justificativa;
- o peso;
- o threshold;
- a própria lente/red-team.

## 9. G0..G6 herdados do Drive

- G0 fonte identificada;
- G1 duplicidade avaliada;
- G2 definição/domínio;
- G3 relações/dependências;
- G4 evidência ou TOKEN_VAZIO;
- G5 teste/verificador;
- G6 risco/rollback.

## 10. Proveniência por avaliação

Toda avaliação material deve ligar:
- `claim_hash`;
- `method_hash`;
- `evidence_snapshot_hash`;
- `source_commit`.

Mudança em qualquer base invalida a avaliação corrente até revisão.

## 11. Evidência

Cada evidência possui ID único, origem, data, domínio, claim-state, artefato, limite, dimensões que suporta e relação do revisor (`SELF`, `SAME_TEAM`, `INDEPENDENT`, `EXTERNAL`).

Contraevidência é primeira classe:
`COUNTEREXAMPLE`, `FAILED_PROOF`, `FAILED_REPRODUCTION`, `BOUNDARY_FAILURE`, `CONTRADICTION`.

## 12. Procedimento P00..P14

P00 REQUEST_RECEIVED  
P01 REQUEST_NORMALIZED  
P02 SCOPE_BOUND  
P03 SOURCE_BOUND  
P04 DEDUP_CHECKED  
P05 FORMAL_STATEMENT_BOUND  
P06 EVIDENCE_BOUND  
P07 FALSIFIER_BOUND  
P08 RIGOR_ASSESSED  
P09 NIBIGUIRI_ASSESSED  
P10 DEPENDENCIES_PROPAGATED  
P11 GATES_EVALUATED  
P12 REVIEW_REQUIRED  
P13 ELIGIBLE_FOR_CLAIM_TRANSITION  
P14 COMPLETED_RECEIPT

O engine nunca muda um claim automaticamente para `CLAIM_ALLOWED`.

## 13. Invariantes

`TOKEN_VAZIO != 0`  
`N/A != desconhecido`  
`score != verdade`  
`coverage != rigor`  
`hash != prova`  
`CI != teorema`  
`matriz grande != completude`  
`mesmo número != mesmo objeto`  
`branch != PR != merge != main`

## 14. Testes P0

A suíte V2 cobre:
- baseline fail-closed;
- hard gate baixo bloqueante;
- classes monotônicas;
- R6 incompleto proibido;
- N/A com motivo/perfil;
- prior art obrigatório para novidade, não para verdade;
- staleness;
- 55.296 endereços adversariais;
- P00..P14 sem missing step;
- claim-state canônico.

`STRUCTURAL PASS != MATHEMATICAL PROOF`.
