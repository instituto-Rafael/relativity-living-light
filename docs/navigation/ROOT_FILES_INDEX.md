# Índice Navegável dos Arquivos Soltos da Raiz

**Gerado para:** refatoração sem quebra de caminhos  
**Estado:** `NAVIGATION_LAYER_V1`  
**Regra:** este índice **não move nem apaga** arquivos; ele atribui rota de navegação e decisão de migração.

## Como usar

- `KEEP_ROOT`: arquivo que faz sentido permanecer na raiz.
- `INDEX_FIRST`: documento legível pela navegação; migração física só após checagem de backlinks.
- `ROUTE_CODE`: fonte executável; navegar por código/ferramentas, não como documento de entrada.
- `ROUTE_REGISTRY`: configuração/registro; navegar por governança/dados.
- `LEGACY_REVIEW`: preservar, classificar e apontar sucessor canônico antes de mover.
- `LEGACY_STUB`: corpo já migrado; caminho raiz existe apenas para compatibilidade/backlink.
- `ARTIFACT_REVIEW`: binário/bundle; exigir provenance/hash/retention antes de publicação.
- `MANUAL_REVIEW`: sem decisão automática.

**Total de arquivos na raiz nesta varredura:** 61  
**Total de diretórios na raiz:** 47

## Arquivos

