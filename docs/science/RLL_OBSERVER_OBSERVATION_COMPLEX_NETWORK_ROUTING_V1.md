# RLL — Observador, observação e cursos científicos em rede complexa V1

**Governing closure:** `CLOSURE_L13`  
**State:** `SOURCE_CONTRACT_NOT_EXECUTION_PROOF / claim_allowed=false`

## Fechamento novo

Cada ocorrência relevante passa a ser um nó auditável:

```text
OBSERVER
  -> OBSERVATION
  -> EPISTEMIC_STATE
  -> CONDUCT
  -> SCIENCE_ROUTE(S)
  -> EVIDENCE / CONTRADICTION / GAP
  -> REQUIRED_GATE
  -> RECEIPT
  -> NEXT_ACTION or ROLLBACK
```

### Estados epistemológicos

`OBSERVED`, `NEW_OBSERVED`, `UNCERTAIN`, `UNKNOWN`, `OPPORTUNITY`,
`CONTRADICTION`, `ANOMALY`, `REJECTED`, `VERIFIED_LIMITED`, `SUPERSEDED`.

### Condutas

A linguagem da sessão foi normalizada sem apagar a origem:
atenção→`ATTENTION`; atendimento→`ATTEND`; atuação→`ACT`; atualizar→`UPDATE`;
revisar→`REVIEW`; recusas→`REFUSE`; bug→`BUG`; erros→`ERROR`;
edição→`EDIT`; pensar→`THINK`; permutar→`PERMUTE`; anomalias→`ANOMALY`;
∆→`DELTA`; ∅→`EMPTY_OR_GAP`.

### Tags do ∅ observado

`POSSIBLE`, `VERBAL`, `ATEMPORAL`, `IGNORED_PREVIOUSLY`,
`NONVERBAL`, `INCONSISTENCY`, `FORGOTTEN_RECOVERED`, `PARADOX`,
`NONLINEAR`, `MULTIFILAMENT_PATH_RELATION`.

## Cursos/áreas científicas

O contrato contém rotas explícitas para cosmologia observacional, estatística/Bayes,
física matemática, geometria/topologia, redes complexas, plasma/MHD,
eletromagnetismo, óptica quântica/fotônica, acústica, termodinâmica,
partículas/astropartículas, análise numérica, engenharia de software/métodos
formais, teoria da informação/sinais, metrologia/proveniência, epistemologia,
biofísica/neurociência e governança/reprodutibilidade.

Uma observação pode ter várias áreas, mas deve marcar `PRIMARY` e `SECONDARY`.
A multiplicidade de áreas não cria causalidade.

## Rede complexa

Nós: Observer, Observation, ScienceRoute, Conduct, Evidence, Gap, Contradiction,
Gate, Receipt, Artifact e Route.

Arestas: `OBSERVED_BY`, `CLASSIFIED_AS`, `ROUTED_TO`, `ACTED_AS`,
`SUPPORTED_BY`, `CONTRADICTS`, `DEPENDS_ON`, `FALSIFIED_BY`,
`REQUIRES_GATE`, `PRODUCES_RECEIPT`, `CLOSES_GAP`, `SUPERSEDES`,
`ROLLBACK_TO`, `BRIDGES_TO`.

Cada aresta material exige proveniência própria.

## Invariantes

```text
OBSERVER != OBSERVATION
NEW != TRUE
UNKNOWN != ZERO
UNCERTAIN != FALSE
ANOMALY != MECHANISM
OPPORTUNITY != EVIDENCE
PARADOX != CONTRADICTION
MULTIFILAMENT_RELATION != CAUSALITY
```

## R3

F_ok = taxonomia disciplinar + estados + condutas + grafo + gaps + gates definidos.
F_gap = execução em observações sucessoras e revisão humana das tags científicas.
F_next = integrar intake em RafPolimata e correção programática em RafGitTools.
