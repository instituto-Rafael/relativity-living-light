# Fontes do projeto ↔ RLL — integração vetorial V1

Estado: `IMPLEMENTED_LOCAL / CLAIM_ALLOWED=false / RAW_BODIES_NOT_COMMITTED`.

## Regra de autoridade

As fontes alimentam busca, proveniência e geração de hipóteses; não promovem conclusão científica. O RLL continua autoridade apenas para ciência observacional, datasets, likelihoods, modelos, falsificadores e resultados reproduzíveis.

## Lote

O lote deduplicado contém 14 corpos. O manifesto registra SHA-256, tamanho, linhas, estado temporal, relação com o RLL, visibilidade e política de ingestão. Os textos brutos permanecem fora do Git e são lidos somente de um diretório local fornecido pelo operador.

## Rotas

- `RLL_DIRECT_AND_METHODOLOGY`: FASE 21, grafo epistêmico, claims, gaps e contradições.
- `RLL_DIRECT_AND_BIBLIOGRAPHIC`: ORCID, DOI, vetores e proveniência bibliográfica.
- `METHODOLOGY`: fluxo sessão → claim → arquivo → commit → teste → evidência.
- `FEDERATED_GOVERNANCE`: custódia, watchdogs, rollback e limites de autoridade.
- `MATHEMATICAL_CONTEXT`: matemática candidata; exige prova/experimento e não prova cosmologia.
- `COMPUTATIONAL_CONTEXT`: ZIPRAF e Ω-CUBE; arquitetura computacional, não lei física.
- `OPERATIONAL_EVIDENCE`: recibos ARMv7/ELF; prova limitada ao ambiente observado.
- `OUT_OF_SCOPE_PERSONAL`: corpo privado não ingerido e não usado para claims científicos.
- `INDEX_POINTER` e `SOURCE_INVENTORY`: navegação, não evidência.

## Execução

```bash
rll-project-sources --db artifacts/orcid_rll/orcid_rll.sqlite3 ingest \
  --manifest configs/project_sources_manifest.v1.json \
  --source-root /caminho/para/fontes

rll-project-sources --db artifacts/orcid_rll/orcid_rll.sqlite3 search \
  'grafo epistêmico falsificador'
```

A ingestão verifica SHA-256 antes de criar chunks. `PRIVATE_POINTER_ONLY` nunca armazena corpo. Hash divergente produz `HASH_MISMATCH`; arquivo ausente produz `TOKEN_VAZIO_MISSING_LOCAL_FILE`.

## Fronteira científica

```text
fonte de projeto → contexto/hipótese/método
método → experimento
experimento → resultado
resultado → decisão científica
```

`MATHEMATICAL_CONTEXT`, `COMPUTATIONAL_CONTEXT` e `OUT_OF_SCOPE_PERSONAL` carregam `NOT_EVIDENCE_FOR` para claim cosmológico, lei física ou claim biológico/fisiológico.

## Estados de privacidade

- `PUBLIC_SAFE_METADATA_AND_LOCAL_BODY`: o corpo pode ser lido localmente após hash, mas não é commitado.
- `PUBLIC_SAFE_METADATA_ONLY`: somente metadados e índice entram.
- `PRIVATE_POINTER_ONLY`: nem filename público nem chunks; apenas identificador opaco, digest e fronteira.

## Próximo gate

Executar a ingestão local contra o diretório das fontes, verificar `14 documents`, inspecionar os chunks retornados e arquivar somente o receipt JSON. O banco SQLite e os textos permanecem fora do Git.
