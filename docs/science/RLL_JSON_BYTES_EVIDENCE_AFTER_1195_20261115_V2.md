# RLL Ω — Git JSON byte-evidence gate V2 (2026-11-15)

Status: `PROPOSED_REVIEW` · `claim_allowed=false` · `publication_effect=NONE`.

## Autoridade
- Produtor: `instituto-Rafael/relativity-living-light`.
- Base desta proposta: `rll/lab@80d839b8758c475b0a4bbb1dc519664fcc16082d`.
- Predecessor: [PR #1196](https://github.com/instituto-Rafael/relativity-living-light/pull/1196), ainda não incorporada ao RLL na leitura de 2026-11-15.
- Correção upstream confirmada: PR #1195 mesclada em `rll/lab`; o código de teste Git temporário e a chave duplicada do Dependabot estão agora no produtor, de forma que o successor evita os dois falsos bloqueios.

## Delta pequeno e reversível
A coleta JSON existente passa a emitir o manifesto de *metadados de arquivos já públicos* como artefato de GitHub Actions por **sete dias**, sem copiar valores dos JSON nem o corpus privado do Drive/Codex.

Além da contabilidade de `file_receipts`, exige correspondência exata `source.repository_commit == EXPECTED_SOURCE_COMMIT`, cardinalidade de caminhos distintos, `parsed_files=json_like_paths` e `size_limit_files=symlink_skipped=parse_failed_unique_blobs=0`. Cada caminho processado deve ter estado `PARSED`, `git_blob_oid` hexadecimal de 40 posições, `raw_sha256` e `canonical_json_sha256` hexadecimais de 64 posições. Arquivo incompleto ou malformado faz o gate falhar. O passo de upload `if: always()` conserva diagnósticos existentes após falha; **upload bem-sucedido não modifica o resultado do gate**.

Nenhum secrets/variables/members/settings/rulesets é criado ou alterado; `permissions.contents=read` e SHA fixo das Actions permanecem.

## Limites
- SHA-256 direto de bytes do arquivo e do objeto JSON canônico **não prova equivalência física**, autoria nem prioridade.
- Repetição de registros em resultados históricos **não autoriza exclusão**.
- Histórico dos receipts `RLL_JSON_762_RAW_CANONICAL_CI_20261115_S2` e `MU-RLL-JSON-526-RECORD-TAXONOMY-20261115-S4` continua preservado no Supabase/Drive. Esta proposta não sobrescreve os registros.
- `claim_allowed=false`; confirmação do código/CI exato não é confirmação das equações cosmológicas.

## Aceitação e rollback
Exigir workflow **RLL JSON Dedup Evidence Gate** na revisão atual, Python tests, YAML Deep Audit, branch maturity e convenção. Resolver todos os checks exigidos pela política antes de merge **humano/autorizado**. Se algum resultado for negativo, manter `DRAFT/HOLD`, tipar o motivo e abrir sucessor, não modificar `rll/lab` diretamente.

Rollback antes do merge: não promover o PR. Depois de um merge autorizado, reverter em outra branch revisável, preservando os recibos anteriores. `rollback_executed=false`.
