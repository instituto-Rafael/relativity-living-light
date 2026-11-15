# RLL Ω — Protocolo de verificação de bytes JSON no CI — 2026-11-15

**Fonte:** `instituto-Rafael/relativity-living-light` · **base:** `rll/lab@3be5a7ed6f66ed07db65539460ce70e726c71f3c` · **escopo:** blobs JSON versionados em Git. **Estado inicial:** `IMPLEMENTED_UNTESTED`; `claim_allowed=false`.

## Motivo e sucessão
Esta nota complementa, sem substituir nem apagar, `docs/science/RLL_JSON_CODEX_DEDUP_EVIDENCE_BOUNDARY_20261114_V1.md`. A implementação inicial emitia um manifesto completo de hashes em `$RUNNER_TEMP` e imprimia apenas contagens no resumo de CI; os hashes dos arquivos **não eram recuperáveis** após o encerramento do runner. A nova revisão conserva esse manifesto durante sete dias como artefato de GitHub Actions, para reconciliação controlada no Supabase privado.

## Contrato de coleta
- O workflow `.github/workflows/rll-json-dedup-gate.yml` faz checkout do commit exato da PR, roda os testes negativos e executa `scripts/audit_rll_json_dedup.py`.
- O manifesto contém somente metadados de arquivos que **já estão publicamente versionados no GitHub**: caminho, Git blob ID, tamanho, SHA-256 dos bytes carregados pelo runner, SHA-256 do JSON canônico quando válido, número de registros e estados `PARSED`, `SIZE_LIMIT` ou `PARSE_FAILED`. Contém grupos de conteúdo idêntico e nenhuma transcrição privada do Codex.
- Nenhuma carga JSON de origem é exportada, nenhum token/credencial é usado ou gravado. O pacote não é um dataset bruto. O registro de hash não prova propriedade intelectual, autoria ou originalidade científica.
- `if: always()` preserva o manifesto inclusive quando um gate falha; falha anterior não é convertida em PASS. A ausência do arquivo faz o step de upload falhar.
- Retenção de sete dias e pin da Action em commit SHA. **O artefato de CI deste repositório público não deve receber nomes, dados, hashes ou metadados de arquivos privados do Drive.**

## Reconciliar de maneira reversível
1. Confirmar commit HEAD da PR e o resultado do workflow específico; não usar apenas status agregado.
2. Baixar via API autenticada o artefato da execução e verificar que `source.repository_commit` corresponde exatamente ao SHA checkout.
3. Auditar `counts.json_like_paths = len(file_receipts)`, `parsed_files + size_limit_files + len(parse_failures) = json_like_paths`.
4. Gravar em `raf_private` um registro **sucessor append-only** de SHA-256 por caminho `(repo, commit, path, Git blob SHA, run_id)`, sem atualizar os 762 registros antigos de Git object identity-only.
5. Em caso de falha, truncamento, arquivo malformado, JSON com chave duplicada, fonte alterada ou hash ausente, usar `TOKEN_VAZIO` tipado e nunca inferir equivalência.
6. Conferir readback do novo índice, manter os originais Git e a história de execução, registrar um μRECEIPT independente.

## Estados que este PR não fecha
- Dedup semântico de fórmulas cosmológicas e 486 ocorrências históricas: `NOT_RUN`.
- Dedup do corpus privado Codex/Google Drive: `NOT_RUN`.
- Validação física do modelo RLL contra DESI/Pantheon+/CMB/growth: `BLOCKED`.
- Avaliação completa da suite Python e YAML: depende de outra revisão (PR #1195).
- Merge, promoção científica, deleção: `NOT_EXECUTED_BY_THIS_WORKFLOW`.

**R3:** F_ok = coleta criptográfica executável com metadados públicos delimitados; F_gap = execução exata e reconciliação de dados ainda pendentes; F_next = inspecionar CI, baixar receipt, conciliar no Supabase e validar por readback. Rollback = não mesclar esta proposta e conservar o histórico; se incorporada, usar PR sucessor com reversão explícita.