| Arquivo | Papel de navegação | Decisão V1 |
|---|---|---|
| [`.gitignore`](../../.gitignore) | `BUILD_TOOLING` | `KEEP_ROOT` |
| [`ARCHITECTURE_CLAIM_GATED.md`](../../ARCHITECTURE_CLAIM_GATED.md) | `ENTRY_GOVERNANCE` | `KEEP_ROOT` |
| [`ARCHITECTURE.md`](../../ARCHITECTURE.md) | `ENTRY_GOVERNANCE` | `KEEP_ROOT` |
| [`ATLAS_CANONICO.md`](../../ATLAS_CANONICO.md) | `ENTRY_ATLAS` | `KEEP_ROOT` |
| [`build.gradle`](../../build.gradle) | `BUILD_TOOLING` | `KEEP_ROOT` |
| [`CAMINHOS_VALIDACAO_NOVOS.yml`](../../CAMINHOS_VALIDACAO_NOVOS.yml) | `REGISTRY_CONFIG` | `ROUTE_REGISTRY` |
| [`Códex1.md`](../../C%C3%B3dex1.md) | `LEGACY_STUB` | `MOVED → docs/legacy/root/prompts/Códex1.md` |
| [`Codex2.md`](../../Codex2.md) | `LEGACY_STUB` | `MOVED → docs/legacy/root/prompts/Codex2.md` |
| [`COMPREHENSIVE_REPOSITORY_ANALYSIS.md`](../../COMPREHENSIVE_REPOSITORY_ANALYSIS.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`CONSOLIDATION.md`](../../CONSOLIDATION.md) | `ENTRY_GOVERNANCE` | `KEEP_ROOT` |
| [`darkmatter.md`](../../darkmatter.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`docs_toroidal_knowledge.md`](../../docs_toroidal_knowledge.md) | `LEGACY_STUB` | `MOVED → docs/legacy/root/concepts/docs_toroidal_knowledge.md` |
| [`EXECUTIVE_SUMMARY.md`](../../EXECUTIVE_SUMMARY.md) | `ENTRY_GOVERNANCE` | `KEEP_ROOT` |
| [`FALSIFIABILITY_PROTOCOL.md`](../../FALSIFIABILITY_PROTOCOL.md) | `ENTRY_GOVERNANCE` | `KEEP_ROOT` |
| [`Geologia.md`](../../Geologia.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`GOVERNANCE_REORG_DRAFT.md`](../../GOVERNANCE_REORG_DRAFT.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`gradle.properties`](../../gradle.properties) | `BUILD_TOOLING` | `KEEP_ROOT` |
| [`gradlew`](../../gradlew) | `BUILD_TOOLING` | `KEEP_ROOT` |
| [`gradlew.bat`](../../gradlew.bat) | `BUILD_TOOLING` | `KEEP_ROOT` |
| [`LICENSE.md`](../../LICENSE.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`main.tex`](../../main.tex) | `OTHER_ROOT` | `MANUAL_REVIEW` |
| [`MANIFESTO_MIGRATION_FILES.md`](../../MANIFESTO_MIGRATION_FILES.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`Matemática.md`](../../Matem%C3%A1tica.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`MathRaf.md`](../../MathRaf.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`NEXT_RLL_VALIDATION_STEP.md`](../../NEXT_RLL_VALIDATION_STEP.md) | `ENTRY_GOVERNANCE` | `KEEP_ROOT` |
| [`Numprimod.md`](../../Numprimod.md) | `LEGACY_REVIEW` | `LEGACY_REVIEW` |
| [`PRODUCTO.json`](../../PRODUCTO.json) | `REGISTRY_CONFIG` | `ROUTE_REGISTRY` |
| [`Provaw.md`](../../Provaw.md) | `LEGACY_STUB` | `MOVED → docs/legacy/root/experiments/Provaw.md` |
| [`pyproject.toml`](../../pyproject.toml) | `BUILD_TOOLING` | `KEEP_ROOT` |
| [`pytest.ini`](../../pytest.ini) | `BUILD_TOOLING` | `KEEP_ROOT` |
| [`Rafael te.md`](../../Rafael%20te.md) | `LEGACY_REVIEW` | `LEGACY_REVIEW` |
| [`RAFAEL_kernel.sh`](../../RAFAEL_kernel.sh) | `EXECUTABLE_SOURCE` | `ROUTE_CODE` |
| [`Rafafinsnce.md`](../../Rafafinsnce.md) | `LEGACY_REVIEW` | `LEGACY_REVIEW` |
| [`README_MASTER.md`](../../README_MASTER.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`README.md`](../../README.md) | `ENTRY_GOVERNANCE` | `KEEP_ROOT` |
| [`REFORM_LOG.md`](../../REFORM_LOG.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`REPRODUCIBILITY_MATRIX.md`](../../REPRODUCIBILITY_MATRIX.md) | `ENTRY_GOVERNANCE` | `KEEP_ROOT` |
| [`requirements-rx.txt`](../../requirements-rx.txt) | `BUILD_TOOLING` | `KEEP_ROOT` |
| [`requirements.txt`](../../requirements.txt) | `BUILD_TOOLING` | `KEEP_ROOT` |
| [`RESUMO_REFORMA.md`](../../RESUMO_REFORMA.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`rll_equation_registry.yml`](../../rll_equation_registry.yml) | `REGISTRY_CONFIG` | `ROUTE_REGISTRY` |
| [`RLL_FALSEABILITY_MATRIX.md`](../../RLL_FALSEABILITY_MATRIX.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`rll_inovacao_tecnologica_watch.json`](../../rll_inovacao_tecnologica_watch.json) | `REGISTRY_CONFIG` | `ROUTE_REGISTRY` |
| [`rll_inovacao_tecnologica_watch.yml`](../../rll_inovacao_tecnologica_watch.yml) | `REGISTRY_CONFIG` | `ROUTE_REGISTRY` |
| [`RLL_JSON_EVOLUTION_WATCHER.yml`](../../RLL_JSON_EVOLUTION_WATCHER.yml) | `REGISTRY_CONFIG` | `ROUTE_REGISTRY` |
| [`RLL_MATERIALIZACAO_CORE.md`](../../RLL_MATERIALIZACAO_CORE.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`RLL_REAL_VALIDATION_PROMPT.md`](../../RLL_REAL_VALIDATION_PROMPT.md) | `ROUTING_STUB` | `MOVED → docs/validation/prompts/RLL_REAL_VALIDATION_PROMPT.md` |
| [`RLL_REAL_VALIDATION_REPORT_TARGET.md`](../../RLL_REAL_VALIDATION_REPORT_TARGET.md) | `ROUTING_STUB` | `MOVED → docs/validation/targets/RLL_REAL_VALIDATION_REPORT_TARGET.md` |
| [`rll_reproducivel.zip`](../../rll_reproducivel.zip) | `BINARY_ARTIFACT` | `ARTIFACT_REVIEW` |
| [`rll_vs_lcdm.py`](../../rll_vs_lcdm.py) | `EXECUTABLE_SOURCE` | `ROUTE_CODE` |
| [`RLL_WANDERING_BLACK_HOLE_TEST.md`](../../RLL_WANDERING_BLACK_HOLE_TEST.md) | `ROUTING_STUB` | `MOVED → docs/validation/cases/RLL_WANDERING_BLACK_HOLE_TEST.md` |
| [`Rsfael`](../../Rsfael) | `LEGACY_STUB / TEXT_IDENTIFIED` | `MOVED → docs/legacy/root/raw/Rsfael.txt` |
| [`runtime-lock.json`](../../runtime-lock.json) | `REGISTRY_CONFIG` | `ROUTE_REGISTRY` |
| [`SCIENTIFIC_CLAIMS.md`](../../SCIENTIFIC_CLAIMS.md) | `ENTRY_GOVERNANCE` | `KEEP_ROOT` |
| [`SCIENTIFIC_CORE_SCOPE.md`](../../SCIENTIFIC_CORE_SCOPE.md) | `ENTRY_GOVERNANCE` | `KEEP_ROOT` |
| [`SECURITY_SUMMARY.md`](../../SECURITY_SUMMARY.md) | `ENTRY_GOVERNANCE` | `KEEP_ROOT` |
| [`settings.gradle`](../../settings.gradle) | `BUILD_TOOLING` | `KEEP_ROOT` |
| [`temp.md`](../../temp.md) | `LEGACY_REVIEW` | `LEGACY_REVIEW` |
| [`TEXTO_DESCRITIVO_ANALITICO_TECNICO.md`](../../TEXTO_DESCRITIVO_ANALITICO_TECNICO.md) | `DOCUMENT` | `INDEX_FIRST` |
| [`Toadd01.md`](../../Toadd01.md) | `LEGACY_STUB` | `MOVED → docs/legacy/root/prototypes/Toadd01.md` |
| [`VALIDATION_STATUS.md`](../../VALIDATION_STATUS.md) | `ENTRY_GOVERNANCE` | `KEEP_ROOT` |

