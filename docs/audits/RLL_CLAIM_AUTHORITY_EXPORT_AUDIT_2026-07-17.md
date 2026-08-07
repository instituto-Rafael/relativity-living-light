# Auditoria do Export de Autoridade RLL

Data: `2026-07-17`  
Branch: `docs/rll-claim-authority-export-20260717`  
Estado: `IMPLEMENTED_NOT_MERGED / CI_PASS / claim_allowed=false`

## O que foi gravado

- export machine-readable dos estados de claim RLL;
- preservação do resultado computacional registrado em `20260709-132833-utc`;
- distinção entre resultado local, superioridade ampla e confirmação física;
- validador fail-closed;
- workflow com checksum e artifact.

## Leitura permitida

```text
A execução registrada comparou os modelos presentes no JSON de entrada.
Na métrica BIC daquele artefato, CPL venceu e o relatório marcou RLL_PERDE.
```

## Leituras bloqueadas

```text
RLL perdeu universalmente.
CPL é a teoria verdadeira.
RLL foi confirmado fisicamente.
RLL é estatisticamente superior em geral.
Uma execução substitui replicação, revisão e novos dados.
```

## Estado observado da CI

```text
workflow = RLL Claim Authority Export
run_id = 29557372658
status = completed
conclusion = success
```

No mesmo commit também concluíram com sucesso os workflows de consistência de convenções, fórmulas/artefatos, validação YAML, Fisher, pipeline científico RLL, análise bayesiana e testes Python. O sucesso valida contratos, sintaxe e execução do pacote; não promove verdade física.

## Limitações preservadas

- `source_ref=main` ainda não é pin imutável de commit;
- o blob SHA protege o conteúdo dos arquivos citados, mas não substitui um manifesto assinado;
- novas execuções podem alterar o estado, desde que preservem a história;
- consumidores precisam registrar `STALE_CONSUMER` quando ficarem atrás do produtor;
- esta mudança não executa likelihood, MCMC ou comparação nova.

## Critério de promoção

```text
CI PASS: atendido para o pacote desta branch
pin por commit/tag
checksum do export
sincronização no consumidor
revisão do escopo/not_claimed
claim_allowed permanece false para verdade física
```

## Resultado

O RLL passa a oferecer uma primeira interface explícita de produtor de claims. Ela permite consumo rastreável sem transformar um README interpretativo em autoridade científica paralela. O pacote passou na CI, mas continua draft e `claim_allowed=false` até revisão e merge.
