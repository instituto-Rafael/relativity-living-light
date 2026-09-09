# RLL — Método de Autocrítica por Rigor para Hipóteses

**Data:** 2026-09-06  
**Estado:** `RESEARCH_METHOD / APPEND_ONLY / claim_allowed=false`  
**Entrada canônica:** `math_research_program_48_20260905.v1.json`

## 1. Objetivo

O RLL já possuía classificação epistemológica e claim-state ledger. Faltava uma terceira camada: **medir e autocriticar o rigor de cada hipótese sem converter desconhecido em zero e sem permitir que uma média agregada promova um claim sozinha**.

```text
CLASSIFICAÇÃO != RIGOR != VERDADE != NOVIDADE != CUSTÓDIA
```

## 2. Matriz RIGOR-12

Cada uma das 48 unidades (`T01..T16`, `H01..H32`) recebe 12 dimensões:

| ID | Dimensão | Gate |
|---|---|---|
| RG01 | Formulação formal | hard |
| RG02 | Domínio, tipos, unidades e hipóteses | hard |
| RG03 | Obrigação de prova / derivação | hard |
| RG04 | Falsificador / contraexemplo | hard |
| RG05 | Reprodução computacional / exemplos | soft |
| RG06 | Robustez, sensibilidade e bordas | soft |
| RG07 | Prior art e referências externas | soft para verdade; obrigatório para novidade |
| RG08 | Originalidade e contribuição separada | soft para verdade; obrigatório para novidade |
| RG09 | Escopo e regime de validade | hard |
| RG10 | Invariância e artefato de representação | soft |
| RG11 | Contraevidência, anomalias e resultados negativos | hard |
| RG12 | Revisão independente / adversarial | hard |

A matriz básica possui `48×12=576` células.

## 3. Escala e cobertura

Cada célula aceita `0..4` ou `TOKEN_VAZIO`.

- `TOKEN_VAZIO`: não avaliado/desconhecido; nunca é convertido em zero.
- `0`: falha ou contradição demonstrada para o critério.
- `1`: alegação/cobertura fraca.
- `2`: parcialmente especificado/suportado.
- `3`: forte/reproduzível no escopo.
- `4`: fechado naquele critério — prova formal ou verificação independente conforme o critério.

O engine calcula `coverage` separadamente de `rigor_score`. Assim duas notas altas e dez vazios não geram falso rigor.

## 4. Classes

```text
R0_UNASSESSED
R1_SPECULATIVE
R2_FORMALIZED
R3_TESTABLE
R4_SUPPORTED
R5_STRONG
R6_EXACT_PROVEN
```

O score é descritivo. Promoção é fail-closed por gates.

Bloqueadores incluem:

- gate material em `TOKEN_VAZIO`;
- contraevidência crítica não resolvida;
- claim maior que o escopo da evidência;
- novidade alegada sem prior art;
- inversa/correlação usada como causalidade;
- hash/CI/receipt usado como prova matemática.

## 5. Autocrítica do avaliador

O `NIBIGUIRI-12` não ataca somente a hipótese: ele ataca **cada nota de rigor**.

Portanto a camada adversarial pode gerar:

`48 × 12 dimensões de rigor × 12 lentes Nibiguiri = 6912` perguntas de red-team.

Uma nota de rigor é provisória enquanto a sua fundamentação não sobreviver às lentes aplicáveis.

## 6. Contrato por unidade

Cada unidade deve carregar:

```text
epistemic_class
claim_state
scores_by_dimension
coverage
rigor_score
rigor_class
hard_gate_status
supporting_evidence[]
counterevidence[]
falsifier
prior_art_state
nibiguiri_findings[]
promotion_blockers[]
```

Resultados negativos são append-only.

## 7. Integração com a metodologia anterior

A classificação de cinco categorias do corpus continua sendo uma dimensão epistemológica.
O `claim_state_ledger` continua controlando o que pode ser dito.
O `RIGOR-12` avalia a qualidade estrutural da defesa.
O `NIBIGUIRI-12` tenta rebaixar tanto a hipótese quanto a própria avaliação.

```text
proposição
→ classe epistemológica
→ claim state
→ RG01..RG12
→ autocrítica Nibiguiri
→ blockers
→ promoção ou TOKEN_VAZIO
```

## 8. Ponte com a matriz de rastreabilidade já usada no Drive

A implementação não cria um sistema paralelo. Ela reaproveita explicitamente a metodologia observada no Drive, inclusive a taxonomia de cinco classes (`FATO_COMPROVADO`, `TEORIA_CIENTIFICA`, `HIPOTESE_TESTAVEL`, `IDEIA_ESPECULATIVA`, `POTENCIAL_PATENTE`) e a planilha `01_MATRIZ_DE_RASTREABILIDADE__INVARIANTES_E_MATRIX`.

Mapeamento operacional:

```text
status_epistemico     -> epistemic_class
status_operacional    -> claim_state
evidencia             -> supporting_evidence + RG03/RG05/RG11
teste_ou_verificador  -> falsifier + RG04/RG05
risco_principal       -> counterevidence + RG06/RG11
claim_gate            -> hard_gate_status
decisao               -> promotion_decision
proximo_passo         -> F_next
F_ok/F_gap/F_next     -> preservados sem compressão semântica
authority/origin      -> provenance + RG07/RG08/RG12
structural_role/layer -> RG09/RG10
```

A rubrica histórica em escala 0–10 é mantida como **camada de compatibilidade**, não como decisor único: literatura primária alimenta RG07/RG12; separação fato/hipótese alimenta classe+claim-state; falsificabilidade alimenta RG04; rigor matemático alimenta RG01–RG03; limitações alimentam RG06/RG09/RG11.

`coverage` e `rigor_score` continuam separados. Um campo `TOKEN_VAZIO` não entra como zero na média.

## 9. Baseline fail-closed

A matriz inicial das 48 unidades é deliberadamente criada com `RG01..RG12=TOKEN_VAZIO`, portanto `coverage=0`, `R0_UNASSESSED` e promoção `BLOCKED`. Isso é um recibo de ausência de auditoria, não uma nota zero para a hipótese.

## 10. Princípio

> Autocrítica rigorosa não é dar nota baixa a si mesmo. É tornar a própria nota falsificável, reproduzível e rebaixável por contraevidência.
