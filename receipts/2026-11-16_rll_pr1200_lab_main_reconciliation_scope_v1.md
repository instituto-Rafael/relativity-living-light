# RLL PR #1200 — reconciliação lab/main, escopo 1

- mu_id: MU-RLL-PR1200-STDLIB-FORWARDPORT-20261116-S1
- intent: reconciliar `rll/lab` com `main` sem descartar histórico, comportamento nem evidência.
- source_pr: https://github.com/instituto-Rafael/relativity-living-light/pull/1200
- merge_base: `c5d1f5b4ef249f7b59043ae1325b4d7a0d6637a1`
- main_observed: `ac833cb1278ffde951e602dd70df4c11bcda6ac0`
- lab_parent: `65905da20881b638a6c9293c524316f53bfe3b42`
- branch: `work/rll-pr1200-reconcile-stdlib-gates-20261116`
- scope: **branch isolada**; `main` e `rll/lab` não são alteradas.
- source_tree_diff: 801 caminhos só main, 486 só lab, 264 alterados nos dois lados com blob igual, 49 candidatos a reconciliação com blobs diferentes (árvores recursivas GitHub; não classificar os 49 como conflitos textuais sem merge de três vias).

## Delta de código

1. `.github/workflows/calc-data.yml`: trocar instalação pip de pandas/numpy pela validação Python stdlib já existente (`tools/validate_calc_data_stdlib_migration.py`). Preservado o pin lab de setup-python e upload-artifact.
2. `.github/workflows/import-data.yml`: trocar instalação pip de requests/pandas pela verificação `py_compile scripts/import_data.py rx/http.py`. Os dois scripts têm blobs iguais em main/lab. Preservados pins lab de Actions.

## Gate de evidência

- Readback do GitHub confirmou o conteúdo integral e SHA dos dois arquivos alterados.
- O comparativo de escopo registra exatamente dois arquivos de workflow alterados contra o HEAD inicial de lab.
- Não houve execução de CI neste receipt; testes Python, dependências do runner, Android, ciência e runtime permanecem `NOT_RUN`/`TOKEN_VAZIO`.
- Estado: `IMPLEMENTED_UNTESTED`; `claim_allowed=false`; **não** há PASS global.
- A PR #1200 segue `mergeable=false`; o saldo restante exige análise semântica e testes dos outros caminhos, especialmente contratos, geometrias, experimentos e pipelines de ciência.

## Controle e rollback

Não promover esta branch, não alterar `main` ou `rll/lab`, não usar `ours/theirs` globalmente. Rollback operacional: abandonar a branch de trabalho, preservando commits originais; para correção após promoção, criar sucessor revisado. Falsificador: scripts, importações ou outputs divergirem de main/lab ou CI exact-head falhar.

R3: `F_ok` = dois forward-ports gravados e verificados por readback; `F_gap` = 49 candidatos no baseline, CI não executada, risco semântico remanescente; `F_next` = CI direcionada nos dois workflows + reconciliação de 3 vias dos arquivos de maior risco, com gates antes de qualquer merge.