## Diretórios — mapa rápido

| Diretório | Rota sugerida |
|---|---|
| [`.githooks/`](../../.githooks/) | automação e governança Git |
| [`.github/`](../../.github/) | automação e governança Git |
| [`ANALISE_COMPLETA/`](../../ANALISE_COMPLETA/) | consultar NAVIGATION_HUB antes de uso |
| [`app/`](../../app/) | consultar NAVIGATION_HUB antes de uso |
| [`apps/`](../../apps/) | consultar NAVIGATION_HUB antes de uso |
| [`artifacts/`](../../artifacts/) | consultar NAVIGATION_HUB antes de uso |
| [`auditoria/`](../../auditoria/) | evidência/proveniência/auditoria |
| [`book/`](../../book/) | publicação/leitura longa |
| [`configs/`](../../configs/) | consultar NAVIGATION_HUB antes de uso |
| [`core/`](../../core/) | código núcleo |
| [`Dados_artefatos/`](../../Dados_artefatos/) | consultar NAVIGATION_HUB antes de uso |
| [`data/`](../../data/) | dados, contratos e governança executável |
| [`data2/`](../../data2/) | consultar NAVIGATION_HUB antes de uso |
| [`docs/`](../../docs/) | documentação e navegação |
| [`evidence/`](../../evidence/) | evidência/proveniência/auditoria |
| [`examples/`](../../examples/) | consultar NAVIGATION_HUB antes de uso |
| [`figs/`](../../figs/) | consultar NAVIGATION_HUB antes de uso |
| [`fixtures/`](../../fixtures/) | consultar NAVIGATION_HUB antes de uso |
| [`governance/`](../../governance/) | consultar NAVIGATION_HUB antes de uso |
| [`gradle/`](../../gradle/) | consultar NAVIGATION_HUB antes de uso |
| [`internal/`](../../internal/) | consultar NAVIGATION_HUB antes de uso |
| [`knowledge_ecosystem/`](../../knowledge_ecosystem/) | consultar NAVIGATION_HUB antes de uso |
| [`native/`](../../native/) | código núcleo |
| [`newadd/`](../../newadd/) | ingestão/legacy — não assumir canonicidade |
| [`news/`](../../news/) | ingestão/legacy — não assumir canonicidade |
| [`PapersPub/`](../../PapersPub/) | publicação/leitura longa |
| [`products/`](../../products/) | consultar NAVIGATION_HUB antes de uso |
| [`protocols/`](../../protocols/) | consultar NAVIGATION_HUB antes de uso |
| [`provenance/`](../../provenance/) | evidência/proveniência/auditoria |
| [`RAF_VERBEYES/`](../../RAF_VERBEYES/) | consultar NAVIGATION_HUB antes de uso |
| [`RAFAELIA_COSMO_STRUCTURE_D/`](../../RAFAELIA_COSMO_STRUCTURE_D/) | consultar NAVIGATION_HUB antes de uso |
| [`receipts/`](../../receipts/) | evidência/proveniência/auditoria |
| [`requirements/`](../../requirements/) | consultar NAVIGATION_HUB antes de uso |
| [`results/`](../../results/) | resultados materializados |
| [`rll_core/`](../../rll_core/) | código núcleo |
| [`RMR/`](../../RMR/) | consultar NAVIGATION_HUB antes de uso |
| [`rx/`](../../rx/) | consultar NAVIGATION_HUB antes de uso |
| [`schemas/`](../../schemas/) | consultar NAVIGATION_HUB antes de uso |
| [`scripts/`](../../scripts/) | ferramentas e execução |
| [`src/`](../../src/) | código núcleo |
| [`studio/`](../../studio/) | consultar NAVIGATION_HUB antes de uso |
| [`tests/`](../../tests/) | testes e validação |
| [`to_Add/`](../../to_Add/) | ingestão/legacy — não assumir canonicidade |
| [`tools/`](../../tools/) | ferramentas e execução |
| [`validacao_real/`](../../validacao_real/) | testes e validação |
| [`validation/`](../../validation/) | testes e validação |
| [`workflows/`](../../workflows/) | consultar NAVIGATION_HUB antes de uso |

