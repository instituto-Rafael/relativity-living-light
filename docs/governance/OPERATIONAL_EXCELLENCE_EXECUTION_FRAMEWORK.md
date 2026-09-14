# Operational Excellence Execution Framework

## Status

`governance_record / execution_framework / audit_ready / claim_boundary`

Last updated: 2026-07-10

## Applied since last review

- `scripts/build_real_validation_report.py` now wires `rll_model_evidence_scan.json` (claim_status, best_by_AICc, best_by_BIC, H0_all_equal, blocking_reasons, warnings) into every generated report — closes the gap in issue #422.
- `data/pipelines/structure_d/joint_real_likelihood.py` `main()` now reads `STRUCTURE_D_JOINT_OUTPUT_STEM` from the environment, preventing accidental canonical-artifact overwrites when run directly — closes the gap in issue #401.
- Safe robust-fit runner: `scripts/run_structure_d_joint_likelihood.py` with `STRUCTURE_D_JOINT_OUTPUT_STEM`, `STRUCTURE_D_JOINT_SEED`, `STRUCTURE_D_JOINT_MAXITER`.
- Rapport semântico em dinâmicas estruturais documentado: heurísticas em 8 direções, protocolo OMEGA transdisciplinar, taxonomia de derivadas e matriz de invariantes operacionais — closes issue #409; ver [`docs/governance/RAPPORT_SEMANTICS_STRUCTURAL_DYNAMICS.md`](RAPPORT_SEMANTICS_STRUCTURAL_DYNAMICS.md).

## Purpose

Este framework implementa um plano operacional de excelência técnica para governança, auditoria, orquestração e pipelines do repositório.

Ele organiza execução e controle. Não valida RLL como teoria física.

## Scope boundary

Permitido:

```text
definir objetivos, papéis, métricas, ritos e trilha de execução
padronizar qualidade técnica, segurança, rastreabilidade e auditoria
```

Bloqueado:

```text
promover claim científica por melhoria de processo
converter governança em prova de verdade física
```

---

## 1) Objetivos mensuráveis de excelência operacional e técnica

Objetivos canônicos:

1. **Confiabilidade de execução:** manter pipelines críticos reprodutíveis e rastreáveis.
2. **Integridade de evidência:** preservar fronteira entre hipótese, dado, resultado e claim.
3. **Governança contínua:** registrar decisões operacionais com critério e revisão.
4. **Qualidade técnica:** reduzir falhas de consistência estrutural e documental.

KPIs mínimos (mensais):

| KPI | Definição | Meta inicial |
|---|---|---|
| `pipeline_success_rate` | execuções bem-sucedidas / execuções totais em workflows canônicos | >= 95% |
| `audit_closure_rate` | pendências de auditoria fechadas no ciclo / pendências abertas no ciclo | >= 80% |
| `traceability_coverage` | artefatos críticos com source+checksum+estado epistemico declarado | >= 90% |
| `claim_boundary_compliance` | documentos auditados sem sobreclaim / documentos auditados | 100% |

---

## 2) Mapeamento do estado atual

Fluxo operacional base:

```text
entrada (docs/data/scripts)
-> validações estruturais e workflows
-> artefatos em results/artifacts
-> auditoria e registro de fronteira de claim
```

Papéis operacionais:

| Papel | Responsabilidade |
|---|---|
| Maintainer | priorização, merge, critérios de aceitação |
| Curadoria de evidência | proveniência, source, checksum, estados |
| Auditoria | revisão de claim boundary, lacunas e contradições |
| Execução técnica | manutenção de scripts/workflows e estabilidade de pipeline |

Matriz de risco mínima:

| Risco | Efeito | Controle |
|---|---|---|
| sobreclaim científico | interpretação indevida de validade | claim gate explícito em docs e auditorias |
| baixa rastreabilidade | impossibilidade de reconstrução | manifests/checksums/registro epistemico |
| regressão de pipeline | bloqueio de validação operacional | padronização de execução e revisão pós-falha |
| acoplamento documento-evidência frágil | leitura ambígua | links canônicos para arquitetura/auditoria/registries |

---

## 3) Padrões formais

Padrões obrigatórios:

1. **Arquitetura:** separar claramente orientação pública, governança, auditoria, dados, execução e resultados.
2. **Qualidade:** toda melhoria de alto impacto deve explicitar objetivo, limite de claim e próximo passo.
3. **Segurança:** não expor credenciais, material privado ou fonte sem licença definida.
4. **Observabilidade:** cada pipeline crítico deve produzir artefatos de execução e estado final auditável.
5. **Documentação:** documentos de governança devem ser curtos, verificáveis e vinculados a paths canônicos.

---

## 4) Orquestrador e pipelines-alvo

Modelo de orquestração:

```text
planejar -> executar -> validar -> auditar -> decidir -> publicar estado
```

Pipelines-alvo por camada:

| Camada | Objetivo | Saída esperada |
|---|---|---|
| Policy checks | garantir fronteira de claim e política de dados reais | relatório/checksum de policy |
| Structural validation | verificar contratos, organização e consistência documental | relatório de conformidade |
| Evidence audit | validar proveniência e vínculo source->artifact | nota de auditoria e pendências |
| Reproducibility run | executar fluxo canônico de reprodução | artefatos em `results/` e `artifacts/` |

Critérios mínimos de compliance operacional:

- execução determinística quando aplicável;
- logs suficientes para reconstrução;
- artefatos com identificação de execução;
- estado final explícito (`VERIFIED`, `TOKEN_VAZIO`, `CLAIM_BLOCKED`, etc.).

---

## 5) Roadmap incremental

### Fase A — Quick wins

1. Consolidar KPIs e ritos deste framework no ciclo de revisão.
2. Garantir linkagem canônica em índices/documentos de governança.
3. Padronizar formato de pendências de auditoria.

### Fase B — Estrutural

1. Expandir cobertura de rastreabilidade para artefatos críticos remanescentes.
2. Melhorar robustez de workflows com trilha clara de falhas e remediação.
3. Consolidar catálogo de controles operacionais por pipeline.

### Fase C — Maturidade

1. Fechar lacunas recorrentes de auditoria por categoria.
2. Aumentar previsibilidade de execução e revisão externa.
3. Publicar estado operacional periódico com métricas e bloqueios.

---

## 6) Governança contínua

Ritos mínimos:

| Ritual | Frequência | Resultado |
|---|---|---|
| revisão operacional curta | semanal | status de pipeline e bloqueios imediatos |
| revisão de auditoria | quinzenal | fechamento de pendências e novos registros |
| revisão de governança | mensal | atualização de KPIs, riscos e prioridades |

Política de decisão:

```text
sem evidência suficiente -> manter bloqueado
com evidência parcial -> estado intermediário explícito
com evidência rastreável -> permitir promoção controlada
```

---

## 7) Aderência a práticas modernas

Referências de orientação (não equivalem a compliance automático):

- FAIR (dados e metadados);
- rastreabilidade por artefato (proveniência/auditoria);
- reproducibility-by-design (execução verificável);
- governança baseada em risco e evidência.

Checklist de aderência:

- [x] KPI atualizado no ciclo vigente
- [x] pendências críticas com owner e estado
- [x] links canônicos íntegros para governança/auditoria
- [x] fronteira de claim preservada nos documentos de alto impacto
- [x] trilha de execução reproduzível para pipelines críticos

---

## Final boundary

Este framework melhora execução e disciplina operacional.

Ele não:

- valida RLL;
- substitui revisão científica externa;
- converte processo em verdade física.
