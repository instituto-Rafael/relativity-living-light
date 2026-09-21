# Data Manifest — Formalismo de Linguagem, Entropia e Metáforas

**Status:** `planned`

## Artefatos e dados existentes

- `data/rll_latentes`
- `docs/rll_latentes`
- `artifacts/formulas`

## Documentos fonte

- `docs/FORMALIZACAO_CONHECIMENTO_MULTILINGUE.md`
- `docs/FORMALISMO_RAFAELIA_T7_E_COERENCIA.md`
- `docs/RLL_STATISTICAL_FINANCIAL_METRICS.md`
- `newadd/05_TAO_LINGUAGEM_COMPRESSAO.md`
- `newadd/02_Formulacoes_Latentes_RAFAELIA_RLL.md`

## Entradas ainda pendentes

- Dataset canônico com versão, licença, data de acesso e checksum.
- Critério de exclusão/inclusão por observável.
- Tabela de métricas com baseline comparável.
- Registro de figuras geradas em `figures/`.

## Regra de não duplicação

Este manifesto referencia materiais existentes. Cópias locais só devem ser criadas quando houver necessidade editorial ou reprodutível, com checksum, data, origem, destino e justificativa.


## Δ Dataset/experimento proposto — MU-RLL-LANG-MANIFOLD-SEED-20260920

### Corpus paralelo de reconstrução

Proposta: selecionar três traduções/línguas de um corpus bíblico com alinhamento verificável de passagens em Gênesis, João e Mateus.

Estado atual:
- idiomas exatos: `TOKEN_VAZIO`;
- edições/versões: `TOKEN_VAZIO`;
- licença/direitos de redistribuição: `TOKEN_VAZIO`;
- checksum dos bytes-fonte: `TOKEN_VAZIO`;
- fonte canônica de download: `TOKEN_VAZIO`.

Nenhum corpus é considerado ingerido até esses campos serem preenchidos. O teste deve contabilizar integralmente dicionários, índices, alinhamentos, metadados, decoder e proveniência como custo da representação.


## Fechamento parcial do TOKEN_VAZIO — corpus trilíngue

Fontes selecionadas para o gate SCD1:
- ENG: BibleAquifer/WorldEnglishBible @ `bcb8b3edfb302863c241e3d1d2062cf51042d694` — domínio público.
- SPA: BibleAquifer/ReinaValera1909 @ `84a071324be17c7c66db17dd204d7804e66d728b` — domínio público.
- POR: blivre/BibliaLivre @ `a315a15e9f4d01883b62206fe441d57762f126b3` — usar conservadoramente **CC BY 3.0 Brasil**, conforme `LICENCA.md` do repositório-fonte.

Observação de licença: eBible apresenta a Bíblia Livre como CC BY 4.0, enquanto o repositório-fonte mantém CC BY 3.0 Brasil. A divergência permanece registrada; não foi reconciliada por inferência.

Os SHA-256 UTF-8 dos nove arquivos usados estão em `results/SCD1_20260920.json`, junto aos blob SHAs e commits de origem.
