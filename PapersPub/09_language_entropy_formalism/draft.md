# Formalismo de Linguagem, Entropia e Metáforas

**Status:** `planned`  
**Escopo:** Transdisciplinary language/entropy material kept as conceptual unless quantified by reproducible metrics.

## Objetivo

Transformar materiais existentes em uma trilha de paper rastreável, sem mover documentos antes de registrar a migração e sem duplicar conteúdo sem justificativa.

## Claims permitidas nesta fase

- Declarações de escopo, hipótese e plano de validação.
- Síntese de materiais existentes com citação de caminho e status.
- Resultados quantitativos somente quando vierem acompanhados de origem, comando, dataset, métrica e limitação.

## Claims proibidas nesta fase

- Declarar superioridade sobre baselines sem métricas reais comparáveis.
- Converter metáforas, intuições ou analogias em evidência observacional.
- Misturar cosmologia, geofísica e heliosfera como se compartilhassem a mesma validação.

## Materiais existentes a referenciar

- `docs/FORMALIZACAO_CONHECIMENTO_MULTILINGUE.md`
- `docs/FORMALISMO_RAFAELIA_T7_E_COERENCIA.md`
- `docs/RLL_STATISTICAL_FINANCIAL_METRICS.md`
- `newadd/05_TAO_LINGUAGEM_COMPRESSAO.md`
- `newadd/02_Formulacoes_Latentes_RAFAELIA_RLL.md`

## Estrutura planejada do manuscrito

1. Resumo e status científico.
2. Contexto e baseline comparável.
3. Dados e critérios de inclusão/exclusão.
4. Métodos e métricas.
5. Resultados, incluindo resultados negativos.
6. Discussão, limitações e falsificação.
7. Reprodutibilidade e materiais suplementares.

## Registro de migração

Nenhum documento legado foi movido na criação desta pasta. Qualquer migração futura deve registrar origem, destino, checksum quando aplicável, motivo e plano de rollback.


---

## Δ 2026-09-20 — Manifold multidimensional, semente reconstrutível e entropia contextual

**μID:** `MU-RLL-LANG-MANIFOLD-SEED-20260920`  
**Estado:** `HYPOTHESIS / PLANNED / claim_allowed=false`

### Tese operacional

Organização do conhecimento é tratada como um **manifold/grafo multidimensional de coerência técnica e rastreabilidade**, no qual cada unidade deve preservar, quando disponível, tema, fonte, tempo, escala, evidência, relações, estado e rota de reconstrução.

A hipótese não é que uma semente contenha informação ilimitada. A hipótese é que uma **semente reconstrutível** pode referenciar uma estrutura maior quando preserva informação suficiente para o decoder recuperar as relações relevantes:

[
S = \{schema\_version, dictionary/ref, invariants, ordering, provenance, decoder/test\}
]

[
\hat K = R(S,C,D)
]

onde (K) é o conhecimento-fonte, (S) é a semente, (C) é contexto compartilhado e (D) é o decoder. Para reconstrução textual lossless, a condição forte é (hash(\hat K)=hash(K)). Para reconstrução semântica, a métrica deve ser declarada e não pode ser confundida com igualdade byte a byte.

### Entropia contextual

Definir provisoriamente:

[
H_{ctx}=H(\text{redundância},\text{contradição},\text{incerteza},\text{fragmentação}\mid C)
]

O objetivo de reorganização é reduzir (H_{ctx}) e o comprimento descritivo/operacional **relativos a um contexto, codec e tarefa declarados**, preservando proveniência e reconstruibilidade.

Isso **não** implica entropia termodinâmica negativa, violação de Shannon ou criação de informação. O termo “sintropia” permanece, nesta trilha, como rótulo filosófico/organizacional até existir definição mensurável independente.

### Transmissor ↔ receptor / observador ↔ observado

A compressibilidade depende do contexto compartilhado:

[
X \xrightarrow{encode(C)} S \xrightarrow{channel} S' \xrightarrow{decode(C)} \hat X
]

Quanto mais estrutura já compartilhada por transmissor e receptor, menor pode ser a descrição incremental; o custo do dicionário, índices, alinhamentos e proveniência deve ser contabilizado. Não se assume compressibilidade universal independente de língua, observador ou decoder.

### Caso de teste multilíngue proposto

Usar um corpus paralelo de **três línguas** contendo passagens alinháveis do Antigo e do Novo Testamento, com estratos de **Gênesis, João e Mateus**, apenas como banco de ensaio de estrutura canônica e reconstrução cruzada.

- línguas/edições exatas: `TOKEN_VAZIO` até seleção e verificação de licença;
- o corpus religioso é **caso de teste**, não prova da hipótese;
- alinhamento capítulo/versículo, léxico e relações semânticas entram como side-information contabilizada.

**H1:** representação por semente + dicionário/alinhamento + referências reduz o custo total de descrição ou de recuperação em relação a armazenar/tratar cada versão como estrutura independente, mantendo a qualidade de reconstrução definida.

**H0:** após contabilizar dicionário, alinhamento, metadados e proveniência, não há ganho líquido, ou a reconstrução degrada além do limiar pré-definido.

### Métricas mínimas

1. bytes/tokens totais antes e depois, incluindo side-information;
2. taxa de compressão líquida;
3. hash exato quando o objetivo for reconstrução textual lossless;
4. métrica semântica declarada quando o objetivo não for byte-exato;
5. cobertura de proveniência e relações;
6. latência, memória e custo de reconstrução;
7. resultado negativo e diferença por língua/edição.

### Falsificadores

A hipótese deve ser reduzida ou rejeitada se:
- o ganho desaparecer após contabilizar o custo do dicionário/contexto;
- a semente não permitir reconstrução no critério declarado;
- o ganho depender apenas de duplicação trivial já capturada por compressores baseline;
- a organização ocultar contradições ou apagar proveniência;
- resultados não se reproduzirem em corpus não religioso e estruturalmente diferente.

**Boundary:** `SOURCE ≠ ARTEFATO ≠ EXECUÇÃO ≠ EVIDÊNCIA ≠ CLAIM`.


## Resultado SCD1 — 2026-09-20

O primeiro ensaio executado usa 3.483 referências comuns em Gênesis, Mateus e João, totalizando 10.449 registros normalizados em inglês, espanhol e português.

| Representação | bytes UTF-8 |
|---|---:|
| registros JSON verbosos | 1.642.359 |
| SCD1 — refs compartilhadas + vetores linguísticos | 1.273.254 |
| texto puro concatenado | 1.213.948 |

Resultado: SCD1 reduziu **369.105 bytes (22,474%)** frente ao baseline JSON verboso e reconstruiu exatamente os registros normalizados (`SHA-256 960d1c66…e82c8f`). Porém SCD1 ficou **59.306 bytes (4,885%) maior** que texto puro.

**Interpretação permitida:** há ganho de organização/deduplicação estrutural de metadados para o modelo normalizado.  
**Interpretação proibida:** chamar este resultado de compressor universal ou de compressão semântica superior a compressores gerais.

Próximo gate: comparar, sobre os mesmos bytes e com custos de schema/dicionário contabilizados, SCD1 versus gzip/zstd/brotli e um codec estrutural; repetir em corpus paralelo não religioso.