## Política de migração

1. Primeiro criar índice/backlinks.
2. Depois confirmar canonicidade e LGPD/data-class.
3. Só então mover em ondas pequenas.
4. Para documentos legados, manter stub no caminho antigo apontando ao novo destino quando a compatibilidade de links importar.
5. Binários e bundles não são movidos automaticamente: exigem hash, origem, finalidade e retenção.

## TOKEN_VAZIO

- `TOKEN_VAZIO_BACKLINK_GRAPH_COMPLETE`: ainda não foi provado que todo arquivo raiz pode ser movido sem quebrar links.
- `TOKEN_VAZIO_LEGAL_COMPLIANCE_REVIEW`: engenharia de privacidade não equivale a parecer jurídico.
- `TOKEN_VAZIO_HUMAN_USABILITY`: navegação humana física ainda precisa de smoke test.


## Wave 2A — migração física concluída

Manifesto: [`RLL_ROOT_PHYSICAL_REFACTOR_WAVE2A_V1.json`](../../data/governance/RLL_ROOT_PHYSICAL_REFACTOR_WAVE2A_V1.json).

Seis corpos legacy saíram da raiz e foram preservados em `docs/legacy/root/`; os seis caminhos antigos são stubs de compatibilidade. Remoção futura dos stubs depende de `TOKEN_VAZIO_STUB_REMOVAL_SAFE`.


## Wave 2B — INDEX_FIRST → typed validation routes

Três documentos ativos de validação foram movidos para [`docs/validation/`](../validation/README.md), preservando stubs na raiz. Manifesto: [`RLL_ROOT_PHYSICAL_REFACTOR_WAVE2B_V1.json`](../../data/governance/RLL_ROOT_PHYSICAL_REFACTOR_WAVE2B_V1.json).